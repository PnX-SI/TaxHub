import os
import logging
from pkg_resources import iter_entry_points
from pathlib import Path
from importlib import import_module
from flask import Flask, current_app, send_from_directory, request, g
from flask_cors import CORS
from flask_migrate import Migrate
from flask_login import current_user
from werkzeug.middleware.proxy_fix import ProxyFix
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.orm.exc import NoResultFound


from apptax.database import db  # must be before pynpnusershub import !!
from pypnusershub.login_manager import login_manager

from apptax.admin.admin import taxhub_admin, taxhub_admin_addview

migrate = Migrate()


@migrate.configure
def configure_alembic(alembic_config):
    """
    This function add to the 'version_locations' parameter of the alembic config the
    'migrations' entry point value of the 'alembic' group for all packages having such entry point.
    Thus, alembic will find migrations provided by all installed packages.
    """
    # Ignore version_locations provided in configuration as TaxHub migrations are also
    # detected by iter_entry_points so we current_app.config["ID_APP"]avoid adding twice
    # version_locations = alembic_config.get_main_option('version_locations', default='').split()
    version_locations = []
    if "ALEMBIC_VERSION_LOCATIONS" in current_app.config:
        version_locations.extend(current_app.config["ALEMBIC_VERSION_LOCATIONS"].split())
    for entry_point in iter_entry_points("alembic", "migrations"):
        _, migrations = str(entry_point).split("=", 1)
        version_locations += [migrations.strip()]
    alembic_config.set_main_option("version_locations", " ".join(version_locations))
    return alembic_config


def create_app():
    app = Flask(__name__, static_folder=os.environ.get("TAXHUB_STATIC_FOLDER", "static"))

    app.config.from_pyfile(os.environ.get("TAXHUB_SETTINGS", "config.py"))
    app.config.from_prefixed_env(prefix="TAXHUB")

    media_path = Path(app.config["MEDIA_FOLDER"]).absolute()

    # Enable serving of media files
    app.add_url_rule(
        "/{media_path}/<path:filename>".format(media_path="medias"),
        view_func=lambda filename: send_from_directory(media_path, filename),
        endpoint="media",
    )

    if "SCRIPT_NAME" not in os.environ and "APPLICATION_ROOT" in app.config:
        os.environ["SCRIPT_NAME"] = app.config["APPLICATION_ROOT"].rstrip("/")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_host=1)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db, directory=Path(__file__).absolute().parent / "migrations")
    CORS(app, supports_credentials=True)

    app.config["DB"] = db

    app.config["USE_S3"] = app.config.get("USE_S3", False)
    app.config["S3_BUCKET_NAME"] = app.config.get("S3_BUCKET_NAME", None)
    app.config["S3_KEY"] = app.config.get("S3_KEY", None)
    app.config["S3_SECRET"] = app.config.get("S3_SECRET", None)
    app.config["S3_ENDPOINT"] = app.config.get("S3_ENDPOINT", None)
    app.config["S3_PUBLIC_URL"] = app.config.get("S3_PUBLIC_URL", None)
    app.config["S3_FOLDER"] = app.config.get("S3_FOLDER", None)
    app.config["S3_REGION_NAME"] = app.config.get("S3_REGION_NAME", None)

    if "CODE_APPLICATION" not in app.config:
        app.config["CODE_APPLICATION"] = "TH"

    @app.before_request
    def load_current_user():
        g.current_user = current_user if current_user.is_authenticated else None

    with app.app_context():

        @app.route("/favicon.ico")
        def favicon():
            return send_from_directory(
                os.path.join(app.root_path, "static"),
                "favicon.ico",
                mimetype="image/vnd.microsoft.icon",
            )

        from pypnusershub import routes

        app.register_blueprint(routes.routes, url_prefix="/api/auth")

        # Flask admin
        taxhub_admin.init_app(app)
        taxhub_admin_addview(app, taxhub_admin)

        # API
        from apptax import taxhub_routes

        for blueprint_path, url_prefix in taxhub_routes:
            module_name, blueprint_name = blueprint_path.split(":")
            blueprint = getattr(import_module(module_name), blueprint_name)
            app.register_blueprint(blueprint, url_prefix=url_prefix)

    return app

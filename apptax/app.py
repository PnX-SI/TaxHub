import os
import logging
from backports.entry_points_selectable import entry_points
from pathlib import Path
from importlib import import_module
from flask import Flask, current_app, send_from_directory, request, g
from flask_cors import CORS
from flask_migrate import Migrate
from flask_login import current_user
from flask_babel import Babel
from werkzeug.middleware.proxy_fix import ProxyFix
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.orm.exc import NoResultFound


from apptax.database import db  # must be before pynpnusershub import !!
from pypnusershub.auth import auth_manager

from apptax.admin.admin import taxhub_admin, taxhub_admin_addview
from apptax.utils.config.utilstoml import load_and_validate_toml
from apptax.utils.config.config_schema import TaxhubSchemaConf

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
    for entry_point in entry_points(group="alembic", name="migrations"):
        version_locations += [entry_point.value]
    alembic_config.set_main_option("version_locations", " ".join(version_locations))
    return alembic_config


def get_locale():
    # if a user is logged in, use the locale from the user settings
    user = getattr(g, "user", None)
    if user is not None:
        return user.locale
    # otherwise try to guess the language from the user accept
    # header the browser transmits.  We support de/fr/en in this
    # example.  The best match wins.
    return request.accept_languages.best_match(["de", "fr", "en"])


def create_app():
    app = Flask(__name__, static_folder=os.environ.get("TAXHUB_STATIC_FOLDER", "static"))

    DEFAULT_CONFIG_FILE = Path(__file__).absolute().parent.parent / "config/taxhub_config.toml"
    CONFIG_FILE = os.environ.get("TAXHUB_CONFIG_FILE", DEFAULT_CONFIG_FILE)
    config = load_and_validate_toml(CONFIG_FILE, TaxhubSchemaConf)
    app.config.update(config)
    app.config.from_prefixed_env(prefix="TAXHUB")

    media_path = Path(app.config["MEDIA_FOLDER"], "taxhub").absolute()

    # Enable serving of media files
    app.add_url_rule(
        f"/{media_path}/<path:filename>",
        view_func=lambda filename: send_from_directory(media_path, filename),
        endpoint="media_taxhub",
    )

    if "SCRIPT_NAME" not in os.environ and "APPLICATION_ROOT" in app.config:
        os.environ["SCRIPT_NAME"] = app.config["APPLICATION_ROOT"].rstrip("/")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_host=1)

    db.init_app(app)
    migrate.init_app(app, db, directory=Path(__file__).absolute().parent / "migrations")
    CORS(app, supports_credentials=True)

    app.config["DB"] = db

    providers_config = [
        {
            "module": "pypnusershub.auth.providers.default.LocalProvider",
            "id_provider": "local_provider",
        },
    ]
    auth_manager.init_app(app, providers_declaration=providers_config)

    # babel
    babel = Babel(app, locale_selector=get_locale)

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

        # Flask admin
        taxhub_admin.init_app(app)
        taxhub_admin_addview(app, taxhub_admin)
        from apptax.admin.admin import adresses

        app.register_blueprint(adresses, url_prefix="/")

        # API
        from apptax import taxhub_api_routes

        base_api_prefix = app.config.get("API_PREFIX")

        for blueprint_path, url_prefix in taxhub_api_routes:
            module_name, blueprint_name = blueprint_path.split(":")
            blueprint = getattr(import_module(module_name), blueprint_name)
            app.register_blueprint(blueprint, url_prefix=base_api_prefix + url_prefix)

    return app

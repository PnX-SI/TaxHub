import os
import logging
from pkg_resources import iter_entry_points

from flask import Flask, current_app
from flask_cors import CORS
from flask_migrate import Migrate
from werkzeug.middleware.proxy_fix import ProxyFix
from sqlalchemy.exc import ProgrammingError

from pypnusershub.db.models import Application
from apptax.database import db


migrate = Migrate()


@migrate.configure
def configure_alembic(alembic_config):
    """
    This function add to the 'version_locations' parameter of the alembic config the
    'migrations' entry point value of the 'alembic' group for all packages having such entry point.
    Thus, alembic will find migrations provided by all installed packages.
    """
    # Ignore version_locations provided in configuration as TaxHub migrations are also
    # detected by iter_entry_points so we avoid adding twice
    #version_locations = alembic_config.get_main_option('version_locations', default='').split()
    version_locations = []
    if 'ALEMBIC_VERSION_LOCATIONS' in current_app.config:
        version_locations.extend(config['ALEMBIC_VERSION_LOCATIONS'].split())
    for entry_point in iter_entry_points('alembic', 'migrations'):
        _, migrations = str(entry_point).split('=', 1)
        version_locations += [ migrations.strip() ]
    alembic_config.set_main_option('version_locations', ' '.join(version_locations))
    return alembic_config


def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')

    app.config.from_pyfile(os.environ.get("TAXHUB_SETTINGS", "config.py"))

    # Patch suppression de static du paramètre UPLOAD_FOLDER
    # TODO changer le système de chargement de la conf pour avoir des valeurs par défaut
    if 'UPLOAD_FOLDER' in app.config:
        if app.config['UPLOAD_FOLDER'].startswith("static/"):
            app.config['UPLOAD_FOLDER'] = app.config['UPLOAD_FOLDER'][7:]


    if 'SCRIPT_NAME' not in os.environ and 'APPLICATION_ROOT' in app.config:
        os.environ['SCRIPT_NAME'] = app.config['APPLICATION_ROOT'].rstrip('/')
    app.wsgi_app = ProxyFix(app.wsgi_app, x_host=1)

    db.init_app(app)
    migrate.init_app(app, db, directory='apptax/migrations')
    CORS(app, supports_credentials=True)

    app.config["DB"] = db

    app.config["S3_BUCKET_NAME"] = app.config.get("S3_BUCKET_NAME", None)
    app.config["S3_KEY"] = app.config.get("S3_KEY", None)
    app.config["S3_SECRET"] = app.config.get("S3_SECRET", None)
    app.config["S3_ENDPOINT"] = app.config.get("S3_ENDPOINT", None)
    app.config["S3_PUBLIC_URL"] = app.config.get("S3_PUBLIC_URL", None)
    app.config["S3_FOLDER"] = app.config.get("S3_FOLDER", None)
    app.config["S3_REGION_NAME"] = app.config.get("S3_REGION_NAME", None)

    @app.teardown_request
    def _manage_transaction(exception):
        if exception:
            db.session.rollback()
        else:
            db.session.commit()
        db.session.remove()

    with app.app_context():
        try:
            th_app = Application.query.filter_by(code_application='TH').one()
        except ProgrammingError:
            logging.warning("Warning: unable to find TaxHub application, database not yet initialized?")
        else:
            app.config["ID_APP"] = th_app.id_application

        from pypnusershub import routes

        app.register_blueprint(routes.routes, url_prefix="/api/auth")

        from apptax.index import routes

        app.register_blueprint(routes, url_prefix="/")

        from apptax.taxonomie.routesbibnoms import adresses

        app.register_blueprint(adresses, url_prefix="/api/bibnoms")

        from apptax.taxonomie.routestaxref import adresses

        app.register_blueprint(adresses, url_prefix="/api/taxref")

        from apptax.taxonomie.routesbibattributs import adresses

        app.register_blueprint(adresses, url_prefix="/api/bibattributs")

        from apptax.taxonomie.routesbiblistes import adresses

        app.register_blueprint(adresses, url_prefix="/api/biblistes")

        from apptax.taxonomie.routestmedias import adresses

        app.register_blueprint(adresses, url_prefix="/api/tmedias")

        from apptax.taxonomie.routesbibtypesmedia import adresses

        app.register_blueprint(adresses, url_prefix="/api/bibtypesmedia")

        from apptax.utils.routesconfig import adresses

        app.register_blueprint(adresses, url_prefix="/api/config")

        from apptax.taxonomie.routesbdcstatuts import adresses

        app.register_blueprint(adresses, url_prefix="/api/bdc_statuts")

    return app

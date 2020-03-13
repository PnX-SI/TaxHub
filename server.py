# coding: utf8
import toml
import sys
import os

from flask import Flask
from flask_cors import CORS
from toml import TomlDecodeError

from apptax.database import db

db = db

app_globals = {}


def load_toml(file_path):
    """
        Chargement des fichier de type toml
    """
    try:
        return toml.load(file_path)
    except (TypeError, TomlDecodeError) as exp:
        sys.exit(
            "Unable to parse config file '{}' : {}".format(
                    file_path, exp
                )
            )


def loadConfig():
    """
        Chargement de la configuration
            si prod = fichiers
                - /etc/taxhub.conf
                - /etc/geonature-db.conf
            si dev = fichier config/taxhub.conf

            Les fichiers sont chargés
                les uns après les autres et se surchagent
    """
    config = {}
    config_files = [
        "config/taxhub.conf.default",
        "/etc/geonature/taxhub.conf",
        "/etc/geonature/geonature-db.conf",
        "config/taxhub.conf"
    ]
    for f in config_files:
        if os.path.isfile(f):
            config.update(load_toml(f))

    # Generation SQLALCHEMY_DATABASE_URI
    if 'SQLALCHEMY_DATABASE_URI' not in config:
        db_uri = "postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}".format(  # noqa E501
            **config
        )
        config['SQLALCHEMY_DATABASE_URI'] = db_uri

    # Generation base_dir et static
    config['BASE_DIR'] = os.path.abspath(os.path.dirname(__file__))
    config['UPLOAD_FOLDER'] = 'static/medias'

    return config


def init_app():
    if app_globals.get('app', False):
        app = app_globals['app']
    else:
        app = Flask(__name__)

    with app.app_context():

        # Chargement de la config
        CONF = loadConfig()
        app.config.update(CONF)
        db.init_app(app)
        db.app = app
        app.config['DB'] = db

        @app.teardown_request
        def _manage_transaction(exception):
            if exception:
                db.session.rollback()
            else:
                db.session.commit()
            db.session.remove()

        from pypnusershub import routes
        app.register_blueprint(routes.routes, url_prefix='/api/auth')

        from apptax.index import routes
        app.register_blueprint(routes, url_prefix='/')

        from apptax.taxonomie.routesbibnoms import adresses
        app.register_blueprint(adresses, url_prefix='/api/bibnoms')

        from apptax.taxonomie.routestaxref import adresses
        app.register_blueprint(adresses, url_prefix='/api/taxref')

        from apptax.taxonomie.routesbibattributs import adresses
        app.register_blueprint(adresses, url_prefix='/api/bibattributs')

        from apptax.taxonomie.routesbiblistes import adresses
        app.register_blueprint(adresses, url_prefix='/api/biblistes')

        from apptax.taxonomie.routestmedias import adresses
        app.register_blueprint(adresses, url_prefix='/api/tmedias')

        from apptax.taxonomie.routesbibtypesmedia import adresses
        app.register_blueprint(adresses, url_prefix='/api/bibtypesmedia')

    return app


app = init_app()
CORS(app, supports_credentials=True)
if __name__ == '__main__':
    app.run()

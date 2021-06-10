# coding: utf8
from flask import Flask
from flask_cors import CORS

from apptax.database import db


import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

db = db

app_globals = {}


def init_app():
    if app_globals.get("app", False):
        app = app_globals["app"]
    else:
        app = Flask(__name__)

    with app.app_context():
        app.config.from_pyfile("config.py")
        db.init_app(app)
        db.app = app
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


app = init_app()
CORS(app, supports_credentials=True)
if __name__ == "__main__":
    app.run()

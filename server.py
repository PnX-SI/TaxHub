# coding: utf8
from flask import Flask, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

import importlib
import datetime

from apptax.database import db

db = db

app_globals = {}


def init_app():
    if app_globals.get('app', False):
        app = app_globals['app']
    else:
        app = Flask(__name__)

    with app.app_context():
        app.config.from_pyfile('config.py')
        db.init_app(app)
        db.app = app

    @app.teardown_request
    def _manage_transaction(exception):
        print('_manage_transaction')
        if exception:
            db.session.rollback()
        else:
            db.session.commit()
        db.session.remove()

    from apptax.index import routes
    app.register_blueprint(routes, url_prefix='/')

    from pypnusershub import routes
    app.register_blueprint(routes.routes, url_prefix='/api/auth')

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
CORS(app)
if __name__ == '__main__':
    app.run()

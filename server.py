#coding: utf8
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import importlib
db = SQLAlchemy()
app_globals = {}

def init_app():
    if app_globals.get('app', False):
        app= app_globals['app']
    else :
        app = Flask(__name__)

    app.config.from_pyfile('config.py')
    db.init_app(app)
    app_globals['app'] = app

    from apptax.index import routes
    app.register_blueprint(routes, url_prefix='/')

    routesAuth = importlib.import_module("apptax.flaskmodule-UserHub-auth.routes")
    app.register_blueprint(routesAuth.routes, url_prefix='/api/auth')

    from apptax.taxonomie.routesbibtaxons import adresses
    app.register_blueprint(adresses, url_prefix='/api/bibtaxons')

    from apptax.taxonomie.routestaxref import adresses
    app.register_blueprint(adresses, url_prefix='/api/taxref')

    from apptax.taxonomie.routesbibattributs import adresses
    app.register_blueprint(adresses, url_prefix='/api/bibattributs')

    from apptax.taxonomie.routesbiblistes import adresses
    app.register_blueprint(adresses, url_prefix='/api/biblistes')
    return app

if __name__ == '__main__':
    init_app().run(debug=True)

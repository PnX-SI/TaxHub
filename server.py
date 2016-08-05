#coding: utf8
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import importlib
import datetime

db = SQLAlchemy()
app_globals = {}

def init_app():
    if app_globals.get('app', False):
        app = app_globals['app']
    else :
        app = Flask(__name__)

    app.config.from_pyfile('config.py')
    db.init_app(app)
    app_globals['app'] = app

    from apptax.index import routes
    app.register_blueprint(routes, url_prefix='/')

    routesAuth = importlib.import_module("apptax.UsersHub-authentification-module.routes")
    app.register_blueprint(routesAuth.routes, url_prefix='/api/auth')

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

    @app.after_request
    def after_request(response):
        try:
            print('after_request')
            if 'token' in request.cookies:
                cookie_exp = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds= app.config['COOKIE_EXPIRATION'])
                response.set_cookie('token', request.cookies['token'], expires=cookie_exp)
                response.set_cookie('currentUser', request.cookies['currentUser'], expires=cookie_exp)
            return response
        except Exception as e:
            print ('NO TOKEN')
            return response

    return app

if __name__ == '__main__':
    init_app().run()

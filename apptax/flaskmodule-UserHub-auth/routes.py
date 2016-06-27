#coding: utf8

'''
routes relatives aux application, utilisateurs et à l'authentification
'''

import json
import uuid
import datetime
from functools import wraps
from flask import Blueprint, Flask, request, jsonify, session, g, Response
from server import db,init_app
from . import models
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

routes = Blueprint('auth', __name__)


def check_auth(level):
    def _check_auth(fn):
        @wraps(fn)
        def __check_auth(*args, **kwargs):
            print('check auth')
            try:
                s = Serializer(init_app().config['SECRET_KEY'])
                data = s.loads(request.cookies['token'])

                user = models.AppUser.query\
                    .filter(models.AppUser.id_role==data['id_role'])\
                    .filter(models.AppUser.id_application==data['id_application'])\
                    .one()
                if user.id_droit_max < level:
                    print('Niveau de droit insufissants')
                    return Response('Forbidden', 403)

                return fn(*args, **kwargs)
            except Exception as e:
                return Response('Forbidden', 403)
        return __check_auth
    return _check_auth


@routes.route('/login', methods=['POST'])
def login():
    try:
        user_data = request.json
        user = models.AppUser.query\
            .filter(models.AppUser.identifiant==user_data['login'])\
            .filter(models.AppUser.id_application==user_data['id_application'])\
            .one()

        if not user.check_password(user_data['password']):
            raise

        #Génération d'un token
        s = Serializer(init_app().config['SECRET_KEY'], expires_in = 24*60*60)
        token = s.dumps({'id_role':user.id_role, 'id_application':user.id_application})
        resp = Response(json.dumps({'user':user.as_dict(), 'token': token.decode('ascii')}))
        cookie_exp = datetime.datetime.now() + datetime.timedelta(days=1)
        resp.set_cookie('token', token, expires=cookie_exp)
        return resp
    except Exception as e:
        print(e)
        resp = Response(json.dumps({'login': False}), status=403)
        return resp

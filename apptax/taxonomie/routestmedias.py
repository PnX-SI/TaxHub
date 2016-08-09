#coding: utf8
from flask import jsonify, json, Blueprint
from flask import request, Response

from server import db

from ..utils.utilssqlalchemy import json_resp
from .models import BibNoms, TMedias, BibTypesMedia
from sqlalchemy import select, or_

import importlib
fnauth = importlib.import_module("apptax.UsersHub-authentification-module.routes")

adresses = Blueprint('t_media', __name__)

@adresses.route('/', methods=['GET'])
@adresses.route('/<int:id>', methods=['GET'])
@json_resp
def get_tmedias(id = None):
    if id:
        data = db.session.query(TMedias).filter_by(id_media=id).first()
        return data.as_dict()
    else :
        data = db.session.query(TMedias).all()
        return [media.as_dict() for media in data]


@adresses.route('/<cdref>', methods=['GET'])
@json_resp
def get_tmediasbyTaxon(cdref):
    q = db.session.query(TMedias)
    if cdref :
        q = q.filter_by(cd_ref=cdref)
    results = q.all()
    obj = []
    for media in results :
            o = dict(media.as_dict().items())
            o.update(dict(media.types.as_dict().items()))
            obj.append(o)
    return obj


@adresses.route('/<type>', methods=['GET'])
@json_resp
def get_tmediasbyType(type):
    q = db.session.query(TMedias)
    if type :
        q = q.filter_by(id_type=type)
    results = q.all()
    obj = []
    for media in results :
            o = dict(media.as_dict().items())
            o.update(dict(media.types.as_dict().items()))
            obj.append(o)
    return obj

@adresses.route('/', methods=['POST', 'PUT'])
@adresses.route('/<int:id_media>', methods=['POST', 'PUT'])
@fnauth.check_auth(4)   
def insertUpdate_bibtaxons(id_media=None):
    data = request.get_json(silent=True)
    # print(data)
    if id_media:
        myMedia = db.session.query(TMedias).filter_by(id_media=id_media).first()
        myMedia.cd_ref = data['cd_ref'], # Le cd_ref a t-il une bonne raison de changer. Sinon on le supprime.
        myMedia.titre = data['titre'],
        myMedia.chemin = data['chemin'],
        myMedia.auteur = data['auteur'],
        myMedia.url = data['url'],
        myMedia.desc_media = data['desc_media'],
        # date_media = data['date_media'], TODO : voir le mode de gestion de la date du media (trigger ???)
        myMedia.is_public = data['is_public'],
        myMedia.supprime = "false",
        myMedia.id_type = data['id_type']
    else:
        myMedia = TMedias(
            cd_ref = data['cd_ref'],
            titre = data['titre'],
            chemin = data['chemin'],
            auteur = data['auteur'],
            # url = data['url'], TODO : test if empty or not
            desc_media = data['desc_media'],
            # date_media = data['date_media'], TODO : voir le mode de gestion de la date du media(trigger ???)
            is_public = data['is_public'],
            supprime = "false",
            id_type = data['id_type']
        )
    db.session.add(myMedia)
    db.session.commit()
    
    id_media = myMedia.id_media
    
    return json.dumps({'success':True, 'id_media':id_media}), 200, {'ContentType':'application/json'}
    
@adresses.route('/<int:id_media>', methods=['DELETE'])
@fnauth.check_auth(4)
def delete_tmedias(id_media):
    myMedia =db.session.query(TMedias).filter_by(id_media=id_media).first()
    db.session.delete(myMedia)
    db.session.commit()
    #todo : remove attached file(s)
    
    return json.dumps({'success':True, 'id_media':id_media}), 200, {'ContentType':'application/json'}
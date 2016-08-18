#coding: utf8
from flask import jsonify, json, Blueprint
from flask import request, Response

from server import db,init_app

from ..utils.utilssqlalchemy import json_resp
from .models import BibNoms, TMedias, BibTypesMedia
from sqlalchemy import select, or_
from werkzeug.utils import secure_filename

from sqlalchemy.exc import IntegrityError

import os

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
    print ('insertUpdate_bibtaxons')

    if request.files :
        file = request.files['file']
    data = {}
    if request.form :
        formData = dict(request.form)
        for key in formData :
            data[key] = formData[key][0]
    else :
        data = request.get_json(silent=True)
    print(data)
    #Si MAJ : récupération des données; Sinon création d'un nouvel objet
    if id_media:
        myMedia = db.session.query(TMedias).filter_by(id_media=id_media).first()
        myMedia.cd_ref = data['cd_ref']
    else:
        myMedia = TMedias(cd_ref =  int(data['cd_ref']))

    #Si il y a un fichier et qu'il est différent du précédent
    if ('file' in locals()) and ((data['isFile'] == True) or (data['isFile'] == 'true' )):
        print('chemin')
        myMedia.url = ''
        if myMedia.chemin != '' :
            try :
                remove_file(myMedia.chemin)
            except :
                pass
        filepath = upload_file(file, myMedia.cd_ref, data['titre'])
        myMedia.chemin = filepath
    elif ('url' in data) and (data['url'] != 'null') and (data['isFile'] != True) :
        print('url')
        myMedia.url = data['url']
        if myMedia.chemin != '' :
            try :
                remove_file(myMedia.chemin)
                myMedia.chemin = ''
            except :
                pass

    myMedia.titre = data['titre']
    if 'auteur' in data :
        myMedia.auteur = data['auteur']
    if 'desc_media' in data :
        myMedia.desc_media = data['desc_media']
    # date_media = data['date_media'], TODO : voir le mode de gestion de la date du media (trigger ???)
    myMedia.is_public = data['is_public']
    myMedia.supprime = "false"
    myMedia.id_type = data['id_type']

    db.session.add(myMedia)
    try :
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        return json.dumps({'success':False, 'message': 'Le titre du média doit être unique' }), 500, {'ContentType':'application/json'}
    except Exception as e:
        print ('Exception')
        db.session.rollback()
        print (e)
        return json.dumps({'success':False }), 500, {'ContentType':'application/json'}


    id_media = myMedia.id_media

    return json.dumps({'success':True, 'id_media':id_media, 'media' : myMedia.as_dict() }), 200, {'ContentType':'application/json'}

@adresses.route('/<int:id_media>', methods=['DELETE'])
@fnauth.check_auth(4)
def delete_tmedias(id_media):
    myMedia =db.session.query(TMedias).filter_by(id_media=id_media).first()
    if myMedia.chemin != '' :
        try :
            remove_file(myMedia.chemin)
        except :
            pass
    db.session.delete(myMedia)
    db.session.commit()

    return json.dumps({'success':True, 'id_media':id_media}), 200, {'ContentType':'application/json'}

def remove_file(filepath):
    os.remove(os.path.join(init_app().config['BASE_DIR'], filepath))

def upload_file(file, cd_ref, titre):
    print('upload_file')
    filename = str(cd_ref)+ '_' + secure_filename(titre) + '.' + file.filename.rsplit('.', 1)[1]
    filepath = os.path.join(init_app().config['UPLOAD_FOLDER'], filename)
    file.save(os.path.join(init_app().config['BASE_DIR'], filepath))
    return filepath

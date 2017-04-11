#coding: utf8
from flask import jsonify, json, Blueprint, request, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select, or_

from ..utils.utilssqlalchemy import json_resp
from .models import BibListes, CorNomListe

db = SQLAlchemy()
adresses = Blueprint('bib_listes', __name__)

@adresses.route('/', methods=['GET'])
@adresses.route('/<int:id>', methods=['GET'])
@json_resp
def get_biblistes(id = None):
    if id:
        data = db.session.query(BibListes).filter_by(id_liste=id).first()
        return data.as_dict()
    else :
        data = db.session.query(BibListes).all()
        maliste = []
        for l in data:
            d = l.as_dict()
            d['nb_taxons'] = len(l.cnl)
            maliste.append(d)
        return maliste


@adresses.route('/<regne>', methods=['GET'])
@adresses.route('/<regne>/<group2_inpn>', methods=['GET'])
@json_resp
def get_biblistesbyTaxref(regne, group2_inpn = None):
    q = db.session.query(BibListes)
    if regne :
        q = q.filter(or_(BibListes.regne == regne, BibListes.regne == None))
    if group2_inpn :
        q = q.filter(or_(BibListes.group2_inpn == group2_inpn, BibListes.group2_inpn == None))
    results = q.all()
    return [liste.as_dict() for liste in results]


@adresses.route('/noms/<int:idliste>', methods=['GET'])
@json_resp
def get_cor_biblistesnoms(idliste = None):
  
    limit = request.args.get('limit') if request.args.get('limit') else 100
    offset = request.args.get('page') if request.args.get('page') else 0

    data = db.session.query(CorNomListe).filter_by(id_liste=idliste).limit(limit).offset(offset).all()
    data_liste = db.session.query(BibListes).filter_by(id_liste=idliste).first()
    # query for get nom and taxref
    liste = [{'nom':nom.bib_nom.as_dict(), 'taxref' : nom.bib_nom.taxref.as_dict()} for nom in data]
    # querty for get liste
    nom_liste = data_liste.as_dict()
    # return  data_liste.as_dict()

    if len(liste) == 0 : 
        return  [nom_liste,[]]
    else:
        return  [nom_liste,liste]

@adresses.route('/count', methods=['GET'])
@json_resp
def get_countbiblistes():
    #Compter le nombre d'enregistrements dans biblistes
    return db.session.query(BibListes).count() 
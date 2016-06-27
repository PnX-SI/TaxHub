#coding: utf8
from flask import jsonify, json, Blueprint
from flask import request, Response

from server import db

from ..utils.utilssqlalchemy import json_resp
from .models import BibListes
from sqlalchemy import select, or_

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
        return [liste.as_dict() for liste in data]


@adresses.route('/<regne>', methods=['GET'])
@adresses.route('/<regne>/<group2_inpn>', methods=['GET'])
@json_resp
def get_biblistesbyTaxref(regne, group2_inpn = None):
    q = db.session.query(BibListes)
    if regne :
        q = q.filter(or_(BibListes.regne == regne, BibListes.regne == None))
    if group2_inpn :
        q = q.filter(or_(BibListes.group2_inpn == group2_inpn, BibListes.group2_inpn == None))
    print (q)
    results = q.all()
    return [liste.as_dict() for liste in results]

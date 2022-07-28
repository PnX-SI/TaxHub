# coding: utf8
from flask import jsonify, json, Blueprint, request, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select, or_

from ..utils.utilssqlalchemy import json_resp
from .models import BibNoms, Taxref, CorTaxonAttribut, BibAttributs

from . import db

adresses = Blueprint("bib_attribut", __name__)


@adresses.route("/", methods=["GET"])
@adresses.route("/<int:id>", methods=["GET"])
@json_resp
def get_bibattributs(id=None):
    if id:
        data = db.session.query(BibAttributs).filter_by(id_attribut=id).first()
        return data.as_dict()
    else:
        data = db.session.query(BibAttributs).all()
        return [attribut.as_dict() for attribut in data]


@adresses.route("/<regne>", methods=["GET"])
@adresses.route("/<regne>/<group2_inpn>", methods=["GET"])
@json_resp
def get_bibattributsbyTaxref(regne, group2_inpn=None):
    q = db.session.query(BibAttributs)
    if regne:
        q = q.filter(or_(BibAttributs.regne == regne, BibAttributs.regne == None))
    if group2_inpn:
        q = q.filter(
            or_(BibAttributs.group2_inpn == group2_inpn, BibAttributs.group2_inpn == None)
        )
    results = q.all()

    attDict = {}
    for attribut in results:
        o = dict(attribut.as_dict().items())
        idTheme = attribut.id_theme
        if idTheme not in attDict.keys():
            t = dict(attribut.theme.as_dict().items())
            attDict[idTheme] = t
            attDict[idTheme]["attributs"] = []
        attDict[idTheme]["attributs"].append(o)
    return list(attDict.values())

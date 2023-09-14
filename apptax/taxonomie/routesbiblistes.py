# coding: utf8

import os
import logging

from flask import Blueprint, request, current_app
from sqlalchemy import func, or_
from sqlalchemy.orm import joinedload

from pypnusershub import routes as fnauth
from utils_flask_sqla.response import json_resp

from . import filemanager
from . import db
from ..utils.utilssqlalchemy import json_resp, csv_resp
from ..utils.genericfunctions import calculate_offset_page
from .models import BibListes, Taxref
from apptax.taxonomie.schemas import BibListesSchema

adresses = Blueprint("bib_listes", __name__)
logger = logging.getLogger()

# !! les routes  get_biblistes et get_biblistesbyTaxref ne retourne pas les données
#       selon le même format !!!


@adresses.route("/", methods=["GET"])
@json_resp
def get_biblistes(id=None):
    """
    retourne les contenu de bib_listes dans "data"
    et le nombre d'enregistrements dans "count"
    """
    data = db.session.query(BibListes).all()
    biblistes_schema = BibListesSchema(exclude=("v_regne", "v_group2_inpn"))
    maliste = {"data": [], "count": 0}
    maliste["count"] = len(data)
    maliste["data"] = biblistes_schema.dump(data, many=True)
    return maliste


@adresses.route("/<regne>", methods=["GET"])
@adresses.route("/<regne>/<group2_inpn>", methods=["GET"])
def get_biblistesbyTaxref(regne, group2_inpn=None):
    q = db.session.query(BibListes)
    if regne:
        q = q.filter(or_(BibListes.v_regne == regne, BibListes.v_regne == None))
    if group2_inpn:
        q = q.filter(or_(BibListes.v_group2_inpn == group2_inpn, BibListes.v_group2_inpn == None))
    results = q.all()
    return BibListesSchema(exclude=("v_regne", "v_group2_inpn")).dump(results, many=True)


@adresses.route("/cor_nom_liste", methods=["GET"])
@json_resp
def get_cor_nom_liste():
    limit = request.args.get("limit", 20, int)
    page = request.args.get("page", 1, int)
    q = db.session.query(BibListes.id_liste, Taxref.cd_nom).join(BibListes.noms)
    total = q.count()
    results = q.paginate(page=page, per_page=limit, error_out=False)
    items = []
    for r in results.items:
        items.append({"id_liste": r.id_liste, "cd_nom": r.cd_nom})
    return {
        "items": items,
        "total": total,
        "limit": limit,
        "page": page,
    }

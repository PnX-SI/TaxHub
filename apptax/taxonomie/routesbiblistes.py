# coding: utf8

import os
import logging

from flask import Blueprint
from sqlalchemy import select

from utils_flask_sqla.response import json_resp

from . import db
from .models import BibListes
from apptax.taxonomie.schemas import BibListesSchema

adresses = Blueprint("bib_listes", __name__)
logger = logging.getLogger()

# !! les routes  get_biblistes et get_biblistesbyTaxref ne retourne pas les données
#       selon le même format !!!


@adresses.route("/", methods=["GET"])
@json_resp
def get_biblistes():
    """
    retourne les contenu de bib_listes dans "data"
    et le nombre d'enregistrements dans "count"
    """
    biblistes_records = db.session.execute(
        select(
            BibListes.id_liste,
            BibListes.code_liste,
            BibListes.nom_liste,
            BibListes.desc_liste,
            BibListes.nb_taxons,
            BibListes.regne,
            BibListes.group2_inpn,
        )
    ).all()
    biblistes_schema = BibListesSchema()
    biblistes_infos = {
        "data": biblistes_schema.dump(biblistes_records, many=True),
        "count": len(biblistes_records),
    }

    return biblistes_infos


@adresses.route("/<regne>", methods=["GET"], defaults={"group2_inpn": None})
@adresses.route("/<regne>/<group2_inpn>", methods=["GET"])
def get_biblistesbyTaxref(regne, group2_inpn):
    q = select(BibListes)
    if regne:
        q = q.where(BibListes.regne == regne)
    if group2_inpn:
        q = q.where(BibListes.group2_inpn == group2_inpn)
    results = db.session.scalars(q).all()
    return BibListesSchema().dump(results, many=True)

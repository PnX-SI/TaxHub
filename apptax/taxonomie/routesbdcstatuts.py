# coding: utf8

import os
import logging

from flask import Blueprint, request, current_app
from sqlalchemy import func, or_

from pypnusershub import routes as fnauth

from . import filemanager
from . import db
from ..log import logmanager
from ..utils.utilssqlalchemy import json_resp, csv_resp
from ..utils.genericfunctions import calculate_offset_page
from .models import (
    TaxrefBdcStatutCorTextValues,
    TaxrefBdcStatutTaxon,
    TaxrefBdcStatutText,
    TaxrefBdcStatutType,
    TaxrefBdcStatutValues
)


adresses = Blueprint("bdc_status", __name__)
logger = logging.getLogger()


@adresses.route("/<cd_ref>", methods=["GET"])
@json_resp
def get_biblistes(cd_ref=None):
    """
        retourne les contenu de bib_listes dans "data"
        et le nombre d'enregistrements dans "count"
        """
    q = db.session.query(TaxrefBdcStatutTaxon).filter_by(
        cd_ref = cd_ref
    )
    print(q)
    data = q.all()
    maliste = {"data": [], "count": 0}
    print(data)
    for l in data:
        d = l.as_dict()
        d['value'] = l.value_text.value.as_dict()
        d['text'] = l.value_text.text.as_dict()
        maliste["data"].append(d)
    return maliste

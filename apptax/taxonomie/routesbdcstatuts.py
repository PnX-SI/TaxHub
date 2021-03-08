# coding: utf8

import os
import logging
from flask import jsonify
from flask import Blueprint, request, current_app
from sqlalchemy import func, or_
from sqlalchemy.orm import joinedload

from pypnusershub import routes as fnauth

from . import filemanager
from . import db
from ..log import logmanager
from ..utils.utilssqlalchemy import json_resp, csv_resp, dict_merge
from ..utils.genericfunctions import calculate_offset_page
from .models import (
    TaxrefBdcStatutCorTextValues,
    TaxrefBdcStatutTaxon,
    TaxrefBdcStatutText,
    TaxrefBdcStatutType,
    TaxrefBdcStatutValues,
    VBdcStatus
)


adresses = Blueprint("bdc_status", __name__)
logger = logging.getLogger()


@adresses.route("/list/<cd_ref>", methods=["GET"])
@json_resp
def get_bdcstatus_list_for_one_taxon(cd_ref=None):
    """
        retourne la listes des statuts associés à un taxon
    """
    q = db.session.query(VBdcStatus).filter_by(
        cd_ref=cd_ref
    )
    print(q)
    data = q.all()
    return [d.as_dict() for d in data]


@adresses.route("/hierarchy/<cd_ref>", methods=["GET"])
@json_resp
def get_bdcstatus_hierarchy(cd_ref=None):
    """
        retourne la listes des statuts associés sous forme hierarchique
    """
    # get parameters type:
    type_statut = request.args.get("type_statut")

    q = (
        db.session.query(TaxrefBdcStatutTaxon)
        .join(TaxrefBdcStatutCorTextValues)
        .join(TaxrefBdcStatutText)
        .filter(
            TaxrefBdcStatutTaxon.cd_ref == cd_ref
        ).filter(
            TaxrefBdcStatutText.enable == True
        )
    )
    if type_statut:
        q = q.filter(
            TaxrefBdcStatutText.cd_type_statut == type_statut
        )

    q = (
        q.options(
            joinedload(TaxrefBdcStatutTaxon.value_text)
            .joinedload(TaxrefBdcStatutCorTextValues.value)
        ).options(
            joinedload(TaxrefBdcStatutTaxon.value_text)
            .joinedload(TaxrefBdcStatutCorTextValues.text)
            .joinedload(TaxrefBdcStatutText.type_statut)
        )
    )
    data = q.all()
    results = {}

    for d in data:
        cd_type_statut = d.value_text.text.type_statut.cd_type_statut
        res = {** d.value_text.text.type_statut.as_dict(), **{"text": {}}}
        id_text = d.value_text.text.id_text
        res["text"][id_text] = {**d.value_text.text.as_dict(), **{"values": {}}}

        res["text"][id_text]["values"][d.value_text.id_value_text] = {
            **d.as_dict(), **d.value_text.value.as_dict()
        }

        if cd_type_statut in results:
            dict_merge(results[cd_type_statut], res)
        else:
            results[cd_type_statut] = res

    return results

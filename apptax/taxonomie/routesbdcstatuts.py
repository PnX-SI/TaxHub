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
from .repositories import BdcStatusRepository
from .models import (
    TaxrefBdcStatutCorTextValues,
    TaxrefBdcStatutText,
    TaxrefBdcStatutType,
    TaxrefBdcStatutValues,
    VBdcStatus,
)

adresses = Blueprint("bdc_status", __name__)
logger = logging.getLogger()


@adresses.route("/list/<cd_ref>", methods=["GET"])
@json_resp
def get_bdcstatus_list_for_one_taxon(cd_ref=None):
    """
    Retourne la liste des statuts associés à un taxon.
    """
    q = db.session.query(VBdcStatus).filter_by(cd_ref=cd_ref)
    data = q.all()
    return [d.as_dict() for d in data]


@adresses.route("/hierarchy/<cd_ref>", methods=["GET"])
@json_resp
def get_bdcstatus_hierarchy(cd_ref=None):
    """
    Retourne la liste des statuts associés sous forme hiérarchique.
    """
    # get parameters type:
    type_statut = request.args.get("type_statut")

    results = BdcStatusRepository().get_status(
        cd_ref=cd_ref, type_statut=type_statut, enable=True, format=True
    )

    return results


@adresses.route("/status_values/<status_type>", methods=["GET"])
@json_resp
def get_status_lists_values(status_type=None):
    """
    Retourne les valeurs (code et intitulé) d'un type de statut.

    Params:
    :param status_type: code d'un type de statut de statuy. Obligatoire.

    :returns: une liste de dictionnaires contenant les infos des valeurs
    d'un type de liste de rouge.
    """
    data = (
        db.session.query(TaxrefBdcStatutValues)
        .join(
            TaxrefBdcStatutCorTextValues,
            TaxrefBdcStatutValues.id_value == TaxrefBdcStatutCorTextValues.id_value,
        )
        .join(
            TaxrefBdcStatutText,
            TaxrefBdcStatutText.id_text == TaxrefBdcStatutCorTextValues.id_text,
        )
        .filter(TaxrefBdcStatutText.cd_type_statut == status_type)
        .order_by(TaxrefBdcStatutValues.code_statut)
        .distinct()
    )
    return [d.as_dict(fields=("code_statut", "label_statut", "display")) for d in data]


@adresses.route("/status_types", methods=["GET"])
@json_resp
def get_status_types():
    """
    Retourne les types (code et intitulé) avec leur regroupement.

    Params:
    :query str codes: filtre sur une liste de codes de types de statuts
    séparés par des virgules.
    :query str gatherings: filtre sur une liste de type de regroupement
    de types de statuts séparés par des virgules.

    :returns: une liste de dictionnaires contenant les infos d'un type de statuts.
    """
    query = db.session.query(TaxrefBdcStatutType).order_by(TaxrefBdcStatutType.lb_type_statut)

    # Use request parameters
    codes = extract_multi_values_request_param("codes")
    if codes:
        query = query.filter(TaxrefBdcStatutType.cd_type_statut.in_(codes))

    gatherings = extract_multi_values_request_param("gatherings")
    if gatherings:
        query = query.filter(TaxrefBdcStatutType.regroupement_type.in_(gatherings))

    data = query.all()
    return [
        d.as_dict(fields=("cd_type_statut", "lb_type_statut", "regroupement_type", "display"))
        for d in data
    ]


def extract_multi_values_request_param(paramName):
    param_values = None
    if paramName in request.args:
        param_values = request.args.get(paramName).split(",")
        if len(param_values) > 0:
            param_values = map(str.strip, param_values)
    return param_values

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
from .models import VBdcStatus

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

    results = BdcStatusRepository().get_status(
        cd_ref=cd_ref,
        type_statut=type_statut,
        enable=True,
        format=True
    )

    return results

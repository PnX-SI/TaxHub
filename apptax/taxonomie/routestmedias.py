# coding: utf8
import logging
import os
from flask import jsonify, json, Blueprint, request, Response, g, current_app, send_file

from sqlalchemy.exc import IntegrityError
from PIL import Image

from pypnusershub import routes as fnauth

from . import db
from . import filemanager
from .filemanager import FILEMANAGER
from ..log import logmanager
from ..utils.utilssqlalchemy import json_resp
from .models import TMedias, BibTypesMedia
from .repositories import MediaRepository

adresses = Blueprint("t_media", __name__)
logger = logging.getLogger()

media_repo = MediaRepository(db.session, current_app.config.get("S3_BUCKET_NAME"))


@adresses.route("/", methods=["GET"])
@adresses.route("/<int:id>", methods=["GET"])
@json_resp
def get_tmedias(id=None):
    if id:
        return media_repo.get_and_format_one_media(id)
    return media_repo.get_and_format_media_filter_by(
        filters={}, force_path=request.args.get("forcePath", False)
    )


@adresses.route("/bycdref/<cdref>", methods=["GET"])
@json_resp
def get_tmediasbyTaxon(cdref):

    filters = {}
    if cdref:
        filters = {"cd_ref": cdref}
    obj = media_repo.get_and_format_media_filter_by(
        filters=filters, force_path=request.args.get("forcePath", False)
    )
    return obj


# REM : Route utilisée ?????
#  Rentre en conflit avec  get_tmedias
@adresses.route("/<type>", methods=["GET"])
@json_resp
def get_tmediasbyType(type):
    filters = {}
    if type:
        filters = {"id_type": type}
    obj = media_repo.get_media_filter_by(
        filters=filters, force_path=request.args.get("forcePath", False)
    )
    return obj


@adresses.route("/", methods=["POST", "PUT"])
@adresses.route("/<int:id_media>", methods=["POST", "PUT"])
@fnauth.check_auth(2, True)
def insertUpdate_tmedias(id_media=None, id_role=None):
    # récupération des données du formulaire
    upload_file = None
    if request.files:
        upload_file = request.files["file"]

    data = {}
    if request.form:
        data = request.form.to_dict()
    else:
        data = request.get_json(silent=True)

    # Enregistrement des données du média
    myMedia, action = media_repo.import_media(data, upload_file, id_media)

    # Log
    logmanager.log_action(
        id_role,
        "bib_media",
        myMedia.id_media,
        repr(myMedia),
        action,
        "Traitement média : " + myMedia.titre,
    )
    return (
        json.dumps({"success": True, "id_media": myMedia.id_media, "media": myMedia.as_dict()}),
        200,
        {"ContentType": "application/json"},
    )


@adresses.route("/<int:id_media>", methods=["DELETE"])
@fnauth.check_auth(2, True)
def delete_tmedias(id_media, id_role):
    myMedia = media_repo.delete(id_media)
    # Log
    logmanager.log_action(
        id_role,
        "bib_media",
        id_media,
        repr(myMedia),
        "DELETE",
        "Suppression du média : " + myMedia.titre,
    )
    return (
        json.dumps({"success": True, "id_media": id_media}),
        200,
        {"ContentType": "application/json"},
    )


@adresses.route("/thumbnail/<int:id_media>", methods=["GET"])
def getThumbnail_tmedias(id_media):
    """
    Fonction qui génère une vignette d'un média existants

    Params
    ------
        id_media : identifiant du média
        h : hauteur souhaitée
        w : largeur souhaitée
        regenerate : force la régénération du thumbnail

    Return
    ------
        Image générée
    """

    myMedia = media_repo.get_one_media(id_media)
    if myMedia is None:
        return (
            json.dumps(
                {
                    "success": False,
                    "id_media": id_media,
                    "message": "Le média demandé n" "éxiste pas",
                }
            ),
            400,
            {"ContentType": "application/json"},
        )

    params = request.args
    pad = True
    size = (300, 400)
    if ("h" in params) or ("w" in params):
        size = (int(params.get("h", -1)), int(params.get("w", -1)))

    regenerate = False
    if ("regenerate" in params) and (params.get("regenerate") == "true"):
        regenerate = True

    thumbpath = FILEMANAGER.create_thumb(myMedia, size, regenerate)

    return send_file(thumbpath, mimetype="image/jpg")

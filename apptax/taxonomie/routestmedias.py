# coding: utf8
import logging
from pathlib import Path
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

    force = False
    if ("force" in params) and (params.get("force") == "true"):
        force = True
    regenerate = False
    if ("regenerate" in params) and (params.get("regenerate") == "true"):
        regenerate = True

    thumbpath = FILEMANAGER.create_thumb(myMedia, size, force, regenerate)

    return send_file(os.path.join(Path(current_app.config["MEDIA_FOLDER"]).absolute(), thumbpath))

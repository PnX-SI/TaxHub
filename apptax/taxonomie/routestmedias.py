# coding: utf8
import logging
from pathlib import Path
import os
from flask import json, Blueprint, request, current_app, send_file, abort
from sqlalchemy import select
from werkzeug.exceptions import Forbidden


from .models import TMedias, BibTypesMedia
from .schemas import TMediasSchema, BibTypesMediaSchema
from apptax.taxonomie.filemanager import LocalFileManagerService
from apptax.database import db

DEFAULT_THUMBNAIL_SIZE = (300, 400)

adresses = Blueprint("t_media", __name__)
logger = logging.getLogger()


@adresses.route("/", methods=["GET"])
@adresses.route("/<int:id>", methods=["GET"])
def get_tmedias(id=None):
    """
    Liste des médias
    TODO add pagination
    """
    if id:
        media = db.session.get(TMedias, id)
        return TMediasSchema().dump(media)
    medias = db.session.scalars(select(TMedias)).all()
    return TMediasSchema().dump(medias, many=True)


@adresses.route("/types", methods=["GET"])
@adresses.route("/types/<int:id>", methods=["GET"])
def get_type_tmedias(id=None):
    """
    Liste des types de médias
    """
    if id:
        type_media = db.session.get(BibTypesMedia, id)
        return BibTypesMediaSchema().dump(type_media)
    types_media = db.session.scalars(select(BibTypesMedia)).all()
    return BibTypesMediaSchema().dump(types_media, many=True)


@adresses.route("/bycdref/<cd_ref>", methods=["GET"])
def get_tmediasbyTaxon(cd_ref):
    """
    Liste des médias associés à un taxon
    """
    q = select(TMedias).filter_by(cd_ref=cd_ref)
    medias = db.session.scalars(q).all()
    return TMediasSchema().dump(medias, many=True)


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

    media = db.session.get(TMedias, id_media)
    if media is None:
        return (
            json.dumps(
                {
                    "success": False,
                    "id_media": id_media,
                    "message": "Le média demandé n'existe pas",
                }
            ),
            400,
            {"ContentType": "application/json"},
        )

    params = request.args

    size = DEFAULT_THUMBNAIL_SIZE

    height_params: str = params.get("h", None)
    width_params: str = params.get("w", None)
    force = params.get("force") == "true"
    regenerate = params.get("regenerate") == "true"

    if (width_params and not width_params.isdigit()) or (
        height_params and not height_params.isdigit()
    ):
        raise Forbidden("Valeur de la hauteur ou largeur incorrecte: Un entier est attendu")

    if width_params and not height_params:
        size = [int(width_params), -1]

    if height_params and not width_params:
        size = [-1, int(height_params)]

    if height_params and width_params:
        size = (int(width_params), int(height_params))
        force = True

    thumbpath = LocalFileManagerService().create_thumb(media, size, force, regenerate)
    if thumbpath:
        return send_file(
            os.path.join(Path(current_app.config["MEDIA_FOLDER"]).absolute(), "taxhub", thumbpath)
        )
    else:
        abort(404)

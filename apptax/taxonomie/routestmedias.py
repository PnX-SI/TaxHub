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

media_repo = MediaRepository(db.session, current_app.config["S3_BUCKET_NAME"])


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
    try:
        if request.files:
            file = request.files["file"]
        data = {}
        if request.form:
            data = request.form.to_dict()
        else:
            data = request.get_json(silent=True)

        # Si MAJ : récupération des données; Sinon création d'un nouvel objet
        if id_media:
            myMedia = db.session.query(TMedias).filter_by(id_media=id_media).first()
            myMedia.cd_ref = data["cd_ref"]
            old_title = myMedia.titre
            action = "UPDATE"
            # suppression des thumbnails
            FILEMANAGER.remove_thumb(id_media)

        else:
            myMedia = TMedias(cd_ref=int(data["cd_ref"]))
            old_title = ""
            action = "INSERT"
        myMedia.titre = data["titre"]
        if "auteur" in data:
            myMedia.auteur = data["auteur"]
        if "desc_media" in data:
            myMedia.desc_media = data["desc_media"]

        # date_media = data['date_media'],
        # TODO : voir le mode de gestion de la date du media (trigger ???)

        if isinstance(data["is_public"], bool):
            is_pub = data["is_public"]
        else:
            is_pub = json.loads(data["is_public"].lower())

        myMedia.is_public = is_pub
        myMedia.supprime = False
        myMedia.id_type = data["id_type"]
        db.session.add(myMedia)
        try:
            db.session.commit()

        except IntegrityError as e:
            logger.error(e)
            db.session.rollback()
            return (
                json.dumps({"success": False, "message": repr(e.args)}),
                500,
                {"ContentType": "application/json"},
            )
        except Exception as e:
            logger.error(e)
            db.session.rollback()
            return (
                json.dumps({"success": False, "message": repr(e.args)}),
                500,
                {"ContentType": "application/json"},
            )

        if ("file" in locals()) and (
            (data["isFile"] is True) or (data["isFile"] == "true")
        ):
            myMedia.url = ""
            old_chemin = myMedia.chemin
            filepath = FILEMANAGER.upload_file(
                file, myMedia.id_media, myMedia.cd_ref, data["titre"]
            )
            myMedia.chemin = filepath
            if (old_chemin != "") and (old_chemin != myMedia.chemin):
                FILEMANAGER.remove_file(old_chemin)
        elif (
            ("chemin" not in data)
            and ("url" in data)
            and (data["url"] != "null")
            and (data["url"] != "")
            and (data["isFile"] is not True)
        ):
            myMedia.url = data["url"]
            if myMedia.chemin != "":
                FILEMANAGER.remove_file(myMedia.chemin)
                myMedia.chemin = ""
        elif old_title != myMedia.titre:
            filepath = FILEMANAGER.rename_file(myMedia.chemin, old_title, myMedia.titre)
            myMedia.chemin = filepath

        db.session.add(myMedia)
        db.session.commit()

        # preparation de la réponse json (ajout du
        #    nom du type de média pour affichage en front)
        medium = myMedia.as_dict()
        medium["nom_type_media"] = data["nom_type_media"]

        # Log
        logmanager.log_action(
            id_role,
            "bib_media",
            myMedia.id_media,
            repr(myMedia),
            action,
            u"Traitement média : " + myMedia.titre,
        )
        return (
            json.dumps(
                {"success": True, "id_media": myMedia.id_media, "media": medium}
            ),
            200,
            {"ContentType": "application/json"},
        )

    except Exception as e:
        logger.error(e)
        return (
            json.dumps({"success": False, "message": repr(e)}),
            500,
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
        u"Suppression du média : " + myMedia.titre,
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

    try:
        thumbpath = FILEMANAGER.create_thumb(myMedia, size, regenerate)
        print(thumbpath)
    except Exception as e:
        logger.error(e)
        return (
            json.dumps({"success": False, "id_media": id_media, "message": repr(e)}),
            500,
            {"ContentType": "application/json"},
        )
    else:
        print("file exists")

    return send_file(thumbpath, mimetype="image/jpg")

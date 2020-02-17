# coding: utf8
import logging
from flask import jsonify, json, Blueprint, request, Response, g, current_app, send_file

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

import re
import os
import cv2

from ..utils.utilssqlalchemy import json_resp
from .models import BibNoms, TMedias, BibTypesMedia
from . import filemanager
from ..log import logmanager

from pypnusershub import routes as fnauth

from . import db

adresses = Blueprint("t_media", __name__)
logger = logging.getLogger()


@adresses.route("/", methods=["GET"])
@adresses.route("/<int:id>", methods=["GET"])
@json_resp
def get_tmedias(id=None):
    if id:
        data = db.session.query(TMedias).filter_by(id_media=id).first()
        return data.as_dict()
    else:
        data = db.session.query(TMedias).all()
        return [media.as_dict() for media in data]


@adresses.route("/bycdref/<cdref>", methods=["GET"])
@json_resp
def get_tmediasbyTaxon(cdref):
    q = db.session.query(TMedias)
    if cdref:
        q = q.filter_by(cd_ref=cdref)
    results = q.all()
    obj = []
    for media in results:
        o = dict(media.as_dict().items())
        o.update(dict(media.types.as_dict().items()))
        obj.append(o)
    return obj


@adresses.route("/<type>", methods=["GET"])
@json_resp
def get_tmediasbyType(type):
    q = db.session.query(TMedias)
    if type:
        q = q.filter_by(id_type=type)
    results = q.all()
    obj = []
    for media in results:
        o = dict(media.as_dict().items())
        o.update(dict(media.types.as_dict().items()))
        obj.append(o)
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
            try:
                filemanager.remove_dir(
                    os.path.join(
                        current_app.config["UPLOAD_FOLDER"], "thumb", str(id_media)
                    )
                )
            except (FileNotFoundError, IOError, OSError) as e:
                logger.error(e)
                pass

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
        myMedia.is_public = data["is_public"]
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
            filepath = filemanager.upload_file(
                file, myMedia.id_media, myMedia.cd_ref, data["titre"]
            )
            myMedia.chemin = filepath
            if (old_chemin != "") and (old_chemin != myMedia.chemin):
                filemanager.remove_file(old_chemin)
        elif (
            ("url" in data)
            and (data["url"] != "null")
            and (data["url"] != "")
            and (data["isFile"] is not True)
        ):
            myMedia.url = data["url"]
            if myMedia.chemin != "":
                filemanager.remove_file(myMedia.chemin)
                myMedia.chemin = ""
        elif old_title != myMedia.titre:
            filepath = filemanager.rename_file(myMedia.chemin, old_title, myMedia.titre)
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
    myMedia = db.session.query(TMedias).filter_by(id_media=id_media).first()
    if myMedia.chemin != "":
        filemanager.remove_file(myMedia.chemin)

    db.session.delete(myMedia)
    db.session.commit()
    # suppression des thumbnails
    try:
        filemanager.remove_dir(
            os.path.join(current_app.config["UPLOAD_FOLDER"], "thumb", str(id_media))
        )
    except (FileNotFoundError, IOError, OSError) as e:
        logger.error(e)
        pass
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
    params = request.args
    pad = True
    size = (300, 400)
    if ("h" in params) or ("w" in params):
        size = (int(params.get("h", -1)), int(params.get("w", -1)))

    thumbdir = os.path.join(
        current_app.config["BASE_DIR"],
        current_app.config["UPLOAD_FOLDER"],
        "thumb",
        str(id_media),
    )
    thumbpath = os.path.join(thumbdir, "{}x{}.jpg".format(size[0], size[1]))

    if ("regenerate" in params) and (params.get("regenerate") == "true"):
        filemanager.remove_file(
            os.path.join(
                current_app.config["UPLOAD_FOLDER"],
                "thumb",
                str(id_media),
                "{}x{}.jpg".format(size[0], size[1]),
            )
        )

    if not os.path.exists(thumbpath):
        myMedia = db.session.query(TMedias).filter_by(id_media=id_media).first()

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
        try:
            if (myMedia.chemin) and (myMedia.chemin != ""):
                img = cv2.imread(
                    os.path.join(current_app.config["BASE_DIR"], myMedia.chemin)
                )
            else:
                img = filemanager.url_to_image(myMedia.url)
            resizeImg = filemanager.resizeAndPad(img, size)

            # save file
            if not os.path.exists(thumbdir):
                os.makedirs(thumbdir)

            cv2.imwrite(thumbpath, resizeImg)
        except Exception as e:
            logger.error(e)
            return (
                json.dumps(
                    {"success": False, "id_media": id_media, "message": repr(e)}
                ),
                500,
                {"ContentType": "application/json"},
            )
    else:
        print("file exists")

    return send_file(thumbpath, mimetype="image/jpg")


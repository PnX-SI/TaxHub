# coding: utf8
from warnings import warn
import logging

from flask import Blueprint, request
from werkzeug.exceptions import NotFound


from utils_flask_sqla.response import json_resp

from .models import (
    Taxref,
    CorTaxonAttribut,
    BibThemes,
    BibAttributs,
)
from .models import Taxref, CorTaxonAttribut, BibThemes, BibAttributs, TMedias
from .schemas import TMediasSchema
from . import db

adresses = Blueprint("bib_noms", __name__)
logger = logging.getLogger()


@adresses.route("/taxoninfo/<int(signed=True):cd_nom>", methods=["GET"])
@json_resp
def getOne_bibtaxonsInfo(cd_nom):
    """
    Route qui renvoie les attributs et les médias d'un taxon

    Parameters:

        - cd_nom (integer)
        - id_theme (integer): id du thème des attributs
                (Possibilité de passer plusieurs id_theme)
        - id_attribut(integer): id_attribut
                (Possibilité de passer plusiers id_attribut)
    """
    warn(
        "Route taxoninfo is deprecated, please use taxref detail route instead)",
        DeprecationWarning,
    )

    # Récupération du cd_ref à partir du cd_nom
    taxon = Taxref.query.get(cd_nom)
    if not taxon:
        raise NotFound()
    else:
        cd_ref = taxon.cd_ref
    obj = {}
    # A out des attributs
    obj["attributs"] = []
    q = db.session.query(CorTaxonAttribut).filter_by(cd_ref=cd_ref)
    join_on_bib_attr = False
    if "id_theme" in request.args.keys():
        q = q.join(BibAttributs, BibAttributs.id_attribut == CorTaxonAttribut.id_attribut).filter(
            BibAttributs.id_theme.in_(request.args.getlist("id_theme"))
        )
        join_on_bib_attr = True
    if "id_attribut" in request.args.keys():
        if not join_on_bib_attr:
            q = q.join(BibAttributs, BibAttributs.id_attribut == CorTaxonAttribut.id_attribut)
        q = q.filter(BibAttributs.id_attribut.in_(request.args.getlist("id_attribut")))
    bibAttr = q.all()
    for attr in bibAttr:
        o = dict(attr.as_dict().items())
        o.update(dict(attr.bib_attribut.as_dict().items()))
        id = o["id_theme"]
        theme = db.session.query(BibThemes).filter_by(id_theme=id).first()
        o["nom_theme"] = theme.as_dict()["nom_theme"]
        obj["attributs"].append(o)
    # Ajout des medias
    medias = TMedias.query.filter_by(**{"cd_ref": cd_ref}).all()
    obj["medias"] = TMediasSchema().dump(medias, many=True)

    return obj

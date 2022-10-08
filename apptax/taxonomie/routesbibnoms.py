# coding: utf8
import logging

from flask import json, Blueprint, request, current_app
from sqlalchemy import func

from ..utils.utilssqlalchemy import json_resp
from ..utils.genericfunctions import calculate_offset_page
from ..log import logmanager
from .models import (
    BibNoms,
    Taxref,
    CorTaxonAttribut,
    BibThemes,
    CorNomListe,
    BibAttributs,
)
from .repositories import MediaRepository
from pypnusershub import routes as fnauth
from . import db

adresses = Blueprint("bib_noms", __name__)
logger = logging.getLogger()


media_repo = MediaRepository(db.session, current_app.config.get("S3_BUCKET_NAME"))


@adresses.route("/", methods=["GET"])
@json_resp
def get_bibtaxons():
    bibTaxonColumns = BibNoms.__table__.columns
    taxrefColumns = Taxref.__table__.columns
    parameters = request.args

    q = db.session.query(BibNoms, Taxref).filter(BibNoms.cd_nom == Taxref.cd_nom)

    nbResultsWithoutFilter = q.count()

    # Traitement des parametres
    limit = parameters.get("limit", 20, int)
    page = parameters.get("page", 1, int)
    offset = parameters.get("offset", 0, int)
    (limit, offset, page) = calculate_offset_page(limit, offset, page)

    # Order by
    if "orderby" in parameters:
        if parameters["orderby"] in taxrefColumns:
            orderCol = getattr(taxrefColumns, parameters["orderby"])
        elif parameters["orderby"] in bibTaxonColumns:
            orderCol = getattr(bibTaxonColumns, parameters["orderby"])
        else:
            orderCol = None

        if "order" in parameters:
            if parameters["order"] == "desc":
                orderCol = orderCol.desc()

        q = q.order_by(orderCol)

    for param in parameters:
        if param in taxrefColumns:
            col = getattr(taxrefColumns, param)
            q = q.filter(col == parameters[param])
        elif param in bibTaxonColumns:
            col = getattr(bibTaxonColumns, param)
            q = q.filter(col == parameters[param])
        elif param == "ilikelatin":
            q = q.filter(taxrefColumns.nom_complet.ilike(parameters[param] + "%"))
        elif param == "ilikelfr":
            q = q.filter(bibTaxonColumns.nom_francais.ilike(parameters[param] + "%"))
        elif param == "ilikeauteur":
            q = q.filter(taxrefColumns.lb_auteur.ilike(parameters[param] + "%"))
        elif (param == "is_ref") and (parameters[param] == "true"):
            q = q.filter(taxrefColumns.cd_nom == taxrefColumns.cd_ref)

    nbResults = q.count()
    data = q.limit(limit).offset(offset).all()
    results = []
    for row in data:
        data_as_dict = row.BibNoms.as_dict()
        data_as_dict["taxref"] = row.Taxref.as_dict()
        results.append(data_as_dict)
    # {"data":results,"count":0}
    return {
        "items": results,
        "total": nbResultsWithoutFilter,
        "total_filtered": nbResults,
        "limit": limit,
        "page": page,
    }


@adresses.route("/taxoninfo/<int:cd_nom>", methods=["GET"])
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
    # Récupération du cd_ref à partir du cd_nom
    cd_ref = db.session.query(Taxref.cd_ref).filter_by(cd_nom=cd_nom).first()
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
    obj["medias"] = media_repo.get_and_format_media_filter_by(
        filters={"cd_ref": cd_ref}, force_path=request.args.get("forcePath", False)
    )

    return obj


@adresses.route("/simple/<int:id_nom>", methods=["GET"])
@json_resp
def getOneSimple_bibtaxons(id_nom):
    bibTaxon = db.session.query(BibNoms).filter_by(id_nom=id_nom).first()
    obj = bibTaxon.as_dict()

    # Ajout des listes
    obj["listes"] = []
    for liste in bibTaxon.listes:
        o = dict(liste.as_dict().items())
        o.update(dict(liste.bib_liste.as_dict().items()))
        obj["listes"].append(o)

    return obj


@adresses.route("/<int:id_nom>", methods=["GET"])
@json_resp
def getOneFull_bibtaxons(id_nom):
    bibTaxon = db.session.query(BibNoms).filter_by(id_nom=id_nom).first()

    obj = bibTaxon.as_dict()

    # Ajout des synonymes
    obj["is_doublon"] = False
    (nbsyn, results) = getBibTaxonSynonymes(id_nom, bibTaxon.cd_nom)
    if nbsyn > 0:
        obj["is_doublon"] = True
        obj["synonymes"] = [i.id_nom for i in results]

    # Ajout des attributs
    obj["attributs"] = []
    for attr in bibTaxon.attributs:
        o = dict(attr.as_dict().items())
        o.update(dict(attr.bib_attribut.as_dict().items()))
        id = o["id_theme"]
        theme = db.session.query(BibThemes).filter_by(id_theme=id).first()
        o["nom_theme"] = theme.as_dict()["nom_theme"]
        obj["attributs"].append(o)

    # Ajout des donnees taxref
    obj["taxref"] = bibTaxon.taxref.as_dict()

    # Ajout des listes
    obj["listes"] = []
    for liste in bibTaxon.listes:
        o = dict(liste.as_dict().items())
        o.update(dict(liste.bib_liste.as_dict().items()))
        obj["listes"].append(o)

    # Ajout des medias
    obj["medias"] = []
    for medium in bibTaxon.medias:
        o = dict(medium.as_dict().items())
        o.update(dict(medium.types.as_dict().items()))
        obj["medias"].append(o)
    return obj


@adresses.route("/", methods=["POST", "PUT"])
@adresses.route("/<int:id_nom>", methods=["POST", "PUT"])
@fnauth.check_auth(3, True)
def insertUpdate_bibtaxons(id_nom=None, id_role=None):
    data = request.get_json(silent=True)

    if id_nom:
        bibTaxon = db.session.query(BibNoms).filter_by(id_nom=id_nom).first()

        bibTaxon.nom_francais = data["nom_francais"] if "nom_francais" in data else None
        bibTaxon.comments = data["comments"] if "comments" in data else None
        action = "UPDATE"
        message = "Taxon mis à jour"
    else:
        bibTaxon = BibNoms(
            cd_nom=data["cd_nom"],
            cd_ref=data["cd_ref"],
            nom_francais=data["nom_francais"] if "nom_francais" in data else None,
            comments=data["comments"] if "comments" in data else None,
        )
        action = "INSERT"
        message = "Taxon ajouté"

    db.session.add(bibTaxon)
    db.session.commit()

    id_nom = bibTaxon.id_nom

    # ###--------------Traitement des attibuts-----------------
    # Suppression des attributs existants
    for bibTaxonAtt in bibTaxon.attributs:
        db.session.delete(bibTaxonAtt)

    db.session.flush()

    if "attributs_values" in data:
        for att in data["attributs_values"]:
            if data["attributs_values"][att] != "" and data["attributs_values"][att] is not None:
                attVal = CorTaxonAttribut(
                    id_attribut=att,
                    cd_ref=bibTaxon.cd_ref,
                    valeur_attribut=data["attributs_values"][att],
                )
                db.session.add(attVal)

    db.session.commit()

    # ###--------------Traitement des listes-----------------
    # Suppression des listes existantes
    for bibTaxonLst in bibTaxon.listes:
        db.session.delete(bibTaxonLst)

    db.session.flush()

    if "listes" in data:
        for lst in data["listes"]:
            listTax = CorNomListe(id_liste=lst["id_liste"], id_nom=id_nom)
            db.session.add(listTax)

    #  Log
    logmanager.log_action(id_role, "bib_nom", id_nom, repr(bibTaxon), action, message)
    db.session.commit()
    return (
        json.dumps({"success": True, "id_nom": id_nom}),
        200,
        {"ContentType": "application/json"},
    )


@adresses.route("/<int:id_nom>", methods=["DELETE"])
@fnauth.check_auth(6, True)
@json_resp
def delete_bibtaxons(id_nom, id_role=None):
    bibTaxon = db.session.query(BibNoms).filter_by(id_nom=id_nom).first()
    db.session.delete(bibTaxon)
    db.session.commit()

    # #Log
    logmanager.log_action(id_role, "bib_nom", id_nom, repr(bibTaxon), "DELETE", "nom supprimé")

    return bibTaxon.as_dict()


# Private functions
def getBibTaxonSynonymes(id_nom, cd_nom):
    q = (
        db.session.query(BibNoms.id_nom)
        .join(BibNoms.taxref)
        .filter(Taxref.cd_ref == func.taxonomie.find_cdref(cd_nom))
        .filter(BibNoms.id_nom != id_nom)
    )
    results = q.all()
    return (q.count(), results)

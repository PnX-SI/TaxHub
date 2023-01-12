from warnings import warn

from flask import abort, jsonify, Blueprint, request
from sqlalchemy import distinct, desc, func, and_
from sqlalchemy.orm.exc import NoResultFound


from ..utils.utilssqlalchemy import json_resp, serializeQuery, serializeQueryOneResult
from .models import (
    Taxref,
    BibNoms,
    VMTaxrefListForautocomplete,
    BibTaxrefHabitats,
    BibTaxrefRangs,
    BibTaxrefStatus,
    TaxrefProtectionArticles,
    VMTaxrefHierarchie,
    VTaxrefHierarchieBibtaxons,
    BibTaxrefLR,
    BibTaxrefHabitats,
    CorNomListe,
    BibListes,
)

from .repositories import BdcStatusRepository

try:
    from urllib.parse import unquote
except ImportError:
    from urllib import unquote

from . import db

adresses = Blueprint("taxref", __name__)


@adresses.route("/", methods=["GET"])
@json_resp
def getTaxrefList():
    return genericTaxrefList(False, request.args)


@adresses.route("/bibnoms/", methods=["GET"])
@json_resp
def getTaxrefBibtaxonList():
    return genericTaxrefList(True, request.args)


@adresses.route("/search/<field>/<ilike>", methods=["GET"])
def getSearchInField(field, ilike):
    """.. http:get:: /taxref/search/(str:field)/(str:ilike)
    .. :quickref: Taxref;

    Retourne les 20 premiers résultat de la table "taxref" pour une
    requête sur le champ `field` avec ILIKE et la valeur `ilike` fournie.
    L'algorithme Trigramme est utilisé pour établir la correspondance.

    :query fields: Permet de récupérer des champs suplémentaire de la
        table "taxref" dans la réponse. Séparer les noms des champs par
        des virgules.
    :query is_inbibnom: Ajoute une jointure sur la table "bib_noms".
    :query add_rank: Ajoute une jointure sur la table "bib_taxref_rangs"
        et la colonne nom_rang aux résultats.
    :query rank_limit: Retourne seulement les taxons dont le rang est
        supérieur ou égal au rang donné. Le rang passé doit être une
        valeur de la colonne "id_rang" de la table "bib_taxref_rangs".

    :statuscode 200: Tableau de dictionnaires correspondant aux résultats
        de la recherche dans la table "taxref".
    :statuscode 500: Aucun rang ne correspond à la valeur fournie.
                     Aucune colonne ne correspond à la valeur fournie.
    """
    taxrefColumns = Taxref.__table__.columns
    if field in taxrefColumns:
        value = unquote(ilike)
        value = value.replace(" ", "%")
        column = taxrefColumns[field]
        q = (
            db.session.query(
                column,
                Taxref.cd_nom,
                Taxref.cd_ref,
                func.similarity(column, value).label("idx_trgm"),
            )
            .filter(column.ilike("%" + value + "%"))
            .order_by(desc("idx_trgm"))
        )

        if request.args.get("fields"):
            fields = request.args["fields"].split(",")
            for field in fields:
                if field in taxrefColumns:
                    column = taxrefColumns[field]
                    q = q.add_columns(column)
                else:
                    msg = f"No column found in Taxref for {field}"
                    return jsonify(msg), 500

        if request.args.get("is_inbibnoms"):
            q = q.join(BibNoms, BibNoms.cd_nom == Taxref.cd_nom)
        join_on_bib_rang = False
        if request.args.get("add_rank"):
            q = q.join(BibTaxrefRangs, Taxref.id_rang == BibTaxrefRangs.id_rang)
            q = q.add_columns(BibTaxrefRangs.nom_rang)
            join_on_bib_rang = True

        if "rank_limit" in request.args:
            if not join_on_bib_rang:
                q = q.join(BibTaxrefRangs, Taxref.id_rang == BibTaxrefRangs.id_rang)
            try:
                sub_q_id_rang = (
                    db.session.query(BibTaxrefRangs.tri_rang)
                    .filter(BibTaxrefRangs.id_rang == request.args["rank_limit"])
                    .one()
                )
            except NoResultFound:
                return (
                    jsonify("No rank found for {}".format(request.args["rank_limit"])),
                    500,
                )
            q = q.filter(BibTaxrefRangs.tri_rang <= sub_q_id_rang[0])

        results = q.limit(20).all()
        return jsonify(serializeQuery(results, q.column_descriptions))
    else:
        jsonify("No column found in Taxref for {}".format(field)), 500


@adresses.route("/<int(signed=True):id>", methods=["GET"])
def getTaxrefDetail(id):
    dfCdNom = Taxref.__table__.columns["cd_nom"]

    q = (
        db.session.query(
            Taxref.cd_nom,
            Taxref.cd_ref,
            Taxref.regne,
            Taxref.phylum,
            Taxref.classe,
            Taxref.ordre,
            Taxref.famille,
            Taxref.cd_taxsup,
            Taxref.cd_sup,
            Taxref.cd_taxsup,
            Taxref.nom_complet,
            Taxref.nom_valide,
            Taxref.nom_vern,
            Taxref.group1_inpn,
            Taxref.group2_inpn,
            Taxref.id_rang,
            BibTaxrefRangs.nom_rang,
            BibTaxrefStatus.nom_statut,
            BibTaxrefHabitats.nom_habitat,
        )
        .outerjoin(BibTaxrefHabitats, BibTaxrefHabitats.id_habitat == Taxref.id_habitat)
        .outerjoin(BibTaxrefStatus, BibTaxrefStatus.id_statut == Taxref.id_statut)
        .outerjoin(BibTaxrefRangs, BibTaxrefRangs.id_rang == Taxref.id_rang)
        .filter(dfCdNom == id)
    )

    results = q.one()

    taxon = serializeQueryOneResult(results, q.column_descriptions)

    qsynonymes = db.session.query(Taxref.cd_nom, Taxref.nom_complet).filter(
        Taxref.cd_ref == results.cd_ref
    )

    synonymes = qsynonymes.all()

    taxon["synonymes"] = [
        {c: getattr(row, c) for c in ["cd_nom", "nom_complet"] if getattr(row, c) is not None}
        for row in synonymes
    ]

    # Pour des questions de retrocompatibilité avec taxref
    #  Les anciens statuts sont toujours remonté
    #  TODO delete après refonte fiche taxon de GN2
    stprotection = db.engine.execute(
        (
            """SELECT DISTINCT pr_a.*
            FROM taxonomie.taxref_protection_articles pr_a
            JOIN (SELECT * FROM taxonomie.taxref_protection_especes pr_sp
            WHERE taxonomie.find_cdref(pr_sp.cd_nom) = {cd_ref}) pr_sp
            ON pr_a.cd_protection = pr_sp.cd_protection"""
        ).format(cd_ref=results.cd_ref)
    )

    taxon["statuts_protection"] = [
        {c.name: getattr(r, c.name) for c in TaxrefProtectionArticles.__table__.columns}
        for r in stprotection
    ]

    areas = None
    if request.args.get("areas_status"):
        areas = request.args["areas_status"].split(",")

    areas_code = None
    if request.args.get("areas_code_status"):
        areas_code = request.args["areas_code_status"].split(",")

    taxon["status"] = BdcStatusRepository().get_status(
        cd_ref=results.cd_ref, areas=areas, areas_code=areas_code, type_statut=None, format=True
    )

    return jsonify(taxon)


@adresses.route("/distinct/<field>", methods=["GET"])
def getDistinctField(field):
    taxrefColumns = Taxref.__table__.columns
    q = db.session.query(taxrefColumns[field]).distinct(taxrefColumns[field])

    limit = request.args.get("limit", 100, int)

    for param in request.args:
        if param in taxrefColumns:
            col = getattr(taxrefColumns, param)
            q = q.filter(col == request.args[param])
        elif param == "ilike":
            q = q.filter(taxrefColumns[field].ilike(request.args[param] + "%"))

    results = q.limit(limit).all()
    return jsonify(serializeQuery(results, q.column_descriptions))


@adresses.route("/hierarchie/<rang>", methods=["GET"])
@json_resp
def getTaxrefHierarchie(rang):
    results = genericHierarchieSelect(VMTaxrefHierarchie, rang, request.args)
    return [r.as_dict() for r in results]


@adresses.route("/hierarchiebibtaxons/<rang>", methods=["GET"])
@json_resp
def getTaxrefHierarchieBibNoms(rang):
    results = genericHierarchieSelect(VTaxrefHierarchieBibtaxons, rang, request.args)
    return [r.as_dict() for r in results]


def genericTaxrefList(inBibtaxon, parameters):
    taxrefColumns = Taxref.__table__.columns
    bibNomsColumns = BibNoms.__table__.columns
    q = db.session.query(Taxref, BibNoms.id_nom)

    qcount = q.outerjoin(BibNoms, BibNoms.cd_nom == Taxref.cd_nom)

    nbResultsWithoutFilter = qcount.count()

    if inBibtaxon is True:
        q = q.join(BibNoms, BibNoms.cd_nom == Taxref.cd_nom)
    else:
        q = q.outerjoin(BibNoms, BibNoms.cd_nom == Taxref.cd_nom)

    # Traitement des parametres
    limit = parameters.get("limit", 20, int)
    page = parameters.get("page", 1, int)

    for param in parameters:
        if param in taxrefColumns and parameters[param] != "":
            col = getattr(taxrefColumns, param)
            q = q.filter(col == parameters[param])
        elif param == "is_ref" and parameters[param] == "true":
            q = q.filter(Taxref.cd_nom == Taxref.cd_ref)
        elif param == "ilike":
            q = q.filter(Taxref.lb_nom.ilike(parameters[param] + "%"))
        elif param == "is_inbibtaxons" and parameters[param] == "true":
            q = q.filter(bibNomsColumns.cd_nom.isnot(None))
        elif param.split("-")[0] == "ilike":
            value = unquote(parameters[param])
            col = str(param.split("-")[1])
            q = q.filter(taxrefColumns[col].ilike(value + "%"))

    nbResults = q.count()

    # Order by
    if "orderby" in parameters:
        if parameters["orderby"] in taxrefColumns:
            orderCol = getattr(taxrefColumns, parameters["orderby"])
        else:
            orderCol = None
        if "order" in parameters:
            if parameters["order"] == "desc":
                orderCol = orderCol.desc()
        q = q.order_by(orderCol)

    results = q.paginate(page=page, per_page=limit, error_out=False)
    return {
        "items": [dict(d.Taxref.as_dict(), **{"id_nom": d.id_nom}) for d in results.items],
        "total": nbResultsWithoutFilter,
        "total_filtered": nbResults,
        "limit": limit,
        "page": page,
    }


def genericHierarchieSelect(tableHierarchy, rang, parameters):

    dfRang = tableHierarchy.__table__.columns["id_rang"]
    q = db.session.query(tableHierarchy).filter(tableHierarchy.id_rang == rang)

    limit = parameters.get("limit", 100, int)

    for param in parameters:
        if param in tableHierarchy.__table__.columns:
            col = getattr(tableHierarchy.__table__.columns, param)
            q = q.filter(col == parameters[param])
        elif param == "ilike":
            q = q.filter(tableHierarchy.__table__.columns.lb_nom.ilike(parameters[param] + "%"))

    results = q.limit(limit).all()
    return results


@adresses.route("/regnewithgroupe2", methods=["GET"])
@json_resp
def get_regneGroup2Inpn_taxref():
    """
    Retourne la liste des règne et groupe 2
        défini par taxref de façon hiérarchique
    formatage : {'regne1':['grp1', 'grp2'], 'regne2':['grp3', 'grp4']}
    """
    q = (
        db.session.query(Taxref.regne, Taxref.group2_inpn)
        .distinct(Taxref.regne, Taxref.group2_inpn)
        .filter(Taxref.regne != None)
        .filter(Taxref.group2_inpn != None)
    )
    data = q.all()
    results = {"": [""]}
    for d in data:
        if d.regne in results:
            results[d.regne].append(d.group2_inpn)
        else:
            results[d.regne] = ["", d.group2_inpn]
    return results


@adresses.route("/allnamebylist/<string:code_liste>", methods=["GET"])
@adresses.route("/allnamebylist", methods=["GET"])
@json_resp
def get_AllTaxrefNameByListe(code_liste=None):
    """
    Route utilisée pour les autocompletes
    Si le paramètre search_name est passé, la requête SQL utilise l'algorithme
    des trigrames pour améliorer la pertinence des résultats
    Route utilisé par le mobile pour remonter la liste des taxons
    params URL:
        - code_liste : code de la liste (si id liste est null ou = à -1 on ne prend pas de liste)
    params GET (facultatifs):
        - search_name : nom recherché. Recherche basé sur la fonction
            ilike de sql avec un remplacement des espaces par %
        - regne : filtre sur le regne INPN
        - group2_inpn : filtre sur le groupe 2 de l'INPN
        - limit: nombre de résultat
        - offset: numéro de la page
    """
    # Traitement des cas ou code_liste = -1
    id_liste = None
    try:
        if code_liste:
            code_liste_to_int = int(code_liste)
            if code_liste_to_int == -1:
                id_liste = -1
        else:
            id_liste = -1
    except ValueError:
        # le code liste n'est pas un entier
        #   mais une chaine de caractère c-a-d bien un code
        pass

    # Get id_liste
    try:
        # S'il y a une id_liste elle à forcement la valeur -1
        #   c-a-d pas de liste
        if not id_liste:
            q = (
                db.session.query(BibListes.id_liste).filter(BibListes.code_liste == code_liste)
            ).one()
            id_liste = q[0]
    except NoResultFound:
        return (
            {"success": False, "message": "Code liste '{}' inexistant".format(code_liste)},
            400,
        )

    q = db.session.query(VMTaxrefListForautocomplete)
    if id_liste and id_liste != -1:
        q = q.join(BibNoms, BibNoms.cd_nom == VMTaxrefListForautocomplete.cd_nom).join(
            CorNomListe,
            and_(CorNomListe.id_nom == BibNoms.id_nom, CorNomListe.id_liste == id_liste),
        )

    search_name = request.args.get("search_name")
    if search_name:
        q = q.add_columns(
            func.similarity(VMTaxrefListForautocomplete.search_name, search_name).label("idx_trgm")
        )
        search_name = search_name.replace(" ", "%")
        q = q.filter(
            func.unaccent(VMTaxrefListForautocomplete.search_name).ilike(
                func.unaccent("%" + search_name + "%")
            )
        ).order_by(desc("idx_trgm"))
        q = q.order_by(
            desc(VMTaxrefListForautocomplete.cd_nom == VMTaxrefListForautocomplete.cd_ref)
        )
    # if no search name no need to order by trigram or cd_nom=cdref - order by PK (use for mobile app)
    else:
        q = q.order_by(VMTaxrefListForautocomplete.gid)

    regne = request.args.get("regne")
    if regne:
        q = q.filter(VMTaxrefListForautocomplete.regne == regne)

    group2_inpn = request.args.get("group2_inpn")
    if group2_inpn:
        q = q.filter(VMTaxrefListForautocomplete.group2_inpn == group2_inpn)

    limit = request.args.get("limit", 20, int)
    page = request.args.get("page", 1, int)
    if "offset" in request.args:
        warn(
            "offset is deprecated, please use page for pagination (start at 1)", DeprecationWarning
        )
        page = (int(request.args["offset"]) / limit) + 1
    data = q.paginate(page=page, per_page=limit, error_out=False)

    if search_name:
        return [d[0].as_dict() for d in data.items]
    else:
        return [d.as_dict() for d in data.items]


@adresses.route("/bib_lr", methods=["GET"])
@json_resp
def get_bib_lr():
    data = db.session.query(BibTaxrefLR).all()
    formated_data = []
    for d in data:
        d = d.as_dict()
        d["nom_categorie_lr"] = d["nom_categorie_lr"] + " - " + d["id_categorie_france"]
        formated_data.append(d)
    return formated_data


@adresses.route("/bib_habitats", methods=["GET"])
@json_resp
def get_bib_hab():
    data = db.session.query(BibTaxrefHabitats).all()
    return [d.as_dict() for d in data]

from warnings import warn

from flask import abort, jsonify, Blueprint, request
from sqlalchemy import desc, func, and_, select
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound
from utils_flask_sqla.response import json_resp
from utils_flask_sqla.generic import serializeQuery

from apptax.taxonomie.models import (
    Taxref,
    VMTaxrefListForautocomplete,
    BibTaxrefHabitats,
    BibTaxrefRangs,
    BibTaxrefHabitats,
    BibListes,
    TMetaTaxref,
    CorTaxonAttribut,
)

from .repositories import BdcStatusRepository, TaxrefTreeRepository

try:
    from urllib.parse import unquote
except ImportError:
    from urllib import unquote

from apptax.taxonomie.schemas import TaxrefSchema
from apptax.utils.utilssqlalchemy import build_query_order
from . import db

adresses = Blueprint("taxref", __name__)


def get_joinedload_when_attributs(fields):
    joinedload_when_attributs = []
    if [i for i in fields if i.startswith("attributs.bib_attribut")]:
        joinedload_when_attributs = [
            joinedload(Taxref.attributs).options(joinedload(CorTaxonAttribut.bib_attribut))
        ]
    return joinedload_when_attributs


@adresses.route("/version", methods=["GET"])
@json_resp
def get_taxref_version():
    """
    La table TMetaTaxref contient la liste des référentiels contenu dans la table taxref
    Cette route renvoie le dernier référentiel qui a été MAJ
    (utilisé pour le mobile pour retélécharger le référentiel lorsque celui ci à changé ou en MAJ)
    """
    taxref_version = TMetaTaxref.query.order_by(TMetaTaxref.update_date.desc()).first()
    if not taxref_version:
        return {"msg": "Table t_meta_taxref non peuplée"}, 500
    return taxref_version.as_dict()


@adresses.route("/search/<field>/<ilike>", methods=["GET"])
def get_search_in_field(field, ilike):
    """.. http:get:: /taxref/search/(str:field)/(str:ilike)
    .. :quickref: Taxref;

    Retourne les 20 premiers résultats de la table "taxref" pour une
    requête sur le champ `field` avec ILIKE et la valeur `ilike` fournie.
    L'algorithme Trigramme est utilisé pour établir la correspondance.

    :query fields: Permet de récupérer des champs suplémentaires de la
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


@adresses.route("/", methods=["GET", "POST"])
def get_taxref_list():
    """
    Retrieve a list of elements from the 'taxref' table.

    Route Parameters
    ----------
    limit : int, optional
        Number of results. Default is 20.
    offset : int, optional
        Page number. Default is 1.
    fields : str, optional
        List of fields to return. Default is an empty string.
    id_liste : list, optional
        List of lists to filter. Default is None. Comma separated if multiple : id_list=100,101
    is_ref : bool, optional
        Filter on 'cd_nom' = 'cd_ref'. Default is None.
    nom_colonne_taxref : str, optional
        Exact filter on a column. Default is None.
    ilike-nom_colonne_taxref : str, optional
        Ilike filter on a column. Default is None.

    Returns
    -------
    dict
        A dictionary containing the results.
    """
    limit = request.values.get("limit", 20, int)
    page = request.values.get("page", 1, int)
    id_liste = None
    cd_nom = None

    if "id_liste" in request.values:
        id_liste = (
            request.values.get("id_liste").split(",") if request.values.get("id_liste") else None
        )
    if "cd_nom" in request.values:
        cd_nom = request.values.get("cd_nom").split(",") if request.values.get("cd_nom") else None

    fields = request.values.get("fields", type=str, default=[])
    parameters = request.values.to_dict()
    parameters["cd_nom"] = cd_nom

    dump_options = {}
    if fields:
        fields = fields.split(",")
        dump_options["only"] = fields

    count_total = db.session.scalar(
        db.select(func.count("*")).select_from(Taxref),
    )

    joinedload_when_attributs = get_joinedload_when_attributs(fields=fields)
    query = Taxref.joined_load(fields).options(*joinedload_when_attributs)
    query = Taxref.where_params(parameters, query=query)

    if id_liste and "-1" not in id_liste:
        query = Taxref.where_id_liste(id_liste, query=query)
    count_filter = db.session.scalar(
        db.select(func.count()).select_from(
            Taxref.where_params(parameters, query=query),
        ),
    )

    query = build_query_order(Taxref, query, parameters, {"orderby": "cd_nom"})
    data = db.paginate(select=query, page=page, per_page=limit, error_out=False)

    return {
        "items": TaxrefSchema(**dump_options).dump(data.items, many=True),
        "total": count_total,
        "total_filtered": count_filter,
        "limit": limit,
        "page": page,
    }


@adresses.route("/<int(signed=True):cd_nom>", methods=["GET"])
def get_taxref_detail(cd_nom):
    fields = request.values.get("fields", type=str, default=[])

    dump_options = {}

    if fields:
        fields = fields.split(",")
    else:
        fields = [
            "attributs",
            "listes",
            "medias",
            "status",
            "synonymes.cd_nom",
            "synonymes.nom_complet",
        ]

    firstlevel_fields = [rel.split(".")[0] for rel in fields]

    # Pop status traité par ailleurs pour qu'ils s'affichent de façon hiérachique
    #  TODO : A normaliser
    join_relationship = [f for f in firstlevel_fields if not f == "status"]

    fields = [f for f in fields if not f.split(".")[0] == "status"]

    joinedload_when_attributs = get_joinedload_when_attributs(fields=fields)
    query = (
        Taxref.joined_load(join_relationship)
        .options(*joinedload_when_attributs)
        .where(Taxref.cd_nom == cd_nom)
    )
    results = db.session.scalars(query).unique().one_or_none()
    if not results:
        abort(404)

    dump_options["only"] = fields
    taxon = TaxrefSchema(**dump_options).dump(results, many=False)

    # Bidouille pour avoir les nom_rang, ....
    if "id_rang" in taxon:
        taxon["nom_rang"] = taxon["id_rang"]
    if "id_habitat" in taxon:
        taxon["nom_habitat"] = str(taxon["id_habitat"])
    if "id_statut" in taxon:
        taxon["nom_statut"] = str(taxon["id_statut"])

    if "status" in firstlevel_fields:
        areas = None
        if request.args.get("areas_status"):
            areas = request.args["areas_status"].split(",")

        areas_code = None
        if request.args.get("areas_code_status"):
            areas_code = request.args["areas_code_status"].split(",")

        taxon["status"] = BdcStatusRepository.get_status(
            cd_ref=results.cd_ref,
            areas=areas,
            areas_code=areas_code,
            type_statut=None,
            format=True,
        )

    return jsonify(taxon)


@adresses.route("/<int(signed=True):cd_nom>/parents", methods=["GET"])
def get_taxref_detail_parents(cd_nom):
    has_linnaean_levels_option = request.values.get("linnaean", False, bool)
    if has_linnaean_levels_option:
        parents = TaxrefTreeRepository.get_linnaean_parents(cd_nom)
    else:
        parents = TaxrefTreeRepository.get_parents(cd_nom)

    return jsonify({"parents": parents})


@adresses.route("/regnewithgroupe2", methods=["GET"])
@json_resp
def get_regne_group2_inpn_taxref():
    """
    Retourne la liste des règnes et groupes 2
        définis par Taxref de façon hiérarchique
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


@adresses.route("/groupe3_inpn", methods=["GET"])
@json_resp
def get_group3_inpn_taxref():
    """
    Retourne la liste des groupes 3 inpn
    """
    data = (
        db.session.query(Taxref.group3_inpn)
        .distinct(Taxref.group3_inpn)
        .filter(Taxref.group3_inpn != None)
    ).all()
    return [d[0] for d in data]


@adresses.route("/allnamebylist/<int(signed=True):id_liste>", methods=["GET"])
@adresses.route("/allnamebylist", methods=["GET"], defaults={"id_liste": -1})
@json_resp
def get_all_taxref_name_by_liste(id_liste):
    """
    Route utilisée pour les autocompletes
    Si le paramètre search_name est passé, la requête SQL utilise l'algorithme
    des trigrammes pour améliorer la pertinence des résultats
    Route utilisée par le mobile pour remonter la liste des taxons
    params URL:
        - id_liste : identifiant de la liste (si id_liste est null ou = à -1 on ne prend pas de liste)
    params GET (facultatifs):
        - code_liste : code de la liste à filtrer, n'est pris en compte que si aucune liste est spécifiée
        - search_name : nom recherché. Recherche basée sur la fonction
            ilike de SQL avec un remplacement des espaces par %
        - regne : filtre sur le règne INPN
        - group2_inpn : filtre sur le groupe 2 de l'INPN
        - limit: nombre de résultats
        - offset: numéro de la page
    """
    if id_liste == -1:
        id_liste = None

    q = select(VMTaxrefListForautocomplete)
    requested_id_list = None
    if id_liste:
        requested_id_list = id_liste
    elif request.args.get("code_liste"):
        requested_id_list = (
            db.session.execute(
                select(BibListes.id_liste).filter_by(code_liste=request.args.get("code_liste"))
            )
        ).scalar()
    if requested_id_list:
        q = q.join(
            BibListes,
            and_(
                BibListes.noms.any(cd_nom=VMTaxrefListForautocomplete.cd_nom),
                BibListes.id_liste == requested_id_list,
            ),
        )

    search_name = request.args.get("search_name")
    if search_name:
        q = q.add_columns(
            func.similarity(VMTaxrefListForautocomplete.unaccent_search_name, search_name).label(
                "idx_trgm"
            )
        )
        search_name = search_name.replace(" ", "%")
        q = q.filter(
            VMTaxrefListForautocomplete.unaccent_search_name.ilike(
                func.unaccent("%" + search_name + "%")
            )
        ).order_by(desc("idx_trgm"))
        q = q.order_by(
            desc(VMTaxrefListForautocomplete.cd_nom == VMTaxrefListForautocomplete.cd_ref)
        )
    # if no search name, no need to order by trigram or cd_nom=cdref - order by PK (used for mobile app)
    else:
        q = q.order_by(VMTaxrefListForautocomplete.gid)

    regne = request.args.get("regne")
    if regne:
        q = q.filter(VMTaxrefListForautocomplete.regne == regne)

    group2_inpn = request.args.get("group2_inpn")
    if group2_inpn:
        q = q.filter(VMTaxrefListForautocomplete.group2_inpn == group2_inpn)

    group3_inpn = request.args.get("group3_inpn")
    if group3_inpn:
        q = q.filter(VMTaxrefListForautocomplete.group3_inpn == group3_inpn)

    limit = request.args.get("limit", 20, int)
    page = request.args.get("page", 1, int)
    if "offset" in request.args:
        warn(
            "offset is deprecated, please use page for pagination (start at 1)", DeprecationWarning
        )
        page = (int(request.args["offset"]) / limit) + 1
    data = db.paginate(q, page=page, per_page=limit, error_out=False)

    return [d.as_dict(exclude=["unaccent_search_name"]) for d in data.items]


@adresses.route("/bib_habitats", methods=["GET"])
@json_resp
def get_bib_hab():
    data = db.session.query(BibTaxrefHabitats).all()
    return [d.as_dict() for d in data]

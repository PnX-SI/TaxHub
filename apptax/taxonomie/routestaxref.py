from flask import jsonify, Blueprint, request
from sqlalchemy import distinct, desc, func

from ..utils.utilssqlalchemy import (
    json_resp, serializeQuery, serializeQueryOneResult
)
from .models import (
    Taxref, BibNoms, VMTaxrefListForautocomplete, BibTaxrefHabitats,
    BibTaxrefRangs, BibTaxrefStatus, TaxrefProtectionArticles,
    VMTaxrefHierarchie, VTaxrefHierarchieBibtaxons, BibTaxrefLR, BibTaxrefHabitats
)

try:
    from urllib.parse import unquote
except ImportError:
    from urllib import unquote

from . import db

adresses = Blueprint('taxref', __name__)


@adresses.route('/', methods=['GET'])
@json_resp
def getTaxrefList():
    return genericTaxrefList(False, request.args)


@adresses.route('/bibnoms/', methods=['GET'])
@json_resp
def getTaxrefBibtaxonList():
    return genericTaxrefList(True, request.args)


@adresses.route('/search/<field>/<ilike>', methods=['GET'])
def getSearchInField(field, ilike):
    taxrefColumns = Taxref.__table__.columns

    if field in taxrefColumns:
        value = unquote(ilike)
        column = taxrefColumns[field]
        q = db.session.query(column)\
            .filter(column.ilike(value+'%'))\
            .order_by(column)
        if request.args.get('is_inbibnoms'):
            q = q.join(BibNoms, BibNoms.cd_nom == Taxref.cd_nom)
        results = q.limit(20).all()
        return jsonify(serializeQuery(results, q.column_descriptions))
    else:
        return 'false'


@adresses.route('/<int:id>', methods=['GET'])
def getTaxrefDetail(id):
    dfCdNom = Taxref.__table__.columns['cd_nom']

    q = db.session.query(
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
        BibTaxrefHabitats.nom_habitat
    )\
    .outerjoin(BibTaxrefHabitats, BibTaxrefHabitats.id_habitat == Taxref.id_habitat)\
    .outerjoin(BibTaxrefStatus, BibTaxrefStatus.id_statut == Taxref.id_statut)\
    .outerjoin(BibTaxrefRangs, BibTaxrefRangs.id_rang == Taxref.id_rang)\
    .filter(dfCdNom == id)

    results = q.one()

    taxon = serializeQueryOneResult(results, q.column_descriptions)

    qsynonymes = db.session.query(
                    Taxref.cd_nom,
                    Taxref.nom_complet
                ).filter(Taxref.cd_ref == results.cd_ref)

    synonymes = qsynonymes.all()

    taxon['synonymes'] = [
        {
            c: getattr(row, c) for c in ['cd_nom', 'nom_complet']
            if getattr(row, c) is not None
        }
        for row in synonymes
    ]
    stprotection = db.engine.execute(
        (
            """SELECT DISTINCT pr_a.*
            FROM taxonomie.taxref_protection_articles pr_a
            JOIN (SELECT * FROM taxonomie.taxref_protection_especes pr_sp
            WHERE taxonomie.find_cdref(pr_sp.cd_nom) = {cd_ref}) pr_sp
            ON pr_a.cd_protection = pr_sp.cd_protection"""
        ).format(cd_ref =results.cd_ref)
    )

    taxon['statuts_protection'] = [
        {
            c.name: getattr(r, c.name)
            for c in TaxrefProtectionArticles.__table__.columns
        }
        for r in stprotection
    ]

    return jsonify(taxon)


@adresses.route('/distinct/<field>', methods=['GET'])
def getDistinctField(field):
    taxrefColumns = Taxref.__table__.columns
    q = db.session.query(taxrefColumns[field]).distinct(taxrefColumns[field])

    limit = request.args.get('limit') if request.args.get('limit') else 100

    for param in request.args:
        if param in taxrefColumns:
            col = getattr(taxrefColumns, param)
            q = q.filter(col == request.args[param])
        elif param == 'ilike':
            q = q.filter(taxrefColumns[field].ilike(request.args[param]+'%'))

    results = q.limit(limit).all()
    return jsonify(serializeQuery(results, q.column_descriptions))


@adresses.route('/hierarchie/<rang>', methods=['GET'])
@json_resp
def getTaxrefHierarchie(rang):
    results = genericHierarchieSelect(VMTaxrefHierarchie, rang, request.args)
    return [r.as_dict() for r in results]


@adresses.route('/hierarchiebibtaxons/<rang>', methods=['GET'])
@json_resp
def getTaxrefHierarchieBibNoms(rang):
    results = genericHierarchieSelect(
        VTaxrefHierarchieBibtaxons,
        rang,
        request.args
    )
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
    limit = int(parameters.get('limit')) if parameters.get('limit') else 100
    page = int(parameters.get('page'))-1 if parameters.get('page') else 0

    for param in parameters:
        if param in taxrefColumns and parameters[param] != '':
            col = getattr(taxrefColumns, param)
            q = q.filter(col == parameters[param])
        elif param == 'is_ref' and parameters[param] == 'true':
            q = q.filter(Taxref.cd_nom == Taxref.cd_ref)
        elif param == 'ilike':
            q = q.filter(Taxref.lb_nom.ilike(parameters[param]+'%'))
        elif param == 'is_inbibtaxons' and parameters[param] == 'true':
            q = q.filter(bibNomsColumns.cd_nom.isnot(None))
        elif param.split('-')[0] == 'ilike':
            value = unquote(parameters[param])
            col = str(param.split('-')[1])
            q = q.filter(taxrefColumns[col].ilike(value+'%'))

    nbResults = q.count()

    # Order by
    if 'orderby' in parameters:
        if parameters['orderby'] in taxrefColumns:
            orderCol = getattr(taxrefColumns, parameters['orderby'])
        else:
            orderCol = None
        if 'order' in parameters:
            if (parameters['order'] == 'desc'):
                orderCol = orderCol.desc()
        q = q.order_by(orderCol)

    results = q.limit(limit).offset(page*limit).all()
    return {
        "items": [
            dict(d.Taxref.as_dict(), **{'id_nom': d.id_nom})
            for d in results
        ],
        "total": nbResultsWithoutFilter,
        "total_filtered": nbResults,
        "limit": limit,
        "page": page
    }


def genericHierarchieSelect(tableHierarchy, rang, parameters):

    dfRang = tableHierarchy.__table__.columns['id_rang']
    q = db.session.query(tableHierarchy)\
        .filter(tableHierarchy.id_rang == rang)

    limit = parameters.get('limit') if parameters.get('limit') else 100

    for param in parameters:
        if param in tableHierarchy.__table__.columns:
            col = getattr(tableHierarchy.__table__.columns, param)
            q = q.filter(col == parameters[param])
        elif param == 'ilike':
            q = q.filter(
                tableHierarchy.__table__.columns
                .lb_nom.ilike(parameters[param]+'%')
            )

    results = q.limit(limit).all()
    return results


@adresses.route('/regnewithgroupe2', methods=['GET'])
@json_resp
def get_regneGroup2Inpn_taxref():
    """
        Retourne la liste des règne et groupe 2
            défini par taxref de façon hiérarchique
        formatage : {'regne1':['grp1', 'grp2'], 'regne2':['grp3', 'grp4']}
    """
    q = db.session.query(Taxref.regne, Taxref.group2_inpn)\
        .distinct(Taxref.regne, Taxref.group2_inpn)\
        .filter(Taxref.regne != None)\
        .filter(Taxref.group2_inpn != None)
    data = q.all()
    results = {'': ['']}
    for d in data:
        if d.regne in results:
            results[d.regne].append(d.group2_inpn)
        else:
            results[d.regne] = ['', d.group2_inpn]
    return results


@adresses.route('/allnamebylist/<int:id_liste>', methods=['GET'])
@json_resp
def get_AllTaxrefNameByListe(id_liste):
    """
        Route utilisée pour les autocompletes
        Si le paramètre search_name est passé, la requête SQL utilise l'algorithme 
        des trigrames pour améliorer la pertinence des résultats
        params URL:
            - id_liste : identifiant de la liste
        params GET:
            - search_name : nom recherché. Recherche basé sur la fonction
                ilike de sql avec un remplacement des espaces par %
            - regne : filtre sur le regne INPN
            - group2_inpn : filtre sur le groupe 2 de l'INPN
    """

    q = db.session.query(
        VMTaxrefListForautocomplete
    ).filter(
        VMTaxrefListForautocomplete.id_liste == id_liste
    )
    search_name = request.args.get('search_name')
    if search_name:
        q = db.session.query(
                VMTaxrefListForautocomplete,
                func.similarity(
                    VMTaxrefListForautocomplete.search_name, search_name
                ).label('idx_trgm')
            ).filter(
                VMTaxrefListForautocomplete.id_liste == id_liste
            )
        search_name = search_name.replace(' ', '%')
        q = q.filter(
            VMTaxrefListForautocomplete.search_name.ilike('%'+search_name+"%")
        ).order_by(desc('idx_trgm'))

    regne = request.args.get('regne')
    if regne:
        q = q.filter(VMTaxrefListForautocomplete.regne == regne)

    group2_inpn = request.args.get('group2_inpn')
    if group2_inpn:
        q = q.filter(VMTaxrefListForautocomplete.group2_inpn == group2_inpn)

    q = q.order_by(desc(
        VMTaxrefListForautocomplete.cd_nom == 
        VMTaxrefListForautocomplete.cd_ref
    ))
    limit = request.args.get('limit', 20)
    data = q.limit(limit).all()
    if search_name:
        return [d[0].as_dict() for d in data]
    return [d.as_dict() for d in data]



@adresses.route('/bib_lr', methods=['GET'])
@json_resp
def get_bib_lr():
    data = db.session.query(BibTaxrefLR).all()
    formated_data = []
    for d in data:
        d = d.as_dict()
        d['nom_categorie_lr'] = d['nom_categorie_lr'] + ' - ' + d['id_categorie_france']
        formated_data.append(d)
    return formated_data

@adresses.route('/bib_habitats', methods=['GET'])
@json_resp
def get_bib_hab():
    data = db.session.query(BibTaxrefHabitats).all()
    return [d.as_dict() for d in data]
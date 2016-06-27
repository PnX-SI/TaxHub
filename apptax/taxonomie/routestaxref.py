#coding: utf8
from flask import jsonify, Blueprint

from flask import request

from server import db

from ..utils.utilssqlalchemy import json_resp, GenericTable, serializeQuery

from sqlalchemy import select

adresses = Blueprint('taxref', __name__)

@adresses.route('/', methods=['GET'])
def getTaxrefList():
    return genericTaxrefList(False, request.args)

@adresses.route('/bibtaxons/', methods=['GET'])
def getTaxrefBibtaxonList():
    return genericTaxrefList(True, request.args)


@adresses.route('/<int:id>', methods=['GET'])
def getTaxrefDetail(id):
    tableTaxref = GenericTable('taxonomie.taxref', 'taxonomie')
    tableBibTaxrefHabitats = GenericTable('taxonomie.bib_taxref_habitats', 'taxonomie')
    tableBibTaxrefRangs = GenericTable('taxonomie.bib_taxref_rangs', 'taxonomie')
    tableBibTaxrefStatuts = GenericTable('taxonomie.bib_taxref_statuts', 'taxonomie')
    tableStProtection = GenericTable('taxonomie.taxref_protection_articles', 'taxonomie')

    dfCdNom = tableTaxref.tableDef.columns['cd_nom']
    q = db.session.query(
            tableTaxref.tableDef,
            tableBibTaxrefRangs.tableDef.columns.nom_rang,
            tableBibTaxrefStatuts.tableDef.columns.nom_statut,
            tableBibTaxrefHabitats.tableDef.columns.nom_habitat
        )\
        .join(tableBibTaxrefHabitats.tableDef, tableBibTaxrefHabitats.tableDef.columns.id_habitat==tableTaxref.tableDef.columns.id_habitat)\
        .join(tableBibTaxrefStatuts.tableDef, tableBibTaxrefStatuts.tableDef.columns.id_statut==tableTaxref.tableDef.columns.id_statut)\
        .join(tableBibTaxrefRangs.tableDef, tableBibTaxrefRangs.tableDef.columns.id_rang==tableTaxref.tableDef.columns.id_rang)\
        .filter(dfCdNom == id)

    results = q.one()
    taxon =serializeQueryOneResult( results, q.column_descriptions)

    qsynonymes = db.session.query(
                    tableTaxref.tableDef.columns.cd_nom,
                    tableTaxref.tableDef.columns.nom_complet
                )\
                .filter(tableTaxref.tableDef.columns['cd_ref'] == results.cd_ref)

    synonymes = qsynonymes.all()

    taxon['synonymes'] = [{c : getattr(row, c) for c in  ['cd_nom', 'nom_complet'] if getattr(row, c) != None } for row in synonymes]

    stprotection = db.engine.execute(" \
            SELECT DISTINCT pr_a.*  \
          FROM taxonomie.taxref_protection_articles pr_a \
          JOIN (SELECT * FROM taxonomie.taxref_protection_especes pr_sp  \
          WHERE taxonomie.find_cdref(pr_sp.cd_nom) = %s ) pr_sp \
          ON pr_a.cd_protection = pr_sp.cd_protection \
          WHERE NOT concerne_mon_territoire IS NULL", results.cd_ref)

    taxon['statuts_protection'] = [{c.name: getattr(r, c.name) for c in tableStProtection.tableDef.columns} for r in stprotection]

    return jsonify(taxon)

@adresses.route('/distinct/<field>', methods=['GET'])
def getDistinctField(field):
    tableTaxref = GenericTable('taxonomie.taxref', 'taxonomie')

    dfield = tableTaxref.tableDef.columns[field]
    q = db.session.query(dfield).distinct(dfield)

    limit = request.args.get('limit') if request.args.get('limit') else 100

    for param in request.args:
        if param in tableTaxref.columns:
            col = getattr(tableTaxref.tableDef.columns,param)
            q = q.filter(col == request.args[param])
        elif param == 'ilike':
            q = q.filter(dfield.ilike(request.args[param]+'%'))

    results = q.limit(limit).all()
    return jsonify(serializeQuery(results,q.column_descriptions))

@adresses.route('/hierarchie/<rang>', methods=['GET'])
@json_resp
def getTaxrefHierarchie(rang):
    print(genericHierarchieSelect('vm_taxref_hierarchie', rang, request.args))
    return genericHierarchieSelect('vm_taxref_hierarchie', rang, request.args)

@adresses.route('/hierarchiebibtaxons/<rang>', methods=['GET'])
def getTaxrefHierarchieBibTaxons(rang):
    return jsonify(genericHierarchieSelect('v_taxref_hierarchie_bibtaxons', rang, request.args))

def genericTaxrefList(inBibtaxon, parameters):

    tableTaxref = GenericTable('taxonomie.taxref', 'taxonomie')
    tableBibTaxons = GenericTable('taxonomie.bib_taxons', 'taxonomie')

    q = db.session.query(tableTaxref.tableDef, tableBibTaxons.tableDef.columns.id_taxon)
    if inBibtaxon == True :
        q = q.join(tableBibTaxons.tableDef, tableBibTaxons.tableDef.columns.cd_nom==tableTaxref.tableDef.columns.cd_nom)
    else :
        q = q.outerjoin(tableBibTaxons.tableDef, tableBibTaxons.tableDef.columns.cd_nom==tableTaxref.tableDef.columns.cd_nom)

    #Traitement des parametres
    limit = parameters.get('limit') if parameters.get('limit') else 100
    offset = parameters.get('page') if parameters.get('page') else 0

    for param in parameters:
        if param in tableTaxref.columns and parameters[param] != '' :
            col = getattr(tableTaxref.tableDef.columns,param)
            q = q.filter(col == parameters[param])
        elif param == 'is_ref' and parameters[param] == True :
            q = q.filter(tableTaxref.tableDef.columns.cd_nom == tableTaxref.tableDef.columns.cd_ref)
        elif param == 'ilike' :
            q = q.filter(tableTaxref.tableDef.columns.lb_nom.ilike(parameters[param]+'%'))
        elif param == 'is_inbibtaxons' and parameters[param] == True :
            q = q.filter(tableBibTaxons.tableDef.columns.cd_nom.isnot(None))
    results = q.limit(limit).offset(offset).all()
    return jsonify(serializeQuery(results,q.column_descriptions))

def genericHierarchieSelect(tableName, rang, parameters):
    tableHierarchy = GenericTable('taxonomie.'+tableName, 'taxonomie')

    dfRang = tableHierarchy.tableDef.columns['id_rang']
    q = db.session.query(tableHierarchy.tableDef)\
        .filter(dfRang == rang)

    limit = parameters.get('limit') if parameters.get('limit') else 100

    for param in parameters:
        if param in tableHierarchy.columns:
            col = getattr(tableHierarchy.tableDef.columns,param)
            q = q.filter(col == parameters[param])
        elif param == 'ilike':
            q = q.filter(tableHierarchy.tableDef.columns.lb_nom.ilike(parameters[param]+'%'))

    results = q.limit(limit).all()
    return serializeQuery(results,q.column_descriptions)

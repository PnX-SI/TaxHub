#coding: utf8
from flask import jsonify, Blueprint, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select, distinct

from ..utils.utilssqlalchemy import json_resp, GenericTable, serializeQuery, serializeQueryOneResult
from .models import Taxref, BibNoms

from urllib.parse import unquote

db = SQLAlchemy()
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
    if field in taxrefColumns :
        value = unquote(ilike)
        column = taxrefColumns[field]
        q= db.session.query(column).filter(column.ilike(value+'%')).order_by(column)
        results = q.limit(20).all()
        return jsonify(serializeQuery(results,q.column_descriptions))
    else :
        return    'false'


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
        .outerjoin(tableBibTaxrefHabitats.tableDef, tableBibTaxrefHabitats.tableDef.columns.id_habitat==tableTaxref.tableDef.columns.id_habitat)\
        .outerjoin(tableBibTaxrefStatuts.tableDef, tableBibTaxrefStatuts.tableDef.columns.id_statut==tableTaxref.tableDef.columns.id_statut)\
        .outerjoin(tableBibTaxrefRangs.tableDef, tableBibTaxrefRangs.tableDef.columns.id_rang==tableTaxref.tableDef.columns.id_rang)\
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
    return genericHierarchieSelect('vm_taxref_hierarchie', rang, request.args)

@adresses.route('/hierarchiebibtaxons/<rang>', methods=['GET'])
def getTaxrefHierarchieBibNoms(rang):
    return jsonify(genericHierarchieSelect('v_taxref_hierarchie_bibtaxons', rang, request.args))

def genericTaxrefList(inBibtaxon, parameters):
    taxrefColumns = Taxref.__table__.columns
    bibNomsColumns = BibNoms.__table__.columns
    q = db.session.query(Taxref, BibNoms.id_nom)

    qcount = q.outerjoin(BibNoms, BibNoms.cd_nom==Taxref.cd_nom)

    nbResultsWithoutFilter = qcount.count()

    if inBibtaxon == True :
        q = q.join(BibNoms, BibNoms.cd_nom==Taxref.cd_nom)
    else :
        q = q.outerjoin(BibNoms, BibNoms.cd_nom==Taxref.cd_nom)

    #Traitement des parametres
    limit = int(parameters.get('limit')) if parameters.get('limit') else 100
    page = int(parameters.get('page'))-1 if parameters.get('page') else 0

    for param in parameters:
        if param in taxrefColumns and parameters[param] != '' :
            col = getattr(taxrefColumns,param)
            q = q.filter(col == parameters[param])
        elif param == 'is_ref' and parameters[param] == 'true' :
            q = q.filter(Taxref.cd_nom == Taxref.cd_ref)
        elif param == 'ilike' :
            q = q.filter(Taxref.lb_nom.ilike(parameters[param]+'%'))
        elif param == 'is_inbibtaxons' and parameters[param] == 'true' :
            q = q.filter(bibNomsColumns.cd_nom.isnot(None))
        elif param.split('-')[0] == 'ilike':
            value = unquote(parameters[param])
            col = str(param.split('-')[1])
            q = q.filter(taxrefColumns[col].ilike(value+'%'))

    nbResults = q.count()
    #Order by
    if 'orderby' in parameters:
        if parameters['orderby'] in taxrefColumns:
            orderCol =  getattr(taxrefColumns,parameters['orderby'])
        else:
            orderCol = None
        if 'order' in parameters:
            if (parameters['order'] == 'desc'):
                orderCol = orderCol.desc()
        q= q.order_by(orderCol)

    results = q.limit(limit).offset(page*limit).all()

    return {"items":[d.Taxref.as_dict() for d in results],"total": nbResultsWithoutFilter, "total_filtered":nbResults, "limit":limit, "page":page}

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

@adresses.route('/regnewithgroupe2', methods=['GET'])
@json_resp
def get_regneGroup2Inpn_taxref():
    """
        Retourne la liste des règne et groupe 2 défini par taxref de façon hiérarchique
        formatage : {'regne1':['grp1', 'grp2'], 'regne2':['grp3', 'grp4']}
    """
    q = db.session.query(Taxref.regne, Taxref.group2_inpn).distinct(Taxref.regne, Taxref.group2_inpn)\
        .filter(Taxref.regne != None).filter(Taxref.group2_inpn != None)
    data = q.all()
    results ={'':['']}
    for d in data:
        if d.regne in results:
            results[d.regne].append(d.group2_inpn)
        else:
            results[d.regne] = ['', d.group2_inpn]
    return results

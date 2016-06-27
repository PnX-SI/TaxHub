#coding: utf8
from flask import jsonify, json, Blueprint
from flask import request, Response

from server import db
from ..utils.utilssqlalchemy import json_resp
from .models import BibTaxons, Taxref, CorTaxonAttribut, CorTaxonListe
from sqlalchemy import func

import importlib

fnauth = importlib.import_module("apptax.flaskmodule-UserHub-auth.routes")

adresses = Blueprint('bib_taxons', __name__)

@adresses.route('/', methods=['GET'])
@json_resp
def get_bibtaxons():
    bibTaxonColumns = BibTaxons.__table__.columns
    taxrefColumns = Taxref.__table__.columns
    parameters = request.args

    q = db.session.query(BibTaxons)\
        .join(BibTaxons.taxref)

    #Traitement des parametres
    limit = parameters.get('limit') if parameters.get('limit') else 100
    offset = parameters.get('page') if parameters.get('page') else 0

    for param in parameters:
        if param in taxrefColumns:
            col = getattr(taxrefColumns,param)
            q = q.filter(col == parameters[param])
        elif param in bibTaxonColumns:
            col = getattr(bibTaxonColumns,param)
            q = q.filter(col == parameters[param])
        elif param == 'ilikelatin':
            q = q.filter(bibTaxonColumns.nom_latin.ilike(parameters[param]+'%'))
        elif param == 'ilikelfr':
            q = q.filter(bibTaxonColumns.nom_francais.ilike(parameters[param]+'%'))
    count= q.count()
    results = q.limit(limit).all()
    taxonsList = []
    for r in results :
        obj = r.as_dict()
        obj['is_doublon'] = False

        #Ajout des synonymes
        (nbsyn, results) = getBibTaxonSynonymes(obj['id_taxon'], obj['cd_nom'])
        if nbsyn > 0 :
            obj['is_doublon'] = True
            obj['synonymes'] = [i.id_taxon for i in results]
        taxonsList.append(obj)

    return taxonsList


@adresses.route('/<int:id_taxon>', methods=['GET'])
@json_resp
def getOne_bibtaxons(id_taxon):
    bibTaxon =db.session.query(BibTaxons).filter_by(id_taxon=id_taxon).first()

    obj = bibTaxon.as_dict()
    obj['is_doublon'] = False
    #Ajout des synonymes
    (nbsyn, results) = getBibTaxonSynonymes(id_taxon, bibTaxon.cd_nom)
    if nbsyn > 0 :
        obj['is_doublon'] = True
        obj['synonymes'] = [i.id_taxon for i in results]

    #Ajout des attributs
    obj['attributs'] = [dict(attr.as_dict().items() | attr.bib_attribut.as_dict().items()) for attr in  bibTaxon.attributs ]

    #Ajout des listes
    obj['listes'] = [dict(liste.as_dict().items() | liste.bib_liste.as_dict().items()) for liste in  bibTaxon.listes ]
    return obj

@adresses.route('/', methods=['POST', 'PUT'])
@adresses.route('/<int:id_taxon>', methods=['POST', 'PUT'])
# @fnauth.check_auth(4)
def insertUpdate_bibtaxons(id_taxon=None):
    data = request.get_json(silent=True)
    if id_taxon:
        bibTaxon =db.session.query(BibTaxons).filter_by(id_taxon=id_taxon).first()
        message = "Taxon mis à jour"
    else :
        bibTaxon = BibTaxons(
            cd_nom = data['cd_nom'],
            nom_latin =  data['nom_latin'],
            nom_francais =  data['nom_francais'],
            auteur =data['auteur'] if 'auteur' in data else None
        )
        message = "Taxon ajouté"
    db.session.add(bibTaxon)
    db.session.commit()

    id_taxon = bibTaxon.id_taxon

    ####--------------Traitement des attibuts-----------------
    #Suppression des attributs exisitants
    for bibTaxonAtt in bibTaxon.attributs:
         db.session.delete(bibTaxonAtt)
    db.session.commit()

    for att in data['attributs_values']:
        attVal = CorTaxonAttribut(
            id_attribut = att,
            id_taxon = id_taxon,
            valeur_attribut =data['attributs_values'][att]
        )
        db.session.add(attVal)
    db.session.commit()

    ####--------------Traitement des listes-----------------
    #Suppression des listes exisitantes
    for bibTaxonLst in bibTaxon.listes:
        print( bibTaxonLst)
        db.session.delete(bibTaxonLst)
    db.session.commit()
    for lst in data['listes']:
        listTax = CorTaxonListe (
            id_liste = lst['id_liste'],
            id_taxon = id_taxon
        )
        db.session.add(listTax)
    db.session.commit()
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

@adresses.route('/<int:id_taxon>', methods=['DELETE'])
@fnauth.check_auth(4)
@json_resp
def delete_bibtaxons(id_taxon):
    bibTaxon =db.session.query(BibTaxons).filter_by(id_taxon=id_taxon).first()
    db.session.delete(bibTaxon)
    db.session.commit()

    return bibTaxon.as_dict()


def getBibTaxonSynonymes(id_taxon, cd_nom):
    q = db.session.query(BibTaxons.id_taxon)\
        .join(BibTaxons.taxref)\
        .filter(Taxref.cd_ref== func.taxonomie.find_cdref(cd_nom))\
        .filter(BibTaxons.id_taxon != id_taxon)
    results =q.all()
    return (q.count(), results)

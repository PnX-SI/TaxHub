#coding: utf8
from flask import jsonify, json, Blueprint
from flask import request, Response

from server import db
from ..utils.utilssqlalchemy import json_resp, serializeQueryOneResult
from .models import BibNoms, Taxref, CorTaxonAttribut, CorNomListe
from sqlalchemy import func

import importlib

fnauth = importlib.import_module("apptax.flaskmodule-UserHub-auth.routes")

adresses = Blueprint('bib_noms', __name__)

@adresses.route('/', methods=['GET'])
@json_resp
def get_bibtaxons():
    bibTaxonColumns = BibNoms.__table__.columns
    taxrefColumns = Taxref.__table__.columns
    parameters = request.args

    q = db.session.query(BibNoms)\
        .join(BibNoms.taxref)

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
            q = q.filter(taxrefColumns.nom_complet.ilike(parameters[param]+'%'))
        elif param == 'ilikelfr':
            q = q.filter(bibTaxonColumns.nom_francais.ilike(parameters[param]+'%'))
    count= q.count()
    results = q.limit(limit).all()
    taxonsList = []
    for r in results :
        obj = r.as_dict()

        #Ajout de taxref
        obj['taxref'] = r.taxref.as_dict()

        #Ajout des synonymes
        # obj['is_doublon'] = False
        # (nbsyn, results) = getBibTaxonSynonymes(obj['id_nom'], obj['cd_nom'])
        # if nbsyn > 0 :
        #     obj['is_doublon'] = True
        #     obj['synonymes'] = [i.id_nom for i in results]

        taxonsList.append(obj)

    return taxonsList


@adresses.route('/<int:id_nom>', methods=['GET'])
@json_resp
def getOne_bibtaxons(id_nom):
    bibTaxon =db.session.query(BibNoms).filter_by(id_nom=id_nom).first()

    obj = bibTaxon.as_dict()

    #Ajout des synonymes
    obj['is_doublon'] = False
    (nbsyn, results) = getBibTaxonSynonymes(id_nom, bibTaxon.cd_nom)
    if nbsyn > 0 :
        obj['is_doublon'] = True
        obj['synonymes'] = [i.id_nom for i in results]

    #Ajout des attributs
    obj['attributs'] = []
    for attr in  bibTaxon.attributs :
        o = dict(attr.as_dict().items())
        o.update(dict(attr.bib_attribut.as_dict().items()))
        obj['attributs'].append(o)

    #Ajout des donnees taxref
    obj['taxref'] = bibTaxon.taxref.as_dict()

    #Ajout des listes
    obj['listes'] = []
    for liste in  bibTaxon.listes :
        o = dict(liste.as_dict().items())
        o.update(dict(liste.bib_liste.as_dict().items()))
        obj['listes'].append(o)
    return obj

@adresses.route('/', methods=['POST', 'PUT'])
@adresses.route('/<int:id_nom>', methods=['POST', 'PUT'])
@fnauth.check_auth(4)
def insertUpdate_bibtaxons(id_nom=None):
    data = request.get_json(silent=True)
    print(data)
    if id_nom:
        bibTaxon =db.session.query(BibNoms).filter_by(id_nom=id_nom).first()
        message = "Taxon mis à jour"
    else :
        bibTaxon = BibNoms(
            cd_nom = data['cd_nom'],
            cd_ref = data['cd_ref'],
            nom_francais =data['nom_francais'] if 'nom_francais' in data else None
        )
        message = "Taxon ajouté"
    db.session.add(bibTaxon)
    db.session.commit()

    id_nom = bibTaxon.id_nom

    ####--------------Traitement des attibuts-----------------
    #Suppression des attributs exisitants
    for bibTaxonAtt in bibTaxon.attributs:
         db.session.delete(bibTaxonAtt)
    db.session.commit()

    if 'attributs_values' in data :
        for att in data['attributs_values']:
            attVal = CorTaxonAttribut(
                id_attribut = att,
                cd_ref = bibTaxon.cd_ref,
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
    if 'listes' in data :
        for lst in data['listes']:
            listTax = CorNomListe (
                id_liste = lst['id_liste'],
                id_nom = id_nom
            )
            db.session.add(listTax)
        db.session.commit()
    return json.dumps({'success':True, 'id_nom':id_nom}), 200, {'ContentType':'application/json'}

@adresses.route('/<int:id_nom>', methods=['DELETE'])
@fnauth.check_auth(4)
@json_resp
def delete_bibtaxons(id_nom):
    bibTaxon =db.session.query(BibNoms).filter_by(id_nom=id_nom).first()
    db.session.delete(bibTaxon)
    db.session.commit()

    return bibTaxon.as_dict()


def getBibTaxonSynonymes(id_nom, cd_nom):
    q = db.session.query(BibNoms.id_nom)\
        .join(BibNoms.taxref)\
        .filter(Taxref.cd_ref== func.taxonomie.find_cdref(cd_nom))\
        .filter(BibNoms.id_nom != id_nom)
    results =q.all()
    return (q.count(), results)

#coding: utf8
from flask import jsonify, json, Blueprint, request, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

from ..utils.utilssqlalchemy import json_resp, serializeQueryOneResult
from ..log import logmanager
from .models import BibNoms, Taxref, CorTaxonAttribut, BibThemes, CorNomListe, TMedias

from pypnusershub import routes as fnauth

db = SQLAlchemy()
adresses = Blueprint('bib_noms', __name__)


@adresses.route('/', methods=['GET'])
@json_resp
def get_bibtaxons():
    bibTaxonColumns = BibNoms.__table__.columns
    taxrefColumns = Taxref.__table__.columns
    parameters = request.args

    q = db.session.query(BibNoms,Taxref).\
    filter(BibNoms.cd_nom == Taxref.cd_nom)

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

    data = q.all()
    results = []
    for row in data:
        data_as_dict = row.BibNoms.as_dict()
        data_as_dict['taxref'] = row.Taxref.as_dict()
        results.append(data_as_dict)
    return results


@adresses.route('/taxoninfo/<int:cd_nom>', methods=['GET'])
@json_resp
def getOne_bibtaxonsInfo(cd_nom):
    #Récupération du cd_ref à partir du cd_nom
    cd_ref = db.session.query(Taxref.cd_ref).filter_by(cd_nom=cd_nom).first()
    obj = {}

    #Ajout des attributs
    obj['attributs'] = []
    bibAttr =db.session.query(CorTaxonAttribut).filter_by(cd_ref=cd_ref).all()
    for attr in  bibAttr :
        o = dict(attr.as_dict().items())
        o.update(dict(attr.bib_attribut.as_dict().items()))
        id = o['id_theme']
        theme = db.session.query(BibThemes).filter_by(id_theme=id).first()
        o['nom_theme'] = theme.as_dict()['nom_theme']
        obj['attributs'].append(o)

    #Ajout des medias
    medias =db.session.query(TMedias).filter_by(cd_ref=cd_ref).all()
    obj['medias'] = []
    for medium in medias :
        o = dict(medium.as_dict().items())
        o.update(dict(medium.types.as_dict().items()))
        obj['medias'].append(o)
    return obj


@adresses.route('/simple/<int:id_nom>', methods=['GET'])
@json_resp
def getOneSimple_bibtaxons(id_nom):
    bibTaxon =db.session.query(BibNoms).filter_by(id_nom=id_nom).first()
    obj = bibTaxon.as_dict()

    #Ajout des listes
    obj['listes'] = []
    for liste in  bibTaxon.listes :
        o = dict(liste.as_dict().items())
        o.update(dict(liste.bib_liste.as_dict().items()))
        obj['listes'].append(o)

    return obj


@adresses.route('/<int:id_nom>', methods=['GET'])
@json_resp
def getOneFull_bibtaxons(id_nom):
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
        id = o['id_theme']
        theme = db.session.query(BibThemes).filter_by(id_theme=id).first()
        o['nom_theme'] = theme.as_dict()['nom_theme']
        obj['attributs'].append(o)

    #Ajout des donnees taxref
    obj['taxref'] = bibTaxon.taxref.as_dict()

    #Ajout des listes
    obj['listes'] = []
    for liste in  bibTaxon.listes :
        o = dict(liste.as_dict().items())
        o.update(dict(liste.bib_liste.as_dict().items()))
        obj['listes'].append(o)

    #Ajout des medias
    obj['medias'] = []
    for medium in  bibTaxon.medias :
        o = dict(medium.as_dict().items())
        o.update(dict(medium.types.as_dict().items()))
        obj['medias'].append(o)
    return obj


# Compter le nombre d'enregistrements dans bib_noms
@adresses.route('/count', methods=['GET'])
@json_resp
def getCount_bibtaxons():
    return db.session.query(BibNoms).count()
    

@adresses.route('/', methods=['POST', 'PUT'])
@adresses.route('/<int:id_nom>', methods=['POST', 'PUT'])
@fnauth.check_auth(3, True)
def insertUpdate_bibtaxons(id_nom=None, id_role=None):
    try:
        data = request.get_json(silent=True)
        if id_nom:
            bibTaxon =db.session.query(BibNoms).filter_by(id_nom=id_nom).first()
            if 'nom_francais' in data :
                bibTaxon.nom_francais = data['nom_francais']
            action = 'UPDATE'
            message = "Taxon mis à jour"
        else :
            bibTaxon = BibNoms(
                cd_nom = data['cd_nom'],
                cd_ref = data['cd_ref'],
                nom_francais =data['nom_francais'] if 'nom_francais' in data else None
            )
            action = 'INSERT'
            message = "Taxon ajouté"
        db.session.add(bibTaxon)
        db.session.commit()

        id_nom = bibTaxon.id_nom

        ####--------------Traitement des attibuts-----------------
        #Suppression des attributs existants
        for bibTaxonAtt in bibTaxon.attributs:
            db.session.delete(bibTaxonAtt)
        db.session.commit()

        if 'attributs_values' in data :
            for att in data['attributs_values']:
                if data['attributs_values'][att] != '' :
                    attVal = CorTaxonAttribut(
                        id_attribut = att,
                        cd_ref = bibTaxon.cd_ref,
                        valeur_attribut =data['attributs_values'][att]
                    )
                    db.session.add(attVal)
            db.session.commit()

        ####--------------Traitement des listes-----------------
        #Suppression des listes existantes
        for bibTaxonLst in bibTaxon.listes:
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

        ##Log
        logmanager.log_action(id_role, 'bib_nom', id_nom, repr(bibTaxon),action,message)
        return json.dumps({'success':True, 'id_nom':id_nom}), 200, {'ContentType':'application/json'}
    except Exception as e:
        db.session.rollback()
        return json.dumps({'success':True, 'message':e}), 500, {'ContentType':'application/json'}


@adresses.route('/<int:id_nom>', methods=['DELETE'])
@fnauth.check_auth(6, True)
@json_resp
def delete_bibtaxons(id_nom, id_role=None):
    bibTaxon =db.session.query(BibNoms).filter_by(id_nom=id_nom).first()
    db.session.delete(bibTaxon)
    db.session.commit()

    ##Log
    logmanager.log_action(id_role, 'bib_nom', id_nom, repr(bibTaxon),'DELETE','nom supprimé')

    return bibTaxon.as_dict()


# Private functions  
def getBibTaxonSynonymes(id_nom, cd_nom):
    q = db.session.query(BibNoms.id_nom)\
        .join(BibNoms.taxref)\
        .filter(Taxref.cd_ref== func.taxonomie.find_cdref(cd_nom))\
        .filter(BibNoms.id_nom != id_nom)
    results =q.all()
    return (q.count(), results)

#coding: utf8
from flask import Blueprint, request
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, select, or_

from ..utils.utilssqlalchemy import json_resp, csv_resp
from .models import BibListes, CorNomListe, Taxref,BibNoms
from . import filemanager
from ..log import logmanager

from pypnusershub import routes as fnauth

db = SQLAlchemy()
adresses = Blueprint('bib_listes', __name__)


@adresses.route('/', methods=['GET'])
@json_resp
def get_biblistes(id = None):
        """
        retourne les contenu de bib_listes dans "data"
        et le nombre d'enregistrements dans "count"
        """
        data = db.session.query(BibListes, func.count(CorNomListe.id_nom).label('c'))\
            .outerjoin(CorNomListe)\
            .group_by(BibListes)\
            .order_by(BibListes.nom_liste).all()
        maliste = {"data":[],"count":0}
        maliste["count"] = len(data)
        for l in data:
            d = l.BibListes.as_dict()
            d['nb_taxons'] = l.c
            maliste["data"].append(d)
        return maliste


@adresses.route('/<regne>', methods=['GET'])
@adresses.route('/<regne>/<group2_inpn>', methods=['GET'])
@json_resp
def get_biblistesbyTaxref(regne, group2_inpn = None):
    q = db.session.query(BibListes)
    if regne :
        q = q.filter(or_(BibListes.regne == regne, BibListes.regne == None))
    if group2_inpn :
        q = q.filter(or_(BibListes.group2_inpn == group2_inpn, BibListes.group2_inpn == None))
    results = q.all()
    return [liste.as_dict() for liste in results]


@adresses.route('/info/<int:idliste>', methods=['GET'])
@json_resp
def getOne_biblistesInfo(idliste = None):
    """
    Information de la liste et liste des taxons d'une liste
    """
    data_liste = db.session.query(BibListes).filter_by(id_liste=idliste).first()
    nom_liste = data_liste.as_dict()

    data = db.session.query(BibNoms,
    Taxref.nom_complet, Taxref.regne, Taxref.group2_inpn).\
    filter(BibNoms.cd_nom == Taxref.cd_nom).\
    filter(BibNoms.id_nom == CorNomListe.id_nom).\
    filter(CorNomListe.id_liste == idliste)

    taxons = data.all()
    results = []
    for row in taxons:
        data_as_dict = row.BibNoms.as_dict()
        data_as_dict['nom_complet'] = row.nom_complet
        data_as_dict['regne'] = row.regne
        data_as_dict['group2_inpn'] = row.group2_inpn
        results.append(data_as_dict)
    return  [nom_liste,results,len(taxons)]


@adresses.route('/exportcsv/<int:idliste>', methods=['GET'])
@csv_resp
def getExporter_biblistesCSV(idliste = None):
    """
        Exporter les taxons d'une liste dans un fichier csv
    """
    liste = db.session.query(BibListes).get(idliste)
    cleanNomliste = filemanager.removeDisallowedFilenameChars(liste.nom_liste)

    data = db.session.query(Taxref).\
        filter(BibNoms.cd_nom == Taxref.cd_nom).filter(BibNoms.id_nom == CorNomListe.id_nom).\
        filter(CorNomListe.id_liste == idliste).all()
    return (cleanNomliste, [nom.as_dict() for nom in data], Taxref.__table__.columns.keys(), ',')


######## Route pour module edit and create biblistes ##############################################

# Get data of list by id
@adresses.route('/<int:idliste>', methods=['GET'])
@json_resp
def getOne_biblistes(idliste = None):
    data = db.session.query(BibListes).filter_by(id_liste=idliste).first()
    return data.as_dict()


# Get list of picto in repertory ./static/images/pictos
@adresses.route('/pictosprojet', methods=['GET'])
@json_resp
def getPictos_files():
    pictos = os.listdir("./static/images/pictos")
    pictos.sort()
    return pictos

######### PUT CREER/MODIFIER BIBLISTES ######################
@adresses.route('/', methods=['POST','PUT'])
@adresses.route('/<int:id_liste>', methods=['POST', 'PUT'])
@json_resp
@fnauth.check_auth(4, True)
def insertUpdate_biblistes(id_liste=None, id_role=None):
    res = request.get_json(silent=True)
    data = {k:v or None for (k,v) in res.items()}

    action = 'INSERT'
    message = "Liste créée"
    if (id_liste) :
        action = 'UPDATE'
        message = "Liste mise à jour"

    bib_liste = BibListes(**data)
    db.session.merge(bib_liste)
    try:
        db.session.commit()
        logmanager.log_action(id_role, 'bib_liste', bib_liste.id_liste, repr(bib_liste),action,message)
        return bib_liste.as_dict()
    except Exception as e:
        db.session.rollback()
        return ({'success':False, 'message':'Impossible de sauvegarder l\'enregistrement'}, 500)


######## Route pour module ajouter noms à la liste ##############################################
## Get Taxons + taxref in a liste with id_liste
@adresses.route('/taxons/', methods=['GET'])
@adresses.route('/taxons/<int:idliste>', methods=['GET'])
@json_resp
def getNoms_bibtaxons(idliste = None):
    q = db.session.query(BibNoms,
        Taxref.nom_complet, Taxref.regne, Taxref.group2_inpn).\
        filter(BibNoms.cd_nom == Taxref.cd_nom)

    if (idliste) :
        q = q.filter(BibNoms.id_nom == CorNomListe.id_nom).\
        filter(CorNomListe.id_liste == idliste)

    data = q.all()
    results = []
    for row in data:
        data_as_dict = row.BibNoms.as_dict()
        data_as_dict['nom_complet'] = row.nom_complet
        data_as_dict['regne'] = row.regne
        data_as_dict['group2_inpn'] = row.group2_inpn
        results.append(data_as_dict)
    return results


## POST - Ajouter les noms à une liste
@adresses.route('/addnoms/<int:idliste>', methods=['POST'])
@json_resp
@fnauth.check_auth(4, True)
def add_cornomliste(idliste = None,id_role=None):
    ids_nom = request.get_json(silent=True)
    data = db.session.query(CorNomListe).filter(CorNomListe.id_liste == idliste).all()
    for id in ids_nom:
        cornom = {'id_nom':id,'id_liste':idliste}
        add_nom = CorNomListe(**cornom)
        db.session.add(add_nom)
    try:
        db.session.commit()

        logmanager.log_action(id_role, 'cor_nom_liste', idliste, '','AJOUT NOM','Noms ajouté à la liste')
        return ids_nom
    except Exception as e:
        db.session.rollback()
        return ({'success':False, 'message':'Impossible de sauvegarder l\'enregistrement'}, 500)


## POST - Enlever les nom dans une liste
@adresses.route('/deletenoms/<int:idliste>', methods=['POST'])
@json_resp
@fnauth.check_auth(4, True)
def delete_cornomliste(idliste = None,id_role=None):
    ids_nom = request.get_json(silent=True)
    for id in ids_nom:
        del_nom =db.session.query(CorNomListe).filter(CorNomListe.id_liste == idliste).\
        filter(CorNomListe.id_nom == id).first()
        db.session.delete(del_nom)
    try:
        db.session.commit()
        
        logmanager.log_action(id_role, 'cor_nom_liste', idliste, '','SUPPRESSION NOM','Noms supprimés de la liste')
        return ids_nom
    except Exception as e:
        db.session.rollback()
        return ({'success':False, 'message':'Impossible de sauvegarder l\'enregistrement'}, 500)

#coding: utf8
from flask import jsonify, json, Blueprint, request, Response, make_response
import os, csv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select, or_

from ..utils.utilssqlalchemy import json_resp
from .models import BibListes, CorNomListe, Taxref,BibNoms

from pypnusershub import routes as fnauth

db = SQLAlchemy()
adresses = Blueprint('bib_listes', __name__)

@adresses.route('/', methods=['GET'])
@json_resp
def get_biblistes(id = None):
        data = db.session.query(BibListes).all()
        maliste = []
        for l in data:
            d = l.as_dict()
            d['nb_taxons'] = len(l.cnl)
            maliste.append(d)
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


@adresses.route('/noms/<int:idliste>', methods=['GET'])
@json_resp
def get_cor_biblistesnoms(idliste = None):
    data = db.session.query(CorNomListe).filter_by(id_liste=idliste).all()
    data_liste = db.session.query(BibListes).filter_by(id_liste=idliste).first()
    # query for get nom and taxref
    liste = [{'nom':nom.bib_nom.as_dict(), 'taxref' : nom.bib_nom.taxref.as_dict()} for nom in data]
    # query for get liste
    nom_liste = data_liste.as_dict()

    if len(liste) == 0 : 
        return  [nom_liste,[]]
    else:
        return  [nom_liste,liste]

@adresses.route('/count', methods=['GET'])
@json_resp
def get_countbiblistes():
    #Compter le nombre d'enregistrements dans biblistes
    return db.session.query(BibListes).count() 


@adresses.route('/count/<int:idliste>', methods=['GET'])
@json_resp
def get_count_detailbiblistes(idliste = None):
    #Compter le nombre de taxons dans une liste
    data_liste = db.session.query(BibListes).filter_by(id_liste=idliste).first()
    return len(data_liste.cnl)

######## Route pour module edit and create biblistes ##############################################

# Get data of list by id
@adresses.route('/<int:idliste>', methods=['GET'])
@json_resp
def get_edit_biblistesbyid(idliste = None):
    data = db.session.query(BibListes).filter_by(id_liste=idliste).first()
    return data.as_dict()

# Get list of regne from taxref
# TODO : voir s'il ne serait pas plus logique de mettre cette route dans routestaxref.py
@adresses.route('/taxref/regne', methods=['GET'])
@json_resp
def get_listof_regne():
    regnes = db.session.query(Taxref.regne).distinct().order_by(Taxref.regne).all()
    nw_regne = []
    for regne in regnes:
        nw_regne.append(regne[0])
    return nw_regne

# Get list of group2_inpn from taxref
# TODO : idem, voir s'il ne serait pas plus logique de mettre cette route dans routestaxref.py
@adresses.route('/taxref/group2_inpn', methods=['GET'])
@json_resp
def get_listof_group2_inpn():
    group2_inpn = db.session.query(Taxref.group2_inpn).distinct().order_by(Taxref.group2_inpn).all()
    nw_group2_inpn = []
    for groupe in group2_inpn:
        nw_group2_inpn.append(groupe[0])
    return nw_group2_inpn

# Get list of picto in dossier ./static/images/pictos
@adresses.route('/picto_projet', methods=['GET'])
@json_resp
def get_listof_picto_projet():
    pictos = os.listdir("./static/images/pictos")
    pictos.sort()
    return pictos

# Get list of picto in database biblistes
@adresses.route('/picto_biblistes', methods=['GET'])
@json_resp
def get_listof_picto_biblistes():
    pictos = db.session.query(BibListes.picto).distinct().order_by(BibListes.picto).all()
    nw_pictos = []
    for picto in pictos:
        nw_pictos.append(picto[0])
    return nw_pictos

# Get list of nom_liste in database biblistes
@adresses.route('/nom_liste', methods=['GET'])
@json_resp
def get_listof_nom_liste():
    nom_liste = db.session.query(BibListes.nom_liste).distinct().order_by(BibListes.nom_liste).all()
    nw_nom_liste = []
    for nom in nom_liste:
        nw_nom_liste.append(nom[0])
    return nw_nom_liste

# Get list of id_liste in database biblistes
@adresses.route('/id_liste', methods=['GET'])
@json_resp
def get_listof_id_liste():
    ids = db.session.query(BibListes.id_liste).order_by(BibListes.id_liste).all()
    nw_id_liste = []
    for i in ids:
        nw_id_liste.append(i[0])
    return nw_id_liste

######### PUT MODIFIER BIBLISTES ######################
# TODO : retirer "insert" du nom de la fonction ou fusionner les 2 routes create et update
@adresses.route('/edit/', methods=['PUT'])
@adresses.route('/edit/<int:id_liste>', methods=['POST', 'PUT'])
@json_resp
@fnauth.check_auth(4, True)
def insertUpdate_biblistes(id_liste=None, id_role=None):

    res = request.get_json(silent=True)
    bib_liste = db.session.query(BibListes).filter_by(id_liste=id_liste).first()
        
    bib_liste.nom_liste = res['nom_liste']
    bib_liste.desc_liste = res['desc_liste']    
    bib_liste.picto = res['picto']
    bib_liste.regne = res['regne']
    bib_liste.group2_inpn = res['group2_inpn']

    db.session.add(bib_liste)
    db.session.commit()

    return bib_liste.as_dict()
        
######### POST CREER BIBLISTES ######################
@adresses.route('/create/', methods=['POST'])
@adresses.route('/create/<int:id_liste>', methods=['POST'])
@json_resp
@fnauth.check_auth(4, True)
def create_biblistes(id_liste=None, id_role=None):
    res = request.get_json(silent=True)
    bib_liste = BibListes()
    
    bib_liste.id_liste = res['id_liste']    
    bib_liste.nom_liste = res['nom_liste']
    bib_liste.desc_liste = res['desc_liste']    
    bib_liste.picto = res['picto']
    bib_liste.regne = res['regne']
    bib_liste.group2_inpn = res['group2_inpn']

    db.session.add(bib_liste)
    db.session.commit()

    return bib_liste.as_dict()

######## Route pour module edit and create biblistes ##############################################
## Exporter route 
@adresses.route('/exporter/<int:idliste>', methods=['GET'])
@json_resp
def get_exporter_liste(idliste = None):
    data = db.session.query(CorNomListe).filter_by(id_liste=idliste).all()
    data_liste = db.session.query(BibListes).filter_by(id_liste=idliste).first()
    return [nom.bib_nom.taxref.as_dict() for nom in data]

######## Route pour module ajouter noms à la liste ##############################################
## Get Taxons
#TODO : idem discuter si mettre cette route dans routesbibnoms.py
@adresses.route('/add/taxons', methods=['GET'])
@json_resp
def get_bibtaxons():
    data = db.engine.execute("\
        select tbn.cd_ref,tbn.id_nom, tbn.cd_nom, tbn.nom_francais, tt.nom_complet \
        from taxonomie.bib_noms tbn, taxonomie.taxref tt \
        where tbn.cd_nom = tt.cd_nom")
    results = []
    for row in data:
        data_as_dict = {
            'nom_complet' : row.nom_complet,
            'nom_francais': row.nom_francais,
            'cd_nom': row.cd_nom,
            'id_nom': row.id_nom,
            'cd_ref': row.cd_ref}
        results.append(data_as_dict)
    return results

## Get Taxons + taxref with in a liste with id_liste
@adresses.route('/add/taxons/<int:idliste>', methods=['GET'])
@json_resp
def get_bibtaxons_idliste(idliste = None):
    data = db.engine.execute("\
        SELECT *\
        FROM    taxonomie.bib_noms tbn, taxonomie.taxref tt\
        WHERE   tbn.id_nom IN (SELECT DISTINCT tcnl.id_nom\
                                FROM taxonomie.cor_nom_liste tcnl\
                                WHERE tcnl.id_liste = %s)\
                AND tbn.cd_nom = tt.cd_nom",idliste)
    results = []
    for row in data:
        data_as_dict = {
            'nom_complet' : row.nom_complet,
            'nom_francais': row.nom_francais,
            'cd_nom': row.cd_nom,
            'id_nom': row.id_nom,
            'cd_ref': row.cd_ref}
        results.append(data_as_dict)
    return results
# coding: utf8
import psycopg2
from functions import main

import configparser

from config import SQLALCHEMY_DATABASE_URI


'''
    Exemple d'utilisation de la fonctionnalité importer média depuis médiawiki
    Usage :
        - créer un lien symbolique de config.py
            pour récupérer les paramètres de connexion à la base
        - choisir une requête sql qui récupère la liste des taxons
            pour lequels récupérer des médias
        - paramétrer la fonction main
'''
try:
    conn = psycopg2.connect(SQLALCHEMY_DATABASE_URI)
except Exception as e:
    print "Connexion à la base impossible"

try:
    cur = conn.cursor()
    sql = """SELECT DISTINCT cd_ref
        FROM taxonomie.bib_noms
        LEFT OUTER JOIN taxonomie.t_medias USING(cd_ref)
        WHERE id_media IS NULL
    """
    # sql = """SELECT cd_ref from taxonomie.bib_noms LIMIT 10"""
    sql = """SELECT cd_ref from atlas.vm_taxons_plus_observes LIMIT 100"""
    cur.execute(sql)
    rows = cur.fetchall()
except Exception as e:
    print "Problème lors de la récupération de la liste des cd_ref"

main(conn, rows, False, False)


conn.close()

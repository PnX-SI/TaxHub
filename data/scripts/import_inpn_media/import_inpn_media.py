# coding: utf8
import psycopg2
import requests

import config

'''
    Exemple d'utilisation de la fonctionnalité importer média depuis inpn
    Usage :
        - créer un lien symbolique de config.py
            pour récupérer les paramètres de connexion à la base
        - choisir une requête sql qui récupère la liste des taxons
            pour lequels récupérer des médias
        - paramétrer la fonction main
    Librairies requises (à installer via pip dans un virtualenv de préférence)
        psycopg2
        requests
'''

# ################
# CONSTANTES
API_URL = "https://taxref.mnhn.fr/api/media/cdNom/{}"

SOURCE = "INPN"

QUERY_INSERT_TMEDIA = """
    INSERT INTO taxonomie.t_medias (
        cd_ref, titre, url, auteur,
        desc_media, date_media, id_type, source, licence
    )
    VALUES (
        %s, %s, %s, %s, COALESCE(%s, null), now(), %s, %s, %s
    );
"""

QUERY_UPDATE_TMEDIA = """
    UPDATE taxonomie.t_medias
    SET titre = %s,  auteur = %s, desc_media= %s, licence =%s
    WHERE cd_ref = %s AND url = %s AND source = %s
"""

QUERY_SELECT_TESTEXISTS = """
    SELECT count(*)
    FROM taxonomie.t_medias
    WHERE cd_ref = %s AND url = %s AND source = %s
"""


# ################
# FONCTIONS

def runquery(cursor, sql, params, trap=False):
    try:
        return cursor.execute(
            sql,
            params
        )
    except Exception as exp:
        print(exp)
        if trap:
            pass
        raise exp


def process_media(media):
    '''
        Fonction qui gère l'enregistrement du media
        dans la base
    '''
    print(media['url'], media['licence'], media['legende'], media['copyright'])

    # Test si média existe déjà en base
    runquery(
        cur,
        QUERY_SELECT_TESTEXISTS,
        (cd_ref[0], media['url'], SOURCE)
    )
    nb = cur.fetchall()

    if nb[0][0] > 0:
        # Mise à jour au cas ou les données
        #       licence/légende/copyright aient changées
        print('update')
        runquery(
            cur,
            QUERY_UPDATE_TMEDIA,
            (
                media['taxon']['lbNom'],
                media['copyright'],
                media['legende'],
                media['licence'],
                cd_ref[0],
                media['url'],
                SOURCE
            ),
            True
        )
    else:
        # Si le média n'éxiste pas insertion en base
        print('insert')
        runquery(
            cur,
            QUERY_INSERT_TMEDIA,
            (
                cd_ref[0], media['taxon']['lbNom'],
                media['url'], media['copyright'],
                media['legende'], 2,
                SOURCE,
                media['licence']
            ),
            True
        )
    conn.commit()


# ################
# SCRIPT
try:
    conn = psycopg2.connect(config.SQLALCHEMY_DATABASE_URI)
except Exception as e:
    print("Connexion à la base impossible")

try:
    cur = conn.cursor()
    cur.execute(config.QUERY_SELECT_CDREF)
    rows = cur.fetchall()
except Exception as e:
    print("Problème lors de la récupération de la liste des cd_ref")


for cd_ref in rows:
    print('TAXON : cd_ref =', cd_ref[0])
    url = API_URL.format(cd_ref[0])
    r = requests.get(url)
    if r.json()['media']:
        medias = r.json()['media']['media']
        if not medias:
            print('    no media')

        for media in medias:
            process_media(media)

conn.close()

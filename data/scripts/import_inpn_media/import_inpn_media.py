# coding: utf8
'''
    Script permettant l'import de médias récupérés via l'API inpn
'''

import psycopg2
import requests

import config


# CONSTANTES
API_URL = "https://taxref.mnhn.fr/api/taxa/{}/media"

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

class Media():

    def __init__(
        self, 
        cd_ref, titre, nom, auteur, desc_media, licence,
        url
    ):
        self.cd_ref = cd_ref
        self.titre = titre
        self.nom = nom
        self.auteur = auteur
        self.desc_media = desc_media
        self.licence = licence
        self.url = url

    def __repr__(self):
        return "Nom: {}, Media: {}".format(
            self.nom, self.url
        )


# FONCTIONS
def runquery(cursor, sql, params, trap=False):
    '''
        Fonction permettant d'executer une requete
        trap : Indique si les erreurs sont ou pas retournées
    '''
    try:
        result = cursor.execute(
            sql,
            params
        )
        return result
    except Exception as exp:
        print(exp)
        if trap:
            return None
        raise exp


def process_media(cur, cd_ref, media):
    '''
        Fonction qui gère l'enregistrement du media dans la base
    '''
    m_obj = Media(
        cd_ref, 
        titre = media['taxon']['referenceNameHtml'], 
        nom = media['taxon']['scientificName'], 
        auteur =  media['copyright'],
        desc_media = media['title'],
        licence  = media['licence'],
        url = media['_links']['file']['href']
    )

    # Test si média existe déjà en base
    runquery(
        cur,
        QUERY_SELECT_TESTEXISTS,
        (m_obj.cd_ref, m_obj.url, SOURCE)
    )
    nb_r = cur.fetchall()

    if nb_r[0][0] > 0:
        # Mise à jour au cas ou les données
        # licence/légende/copyright aient changées
        print(f'\t{m_obj}, Action : UPDATE')
        runquery(
            cur,
            QUERY_UPDATE_TMEDIA,
            (
                m_obj.titre,
                m_obj.auteur,
                m_obj.desc_media,
                m_obj.licence,
                m_obj.cd_ref,
                m_obj.url,
                SOURCE
            ),
            True
        )
    else:
        # Si le média n'existe pas insertion en base
        print(f'\t{m_obj}, Action : INSERT')
        runquery(
            cur,
            QUERY_INSERT_TMEDIA,
            (
                m_obj.cd_ref, m_obj.titre,
                m_obj.url, m_obj.auteur,
                m_obj.desc_media, 2,
                SOURCE, m_obj.licence
            ),
            True
        )
    DB_CONNEXION.commit()


# SCRIPT
try:
    DB_CONNEXION = psycopg2.connect(config.SQLALCHEMY_DATABASE_URI)
except Exception as exp:
    print("ERREUR : connexion à la base impossible !")
    quit()

try:
    cursor = DB_CONNEXION.cursor()
    rows = runquery(cursor, config.QUERY_SELECT_CDREF, None, False)
    rows = cursor.fetchall()
except Exception as exp:
    print("ERREUR : problème lors de la récupération de la liste des cd_ref !")
    quit()


for cd_ref in rows:
    print('TAXON : cd_ref =', cd_ref[0])
    url = API_URL.format(cd_ref[0])
    r = requests.get(url)
    
    if r.status_code != 200:
        print(f"\tERREUR : l'URL {url} retourne le code HTTP {r.status_code} !")
        continue

    if '_embedded' in r.json():
        medias = r.json()['_embedded']['media']
        if not medias:
            print('\tERREUR : aucun media !')

        for media in medias:
            if media['taxon']['referenceId'] == cd_ref[0]: 
                process_media(cursor, cd_ref[0], media)
            else:
                print(f"\tERREUR : media non pris en compte car pas sur le bon taxon {media['taxon']['id']} !")

DB_CONNEXION.close()

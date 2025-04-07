# coding: utf8
"""
    Script permettant l'import de médias récupérés via l'API inpn
"""

import psycopg2
import requests

import config

# Constantes et requêtes :

QUERY_CREATE_TABLE = """
    CREATE TABLE IF NOT EXISTS taxonomie.cor_gbif_taxref (
        cd_nom integer primary key,
        id_gbif varchar(100) NOT NULL
    );
"""

QUERY_EXISTING_MATCHES = """
    SELECT COUNT(*) 
    FROM taxonomie.cor_gbif_taxref;
"""

QUERY_TRUNCATE_COR = """
    TRUNCATE TABLE taxonomie.cor_gbif_taxref;
"""

QUERY_INSERT_MATCH = """
    INSERT INTO taxonomie.cor_gbif_taxref (cd_nom, id_gbif)
    VALUES (%s, %s);
"""

# Fonctions :
class Match:
    def __init__(self, cd_nom, id_gbif):
        self.cd_nom=cd_nom
        self.id_gbif=id_gbif

    def __repr__(self):
        return "Cd_Nom: {}, Id_GBIF: {}".format(self.cd_nom, self.id_gbif)


def runquery(cur, sql, params, trap=True):
    """
    Fonction permettant d'executer une requete
    trap : Indique si les erreurs sont ou pas retournées
    """
    try:
        result = cursor.execute(sql, params)
        return result
    except Exception as exp:
        print(exp)
        if trap:
            return None
        raise exp

def get_existing_matches():
    runquery(cursor, QUERY_EXISTING_MATCHES, None, False)
    existing = cursor.fetchall()
    return existing


# Script :
try:
    DB_CONNEXION = psycopg2.connect(config.SQLALCHEMY_DATABASE_URI)
except Exception as exp:
    print("ERREUR : connexion à la base impossible !")
    quit()

try:
    cursor = DB_CONNEXION.cursor()
    runquery(cursor, config.QUERY_SELECT_CDNOMS, None, False)
    cd_noms = cursor.fetchall()
    print(len(cd_noms),"cd_noms présents dans le référentiel taxref")
except Exception as exp:
    print("ERREUR : problème lors de la récupération des cd_noms dans le référentiel taxref !")
    quit()

# Create table if not exists
try:
    cursor = DB_CONNEXION.cursor()
    runquery(cursor, QUERY_CREATE_TABLE, None, False)
    DB_CONNEXION.commit()
    print("Table de correspondances disponible, poursuite du traitement...")
except Exception as exp:
    print("ERREUR : problème lors de la création de la table de correspondances !")
    quit()

# Gestion des correspondances
try:
    cursor = DB_CONNEXION.cursor()
    # Contrôler l'existant
    runquery(cursor, QUERY_EXISTING_MATCHES, None, False)
    existing = cursor.fetchall()
    if existing[0][0] != 0:
        response=input("{} correspondances déjà disponibles. Souhaitez-vous les mettre à jour ? [O/N]".format(existing[0][0]))
        if response=="O":
            # Suppression des correspondances existantes
            runquery(cursor, QUERY_TRUNCATE_COR, None, False)
            DB_CONNEXION.commit()
        else :
            print("Conservation des correspondances existantes. Fin du traitement.")
            quit()
    # Récupération des correspondances
    print("Récupération des correspondances entre cd_nom et identifiant GBIF...")
    runquery(cursor, config.QUERY_SELECT_CDNOMS, None, False)
    cd_noms=cursor.fetchall()
    for cd_nom in cd_noms:
        API_URL="https://taxref.mnhn.fr/api/taxa/{}/externalIds".format(cd_nom[0])
        API_response = requests.get(API_URL)

        if API_response.status_code != 200:
            print(f"\tERREUR : l'URL {API_URL} retourne le code HTTP {API_response.status_code} !")
            continue

        if "_embedded" in API_response.json():
            externalDbs = API_response.json()["_embedded"]["externalDb"]
            if not externalDbs:
                print("Aucune correspondance retournée par l'API pour le cd_nom {}.".format(cd_nom[0]))

            gbif_ids=[]
            for externalDb in externalDbs:
                # Vérifier qu'il n'y a bien qu'une seule correspondance disponible
                if externalDb['externalDbName']=="GBIF":
                    gbif_ids.append(externalDb['externalId'])
                else :
                    pass
            if len(gbif_ids)==1:
                runquery(cursor, QUERY_INSERT_MATCH, (cd_nom, gbif_ids[0]), False)
                DB_CONNEXION.commit()
                print("Stockage de l'id",gbif_ids[0],"pour le cd_nom",cd_nom[0])
            else:
                # Aucune correspondance OU plusieurs correspondances possibles : pas de stockage en base
                pass
        else :
            print("Aucune correspondance unique retournée par l'API pour le cd_nom {}.".format(cd_nom[0]))
    # Contrôler les correspondances après récupération
    runquery(cursor, QUERY_EXISTING_MATCHES, None, False)
    existing = cursor.fetchall()
    print("{} correspondances ont été enregistrées. Fin du traitement.".format(existing[0][0]))

    DB_CONNEXION.close()
except Exception as exp:
    print("ERREUR : problème lors de la récupération des correspondances !")
    quit()

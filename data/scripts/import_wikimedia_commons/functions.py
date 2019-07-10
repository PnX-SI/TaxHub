
import requests
import psycopg2
from lxml import etree
import xmltodict

from SPARQLWrapper import SPARQLWrapper, JSON


def getLicence(licences):
    licence = []
    if isinstance(licences, dict):
        return licences['name']
    else:
        for i in licences:
            licence.append(i['name'])
    return '; '.join(licence)


def main(dbconnexion, cd_refs, WD_MEDIA_PROP, TAXHUB_MEDIA_ID_TYPE, refreshAtlas=True, simulate=True):
    # DbMedia Query
    cur = dbconnexion.cursor()
    query = """SELECT ?item ?itemLabel ?nomSc ?image ?identifiant_TAXREF  WHERE {
      ?item wdt:P225 ?nomSc.
      ?item wdt:%s ?image.
      ?item wdt:P3186 '%s'
     SERVICE wikibase:label { bd:serviceParam wikibase:language "fr" }
    } LIMIT 200"""
    
    # ajout paramètre agent patch des erreurs 403
    # https://www.mediawiki.org/wiki/Topic:V1zau9rqd4ritpug
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql", 
        agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
    )

    sqlI = """INSERT INTO taxonomie.t_medias
        (cd_ref, titre, url,is_public, id_type, auteur, source, licence)
        VALUES (%s, '%s', '%s', true, %s, '%s', 'Wikimedia Commons', '%s')
    """

    for cd_ref in cd_refs:
        try:
            print("Taxon %s" % cd_ref[0])
            sparql.setQuery(query % (WD_MEDIA_PROP, cd_ref[0]))
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()

            for result in results["results"]["bindings"]:
                if (result['image']['value']):
                    print(' -- INSERT MEDIAS')
                    print("     ", result['image']['value'])
                    # Recuperation des donnees sur commons
                    url = "https://tools.wmflabs.org/magnus-toolserver/commonsapi.php?image=%s" % result['image']['value'].split('Special:FilePath/', 1 )[1]

                    r = requests.get(url)
                    a = xmltodict.parse(r.content)
                    try:
                        aut = 'Commons'
                        try:
                            if len(a['response']['file']['author']) < 500:
                                aut = a['response']['file']['author']
                        except TypeError:
                            print('no author')
                            pass
                        except Exception as e:
                            print("Error during author extraction")
                            print(e)
                        
                        if aut == 'Commons':
                            try:
                                if len(a['response']['file']['uploader']) < 500:
                                    aut = a['response']['file']['uploader']
                            except TypeError:
                                print('no author')
                            except Exception as e:
                                print("Error during author extraction")
                                print(e)

                        licence = ""
                        if 'licenses' in a['response']:
                            if 'license' in a['response']['licenses']:
                                licence = getLicence(a['response']['licenses']['license'])

                        sql = sqlI % (
                            cd_ref[0],
                            a['response']['file']['name'],
                            result['image']['value'],
                            TAXHUB_MEDIA_ID_TYPE,
                            aut,
                            licence
                        )
                        if simulate is False:
                            cur.execute(sql)
                            dbconnexion.commit()
                        else:
                            print(sql)
                    except Exception as e:
                        print('         ERREOR')
                        print(e)
                        dbconnexion.rollback()
                        pass
        except Exception as e:
            print(e)
            pass

    if simulate is False:
        cur.execute("""
            UPDATE taxonomie.t_medias SET id_type = 1
            WHERE id_media IN (
                SELECT max(id_media)
                FROM taxonomie.t_medias t
                LEFT OUTER JOIN (SELECT cd_ref FROM taxonomie.t_medias WHERE id_type = 1) e
                ON t.cd_ref = e.cd_ref
                WHERE e.cd_ref IS NULL
                GROUP BY t.cd_ref
            );
        """)
        if refreshAtlas:
            cur.execute("REFRESH MATERIALIZED VIEW atlas.vm_medias;")
            cur.execute("REFRESH MATERIALIZED VIEW atlas.vm_taxons_plus_observes;")

        dbconnexion.commit()

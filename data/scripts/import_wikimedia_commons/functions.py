
import requests
import psycopg2

from SPARQLWrapper import SPARQLWrapper, JSON


def getLicence(licences):
    licence = []
    if isinstance(licences, dict):
        return licences['name']
    else:
        for i in licences:
            licence.append(i['name'])
    return '; '.join(licence)


def main(dbconnexion, cd_refs, refreshAtlas=True, simulate=True):
    # DbMedia Query
    cur = dbconnexion.cursor()
    query = """SELECT ?item ?itemLabel ?nomSc ?image ?identifiant_TAXREF  WHERE {
      ?item wdt:P225 ?nomSc.
      ?item wdt:P18 ?image.
      ?item wdt:P3186 '%s'
     SERVICE wikibase:label { bd:serviceParam wikibase:language "fr" }
    } LIMIT 200"""

    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

    sqlI = """INSERT INTO taxonomie.t_medias
        (cd_ref, titre, url,is_public, id_type, auteur, source, licence)
        VALUES (%s, '%s', '%s', true, 2, '%s', 'Wikimedia Commons', '%s')
    """

    for cd_ref in cd_refs:
        try:
            print("Taxon %s" % cd_ref[0])
            sparql.setQuery(query % cd_ref[0])
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()

            for result in results["results"]["bindings"]:
                if (result['image']['value']):
                    print(' -- INSERT IMAGE')
                    from lxml import etree
                    # Recuperation des donnees sur commons
                    url = "https://tools.wmflabs.org/magnus-toolserver/commonsapi.php?image=%s" % result['image']['value'].split('Special:FilePath/', 1 )[1]
                    r = requests.get(url)
                    import xmltodict
                    a = xmltodict.parse(r.content)
                    try:
                        aut = 'Commons'
                        if 'author' in a['response']['file']:
                            if len(a['response']['file']['author']) < 500:
                                aut = a['response']['file']['author']
                        licence = getLicence(a['response']['licenses']['license'])
                        sql = sqlI % (
                            cd_ref[0],
                            a['response']['file']['name'],
                            result['image']['value'],
                            aut,
                            licence
                        )

                        if simulate is False:
                            cur.execute(sql)
                            dbconnexion.commit()
                        else:
                            print (sql)
                    except Exception as e:
                        print('         ERREOR')
                        print(e)
                        dbconnexion.rollback()
                        pass
        except Exception as e:
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

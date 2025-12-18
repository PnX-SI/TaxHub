import requests
import xmltodict
import click
import re
from SPARQLWrapper import SPARQLWrapper, JSON


from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from apptax.database import db

from apptax.taxonomie.models import TMedias


def getLicence(licences):
    licence = []
    if isinstance(licences, dict):
        return licences["name"]
    else:
        for i in licences:
            licence.append(i["name"])
    return "; ".join(licence)


def query_api_wikimedia(cd_ref, wd_media_prop, taxhub_type_id):
    query = """SELECT ?item ?itemLabel ?nomSc ?image ?identifiant_TAXREF  WHERE {
      ?item wdt:P225 ?nomSc.
      ?item wdt:%s ?image.
      ?item wdt:P3186 '%s'
     SERVICE wikibase:label { bd:serviceParam wikibase:language "fr" }
    } LIMIT 200"""

    # ajout paramètre agent patch des erreurs 403
    # https://www.mediawiki.org/wiki/Topic:V1zau9rqd4ritpug
    sparql = SPARQLWrapper(
        "https://query.wikidata.org/sparql",
        agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
    )

    sparql.setQuery(query % (wd_media_prop, cd_ref))
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    medias = []
    for result in results["results"]["bindings"]:
        if result["image"]["value"]:
            # Recuperation des donnees sur commons
            image_value = result["image"]["value"].split("Special:FilePath/", 1)[1]
            url = f"https://tools.wmflabs.org/magnus-toolserver/commonsapi.php?image={image_value}"
            r = requests.get(url)
            a = xmltodict.parse(r.content)
            try:
                aut = "Commons"
                try:
                    if len(a["response"]["file"]["author"]) < 500:
                        aut = a["response"]["file"]["author"]
                except (TypeError, KeyError):
                    # If author is missing
                    pass
                except Exception as e:
                    click.secho(f"<--> Error during author extraction {e}", fg="blue")

                # Si pas d'auteur utilisation de l'info uploader
                if aut == "Commons":
                    try:
                        if len(a["response"]["file"]["uploader"]) < 500:
                            aut = a["response"]["file"]["uploader"]
                    except TypeError:
                        click.secho(f"<--> Error no author", fg="red")
                    except Exception as e:
                        click.secho(f"<--> Error during author extraction {e}", fg="blue")

                licence = ""
                if a["response"].get("licenses") is not None:
                    if "license" in a["response"]["licenses"]:
                        licence = getLicence(a["response"]["licenses"]["license"])

                medias.append(
                    {
                        "cd_ref": cd_ref,
                        "titre": re.sub(r"<.*?>", "", (a["response"]["file"]["name"])[0:254]),
                        "url": result["image"]["value"],
                        "is_public": True,
                        "id_type": taxhub_type_id,
                        "auteur": re.sub(r"<.*?>", "", aut),
                        "source": "Wikimedia Commons",
                        "licence": licence,
                    }
                )
            except Exception as e:
                click.secho(f"<--> Error {e}", fg="red")
    return medias


def import_inpn_wikimedia(cd_ref, wd_media_prop, taxhub_type_id):
    # DbMedia Query
    click.secho(f"Get medias for {cd_ref}", fg="green")

    medias = query_api_wikimedia(cd_ref, wd_media_prop, taxhub_type_id)
    if not medias:
        click.secho(f"<--> No medias for {cd_ref}", fg="blue")

    for media in medias:
        url = media["url"]
        try:
            # test if exists
            m_obj = TMedias.query.filter_by(url=url).one()
            click.secho(f"<--> Media already exist: {m_obj.titre}", fg="blue")
        except MultipleResultsFound:
            click.secho(
                f"<--> ERREUR {cd_ref} : l'URL du média {url} est présent plusieurs fois dans la base !",
                fg="red",
            )
        except NoResultFound:
            m_obj = TMedias(**media)

            if len(url) > 255:
                click.secho(f"<--> Url too long {url}", fg="red")
                break
            db.session.add(m_obj)
            try:
                db.session.commit()
            except Exception as e:
                click.secho(f"<--> Commit error {e}", fg="red")

            click.secho(f"<--> Add media: {m_obj.titre}", fg="green")

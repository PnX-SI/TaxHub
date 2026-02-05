import requests
import xmltodict
import click
import re

from SPARQLWrapper import SPARQLWrapper, JSON

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy import select
from apptax.database import db

from apptax.taxonomie.models import TMedias, TaxrefLiens

GBIF_API_URL = "https://api.gbif.org/v1"


def import_taxhub_media(medias, cd_ref):
    """
    Importe des médias dans la base taxhub à partir d'une liste de médias

    :param medias: liste de médias à importer
    :param cd_ref: cd_ref du taxon concerné par l'import
    """
    if not medias:
        click.secho(f"<--> No medias for {cd_ref}", fg="blue")
        return
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


def import_gbif_media_api(taxon, taxhub_type_id, nb_max=3):
    """
    Importe des médias depuis l'API de GBIF pour un taxon donné

    :param taxon: Taxon à importer
    :param taxhub_type_id: Identifiant du type de média taxhub
    :param nb_max: Nombre maximal de médias importées (sur 20 images récupérées par GBIF)
    """
    cd_ref = taxon.cd_ref
    click.secho(f"Get medias for {cd_ref}", fg="green")

    # Get gbif key
    taxon_gbif = db.session.scalar(
        select(TaxrefLiens)
        .where(TaxrefLiens.ct_name == "GBIF")
        .where(TaxrefLiens.cd_nom == cd_ref)
        .limit(1)
    )

    if not taxon_gbif:
        click.secho(f"<--> No taxref link for {cd_ref}", fg="blue")
        return

    medias = query_api_gbif_media(taxon_gbif.ct_sp_id, taxon, taxhub_type_id, nb_max)
    import_taxhub_media(medias, cd_ref)


def import_wikimedia_media_api(cd_ref, wd_media_prop, taxhub_type_id):
    """
    Importer des médias de wikidata à partir d'un cd_ref de référence

    :param cd_ref: cd_ref du taxon concerné par l'import
    :param wd_media_prop: propriété wikidata (P18 : image, P51: sons)
    :param taxhub_type_id: Identifiant du type de média taxhub
    """
    click.secho(f"Get medias for {cd_ref}", fg="green")

    medias = query_api_wikimedia(cd_ref, wd_media_prop, taxhub_type_id)
    if not medias:
        click.secho(f"<--> No medias for {cd_ref}", fg="blue")
    import_taxhub_media(medias, cd_ref)


def query_api_gbif_media(gbif_key, taxon, id_type, nb=3):
    """
    Get medias from GBIF API for a given taxon

    :param gbif_key: gbif key of the taxon
    :param taxon: Taxon to get medias for
    :param id_type: id of the type of media in taxhub
    :param nb: Number of medias to return (default to 3)
    :return: list of medias to import in taxhub
    """
    url = f"{GBIF_API_URL}/species/{gbif_key}/media?limit=20"

    gbif_response = requests.get(url)
    if gbif_response.status_code != 200:
        click.secho(f"<--> URL {url} return {gbif_response.status_code}", fg="blue")
        return

    medias = []
    for result in gbif_response.json()["results"]:
        if result["type"] == "StillImage" and not result.get("audience") == "biologists":

            if result.get("title"):
                titre = result["title"][0:254]
            else:
                titre = taxon.nom_complet
            medias.append(
                {
                    "cd_ref": taxon.cd_ref,
                    "titre": titre,
                    "url": result["identifier"],
                    "is_public": True,
                    "id_type": id_type,
                    "auteur": result.get("rightsHolder"),
                    "source": (result.get("source") + " Via GBIF API").strip(),
                    "licence": result.get("license"),
                }
            )
        if len(medias) > nb - 1:
            return medias
    return medias


def get_licence_wikimedia(licences):
    licence = []
    if isinstance(licences, dict):
        return licences["name"]
    else:
        for i in licences:
            licence.append(i["name"])
    return "; ".join(licence)


def query_api_wikimedia(cd_ref, wd_media_prop, taxhub_type_id):
    """
    Récupère les médias depuis l'API de Wikidata pour un taxon donné

    :param cd_ref: cd_ref du taxon à importer
    :param wd_media_prop: propriété wikidata (P18 : image, P51 : sons)
    :param taxhub_type_id: Identifiant du type de média taxhub
    :return: liste des médias importées
    """

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
                        licence = get_licence_wikimedia(a["response"]["licenses"]["license"])

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

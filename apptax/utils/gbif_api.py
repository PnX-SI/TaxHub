import requests
import click

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy import select
from apptax.database import db

from apptax.taxonomie.models import TMedias, BibTypesMedia, TaxrefLiens


API_URL = "https://api.gbif.org/v1"


def get_gbif_media(gbif_key, taxon, id_type, nb=3):
    url = f"{API_URL}/species/{gbif_key}/media?limit=20"

    gbif_response = requests.get(url)
    print(url)
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
                    "source": result.get("source") or "GBIF",
                    "licence": result.get("license"),
                }
            )
        if len(medias) > nb - 1:
            return medias
    return medias


def import_gbif_media(taxon, taxhub_type_id, nb_max=3):

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

    medias = get_gbif_media(taxon_gbif.ct_sp_id, taxon, taxhub_type_id, nb_max)
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

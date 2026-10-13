import click
import csv

from flask.cli import with_appcontext
from sqlalchemy import select, func, text
from sqlalchemy.orm.exc import NoResultFound


from apptax.database import db
from apptax.taxonomie.commands.migrate_taxref.commands_v15 import migrate_to_v15
from apptax.taxonomie.commands.migrate_taxref.commands_v16 import migrate_to_v16
from apptax.taxonomie.commands.migrate_taxref.commands_v17 import migrate_to_v17
from apptax.taxonomie.commands.migrate_taxref.commands_v18 import migrate_to_v18
from apptax.taxonomie.models import Taxref, BibTypesMedia

from .utils import truncate_bdc_statuts
from .taxref_v14 import import_v14, import_bdc_v14
from .taxref_v15_v16 import (
    import_bdc_v17,
    import_v15,
    import_bdc_v15,
    import_v17,
    link_bdc_statut_to_areas,
    enable_bdc_statut_text,
    import_v16,
    import_bdc_v16,
)
from .taxref_v18 import import_v18, import_bdc_v18
from .migrate_taxref.test_commands_migrate import test_migrate_taxref

from apptax.taxonomie.models import Taxref
from apptax.taxonomie.repositories import TaxrefInfoRepository

import logging

logger = logging.getLogger("taxref_commands")


@click.group(help="Manager TaxRef referentials.")
def taxref():
    pass


@taxref.command()
@with_appcontext
def info():
    taxref_info = TaxrefInfoRepository.getTaxrefInfo()
    click.echo("TaxRef :")
    click.echo(
        f"\tVersion de taxref : {taxref_info['taxref_version'].version} ({taxref_info['taxref_version'].update_date})"
    )
    click.echo(f"\tNombre de taxons : {taxref_info['taxref_count']}")
    click.echo("Base de connaissances :")
    click.echo(
        f"\tStatuts (actifs / total) : {taxref_info['enabled_status_count']} / {taxref_info['status_count']}"
    )


@taxref.command(help="Supprimer toutes les données TaxRef.")
@with_appcontext
def delete():
    click.confirm("Êtes vous sûr de vouloir supprimer toutes les données TaxRef ?", abort=True)
    tables = [
        "taxonomie.bdc_statut",
        "taxonomie.bdc_statut_values",
        "taxonomie.bdc_statut_taxons",
        "taxonomie.bdc_statut_cor_text_area",
        "taxonomie.bdc_statut_cor_text_values",
        "taxonomie.bdc_statut_text",
        "taxonomie.bdc_statut_type",
        "taxonomie.cor_nom_liste",
        "taxonomie.cor_taxon_attribut",
        "taxonomie.taxref",
        "taxonomie.bib_taxref_statuts",
        "taxonomie.bib_taxref_rangs",
        "taxonomie.bib_taxref_habitats",
        "taxonomie.t_meta_taxref",
    ]
    with click.progressbar(
        length=len(tables), label="Delete from table", item_show_func=lambda t: t, show_eta=False
    ) as bar:
        for i, table in enumerate(tables):
            bar.update(n_steps=i, current_item=table)
            db.session.execute(text(f"DELETE FROM {table}"))

    db.session.commit()


@taxref.command(help="Supprimer la base de connaissance des statuts de protection.")
@with_appcontext
def delete_bdc():
    click.confirm(
        "Êtes vous sûr de vouloir supprimer toutes les données de la BDC Statuts ?",
        abort=True,
    )
    truncate_bdc_statuts()
    db.session.commit()


@taxref.command(
    help="Importer des médias de l'INPN TaxRef à partir d'une liste de cd_ref de référence."
)
@click.argument("file", type=click.Path(exists=True))
@with_appcontext
def import_inpn_media(file):
    """
    Importer des médias de l'INPN TaxRef à partir d'une liste de cd_ref de référence
    Le fichier doit contenir une colonne avec la liste des cd_ref à traiter
    """
    from apptax.utils.taxref_api import import_inpn_media

    with open(file, "r") as file:
        csvreader = csv.reader(file)
        for row in csvreader:
            value = row[0]
            if value in ("cd_nom", "cd_ref"):
                continue

            # Get Taxon
            try:
                taxon = db.session.get(Taxref, int(value))
            except (NoResultFound, ValueError):
                logger.error(f"{value} is not a valid cd_ref")
                continue

            import_inpn_media(taxon.cd_ref, taxon.cd_nom, logger)


@taxref.command(
    help="Importer des médias de wikidata à partir d'une liste de cd_ref de référence."
)
@click.argument("file", type=click.Path(exists=True))
@click.option(
    "--wd-media-prop",
    type=str,
    default="P18",
    help="Code de la propriété wikidata (P18 : image, P51: sons)",
)
@click.option("--media-type-id", type=int, default=2, help="Code du type de média taxhub")
@with_appcontext
def import_wikidata_media(file, wd_media_prop, media_type_id):
    """
    Importer des médias de wikidata à partir d'une liste de cd_ref de référence
    Le fichier doit contenir une colonne avec la liste des cd_ref à traiter
    """
    # Constantes type de média et id_type média
    # Images
    # WD_MEDIA_PROP = "P18"
    # TAXHUB_MEDIA_ID_TYPE = "2"
    # Audios
    # # WD_MEDIA_PROP='P51'
    # # TAXHUB_MEDIA_ID_TYPE='5'

    from apptax.utils.external_apis import import_wikimedia_media_api

    # test media type
    media_type = db.session.scalar(
        select(BibTypesMedia).where(BibTypesMedia.id_type == media_type_id)
    )
    if not media_type:
        logger.error(f"{media_type_id} is not a valid media type")
        raise click.ClickException("Invalid media type")

    with open(file, "r") as file:
        csvreader = csv.reader(file)
        for row in csvreader:
            value = row[0]
            if value in ("cd_nom", "cd_ref"):
                continue

            # Get Taxon
            try:
                taxon = db.session.scalar(select(Taxref).where(Taxref.cd_nom == int(value)))
            except (NoResultFound, ValueError):
                logger.error(f"{value} is not a valid cd_ref")
                continue
            import_wikimedia_media_api(taxon.cd_ref, wd_media_prop, media_type_id)


@taxref.command(help="Importer des médias de GBIF à partir d'une liste de cd_ref de référence.")
@click.argument("file", type=click.Path(exists=True))
@click.option("--media-type-id", type=int, default=2, help="Code du type de média taxhub")
@click.option(
    "--nb-max",
    type=int,
    default=3,
    help="Nombre maximal de média importé (sur 20 images récupérés)",
)
@with_appcontext
def import_gbif_media(file, media_type_id, nb_max):
    """
    Importer des médias de wikidata à partir d'une liste de cd_ref de référence
    Le fichier doit contenir une colonne avec la liste des cd_ref à traiter
    """
    from apptax.utils.external_apis import import_gbif_media_api

    # test media type
    media_type = db.session.scalar(
        select(BibTypesMedia).where(BibTypesMedia.id_type == media_type_id)
    )
    if not media_type:
        logger.error(f"{media_type_id} is not a valid media type")
        raise click.ClickException("Invalid media type")

    with open(file, "r") as file:
        csvreader = csv.reader(file)
        for row in csvreader:
            value = row[0]
            if value in ("cd_nom", "cd_ref"):
                continue
            # Get Taxon
            try:
                taxon = db.session.scalar(select(Taxref).where(Taxref.cd_nom == int(value)))
            except (NoResultFound, ValueError):
                logger.error(f"{value} is not a valid cd_ref")
                continue
            import_gbif_media_api(taxon, media_type_id, nb_max)


taxref.add_command(import_v14)
taxref.add_command(import_bdc_v14)
taxref.add_command(import_v15)
taxref.add_command(import_bdc_v15)
taxref.add_command(import_v16)
taxref.add_command(import_v17)
taxref.add_command(import_v18)
taxref.add_command(import_bdc_v16)
taxref.add_command(import_bdc_v17)
taxref.add_command(import_bdc_v18)
taxref.add_command(migrate_to_v15)
taxref.add_command(migrate_to_v16)
taxref.add_command(migrate_to_v17)
taxref.add_command(test_migrate_taxref)
taxref.add_command(link_bdc_statut_to_areas)
taxref.add_command(enable_bdc_statut_text)
taxref.add_command(import_inpn_media)
taxref.add_command(import_wikidata_media)
taxref.add_command(import_gbif_media)

taxref.add_command(migrate_to_v18)

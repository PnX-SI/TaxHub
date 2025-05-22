import click
import csv

from flask.cli import with_appcontext
from sqlalchemy import select, func
from sqlalchemy.orm.exc import NoResultFound


from apptax.database import db
from apptax.taxonomie.commands.migrate_taxref.commands_v15 import migrate_to_v15
from apptax.taxonomie.commands.migrate_taxref.commands_v16 import migrate_to_v16
from apptax.taxonomie.commands.migrate_taxref.commands_v17 import migrate_to_v17
from apptax.taxonomie.commands.migrate_taxref.commands_v18 import migrate_to_v18
from apptax.taxonomie.models import Taxref, TaxrefBdcStatutText, TMetaTaxref

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

import logging

logger = logging.getLogger("taxref_commands")


@click.group(help="Manager TaxRef referentials.")
def taxref():
    pass


@taxref.command()
@with_appcontext
def info():
    click.echo("TaxRef :")
    taxref_version = db.session.scalar(
        select(TMetaTaxref).order_by(TMetaTaxref.update_date.desc()).limit(1)
    )

    click.echo(f"\tVersion de taxref : {taxref_version.version} ({taxref_version.update_date})")
    taxref_count = db.session.scalar(db.select(func.count(Taxref.cd_nom)))
    click.echo(f"\tNombre de taxons : {taxref_count}")
    status_count = db.session.scalar(db.select(func.count(TaxrefBdcStatutText.id_text)))
    enabled_status_count = db.session.scalar(
        select(func.count(TaxrefBdcStatutText.id_text)).where(TaxrefBdcStatutText.enable == True)
    )
    click.echo("Base de connaissances :")
    click.echo(f"\tStatuts (actifs / total) : {enabled_status_count} / {status_count}")


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
            db.session.execute(f"DELETE FROM {table}")

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
                taxon = Taxref.query.get(int(value))
            except (NoResultFound, ValueError):
                logger.error(f"{value} is not a valid cd_ref")
                continue

            import_inpn_media(taxon.cd_ref, taxon.cd_nom, logger)


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

taxref.add_command(migrate_to_v18)

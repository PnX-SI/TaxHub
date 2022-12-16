import logging
import importlib.resources
from zipfile import ZipFile

import click
import sqlalchemy as sa
from sqlalchemy.schema import Table, MetaData
from flask.cli import with_appcontext

from utils_flask_sqla.migrations.utils import open_remote_file

from apptax.database import db
from apptax.taxonomie.commands.utils import copy_from_csv, refresh_taxref_vm, import_bdc_statuts


base_url = "http://geonature.fr/data/inpn/taxonomie/"


def import_bdc_statuts_v14(logger):
    import_bdc_statuts(
        logger,
        base_url,
        "BDC-Statuts-v14.zip",
        "BDC-Statuts-v14/BDC_STATUTS_TYPES_14.csv",
        "BDC-Statuts-v14/BDC_STATUTS_14.csv",
    )


@click.command()
@click.option("--skip-bdc-statuts", is_flag=True, help="Skip import of BDC Statuts")
@with_appcontext
def import_v14(skip_bdc_statuts):
    logger = logging.getLogger()
    bind = db.session.get_bind()
    metadata = MetaData(bind=bind)
    cursor = bind.raw_connection().cursor()
    with open_remote_file(base_url, "TAXREF_v14_2020.zip", open_fct=ZipFile) as archive:
        with archive.open("TAXREF_v14_2020/habitats_note.csv") as f:
            logger.info("Insert TAXREFv14 habitats…")
            copy_from_csv(f, "bib_taxref_habitats", encoding="WIN1252", delimiter=";")
        with archive.open("TAXREF_v14_2020/rangs_note.csv") as f:
            logger.info("Insert TAXREFv14 rangs…")
            copy_from_csv(
                f,
                "bib_taxref_rangs",
                delimiter="\t",
                dest_cols=("tri_rang", "id_rang", "nom_rang", "nom_rang_en"),
            )
        with archive.open("TAXREF_v14_2020/statuts_note.csv") as f:
            logger.info("Insert TAXREFv14 statuts…")
            copy_from_csv(
                f,
                "bib_taxref_statuts",
                encoding="WIN1252",
                delimiter=";",
                dest_cols=("id_statut", "nom_statut"),
                source_cols=("statut", "description"),
            )
        with archive.open("TAXREF_v14_2020/TAXREFv14.txt") as f:
            logger.info("Insert TAXREFv14 referentiel…")
            copy_from_csv(
                f,
                "taxref",
                delimiter="\t",
                dest_cols=(
                    "cd_nom",
                    "id_statut",
                    "id_habitat",
                    "id_rang",
                    "regne",
                    "phylum",
                    "classe",
                    "ordre",
                    "famille",
                    "sous_famille",
                    "tribu",
                    "cd_taxsup",
                    "cd_sup",
                    "cd_ref",
                    "lb_nom",
                    "lb_auteur",
                    "nom_complet",
                    "nom_complet_html",
                    "nom_valide",
                    "nom_vern",
                    "nom_vern_eng",
                    "group1_inpn",
                    "group2_inpn",
                    "url",
                ),
                source_cols=(
                    "cd_nom::int",
                    "fr as id_statut",
                    "habitat::int as id_habitat",
                    "rang as id_rang",
                    "regne",
                    "phylum",
                    "classe",
                    "ordre",
                    "famille",
                    "sous_famille",
                    "tribu",
                    "cd_taxsup::int",
                    "cd_sup::int",
                    "cd_ref::int",
                    "lb_nom",
                    "substring(lb_auteur, 1, 250)",
                    "nom_complet",
                    "nom_complet_html",
                    "nom_valide",
                    "substring(nom_vern,1,1000)",
                    "nom_vern_eng",
                    "group1_inpn",
                    "group2_inpn",
                    "url",
                ),
            )

    if not skip_bdc_statuts:
        import_bdc_statuts_v14(logger)
    else:
        logger.info("Skipping BDC statuts.")

    logger.info("Refresh materialized views…")
    refresh_taxref_vm()

    logger.info("Committing…")
    db.session.commit()


@click.command()
@with_appcontext
def import_bdc_v14():
    logger = logging.getLogger()
    import_bdc_statuts_v14(logger)
    db.session.commit()

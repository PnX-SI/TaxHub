import os
import logging
from zipfile import ZipFile

import click
from sqlalchemy.schema import MetaData
from flask.cli import with_appcontext

from utils_flask_sqla.migrations.utils import open_remote_file

from ref_geo.models import LAreas, BibAreasTypes

from apptax.database import db
from apptax.taxonomie.commands.utils import (
    copy_from_csv,
    refresh_taxref_vm,
    import_bdc_statuts,
    insert_taxref_numversion,
)


base_url = "http://geonature.fr/data/inpn/taxonomie/"


def import_bdc_statuts_v18(logger):
    import_bdc_statuts(
        logger,
        base_url,
        "BDC-STATUTS-v18.zip",
        "BDC_STATUTS_TYPES_18.csv",
        "bdc_statuts_18.csv",
    )


def import_taxref(logger, num_version, taxref_archive_name, taxref_file_name, taxref_region="fr"):
    with open_remote_file(base_url, taxref_archive_name, open_fct=ZipFile) as archive:
        with archive.open("habitats_note.csv") as f:
            logger.info(f"Insert TAXREF v{num_version} habitats…")
            copy_from_csv(f, "bib_taxref_habitats", encoding="WIN1252", delimiter=";")
        with archive.open("rangs_note.csv") as f:
            logger.info(f"Insert TAXREF v{num_version} rangs…")
            copy_from_csv(
                f,
                "bib_taxref_rangs",
                encoding="WIN1252",
                delimiter=";",
                dest_cols=("tri_rang", "id_rang", "nom_rang", "nom_rang_en"),
            )
        with archive.open("statuts_note.csv") as f:
            logger.info(f"Insert TAXREF v{num_version} statuts…")
            copy_from_csv(
                f,
                "bib_taxref_statuts",
                encoding="WIN1252",
                delimiter=";",
                dest_cols=("id_statut", "nom_statut"),
                source_cols=("statut", "description"),
            )
        with archive.open(taxref_file_name) as f:
            logger.info(f"Insert TAXREF v{num_version} referentiel…")
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
                    "cd_ba",
                    "lb_nom",
                    "lb_auteur",
                    "nomenclatural_comment",
                    "nom_complet",
                    "nom_complet_html",
                    "nom_valide",
                    "nom_vern",
                    "nom_vern_eng",
                    "group1_inpn",
                    "group2_inpn",
                    "group3_inpn",
                    "url",
                ),
                source_cols=(
                    "cd_nom::int",
                    f"NULLIF({taxref_region}, '') as id_statut",
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
                    "cd_ba::int",
                    "lb_nom",
                    "substring(lb_auteur, 1, 250)",
                    "nomenclatural_comment",
                    "nom_complet",
                    "nom_complet_html",
                    "nom_valide",
                    "substring(nom_vern,1,1000)",
                    "nom_vern_eng",
                    "group1_inpn",
                    "group2_inpn",
                    "group3_inpn",
                    "url",
                ),
            )
        with archive.open("TAXREF_LIENS.txt") as f:
            logger.info(f"Insert TAXREF v{num_version} liens...")
            copy_from_csv(
                f,
                "taxref_liens",
                delimiter="\t",
                dest_cols=(
                    "ct_name",
                    "ct_type",
                    "ct_authors",
                    "ct_title",
                    "ct_url",
                    "cd_nom",
                    "ct_sp_id",
                    "url_sp",
                ),
                source_cols=(
                    "ct_name",
                    "ct_type",
                    "ct_authors",
                    "ct_title",
                    "ct_url",
                    "cd_nom::int as cd_nom",
                    "ct_sp_id",
                    "url_sp",
                ),
            )
    insert_taxref_numversion(num_version)
    db.session.commit()


@click.command()
@click.option("--skip-bdc-statuts", is_flag=True, help="Skip import of BDC Statuts")
@click.option("--taxref-region", type=str, default="fr", help="Taxref region : column status")
@with_appcontext
def import_v18(skip_bdc_statuts, taxref_region):
    logger = logging.getLogger()

    import_taxref(
        logger,
        num_version="18",
        taxref_archive_name="TAXREF_v18_2025.zip",
        taxref_file_name="TAXREFv18.txt",
        taxref_region=taxref_region,
    )

    if not skip_bdc_statuts:
        import_bdc_statuts_v18(logger)
    else:
        logger.info("Skipping BDC statuts.")

    logger.info("Refresh materialized views…")
    refresh_taxref_vm()

    logger.info("Committing…")
    db.session.commit()


@click.command()
@with_appcontext
def import_bdc_v18():
    logger = logging.getLogger()
    import_bdc_statuts_v18(logger)
    db.session.commit()

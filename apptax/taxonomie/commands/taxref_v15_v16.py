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
    populate_bdc_statut_cor_text_area,
    populate_enable_bdc_statut_text,
)
from apptax.taxonomie.models import Taxref


base_url = "http://geonature.fr/data/inpn/taxonomie/"


def import_bdc_statuts_v15(logger):
    import_bdc_statuts(
        logger,
        base_url,
        "BDC-statuts-15.zip",
        "BDC_STATUTS_TYPES_15.csv",
        "BDC_STATUTS_15.csv",
    )


def import_bdc_statuts_v16(logger):
    import_bdc_statuts(
        logger,
        base_url,
        "BDC-Statuts-v16.zip",
        "BDC_STATUTS_TYPES_16.csv",
        "BDC_STATUTS_16.csv",
    )


def import_taxref(logger, num_version, taxref_archive_name, taxref_file_name):
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
                    "lb_nom",
                    "lb_auteur",
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
                    "NULLIF(fr, '') as id_statut",
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
                    "group3_inpn",
                    "url",
                ),
            )


@click.command()
@click.option("--skip-bdc-statuts", is_flag=True, help="Skip import of BDC Statuts")
@with_appcontext
def import_v15(skip_bdc_statuts):
    logger = logging.getLogger()

    import_taxref(
        logger,
        num_version="15",
        taxref_archive_name="TAXREF_v15_2021.zip",
        taxref_file_name="TAXREFv15.txt",
    )

    if not skip_bdc_statuts:
        import_bdc_statuts_v15(logger)
    else:
        logger.info("Skipping BDC statuts.")

    logger.info("Refresh materialized views…")
    refresh_taxref_vm()

    logger.info("Committing…")
    db.session.commit()


@click.command()
@click.option("--skip-bdc-statuts", is_flag=True, help="Skip import of BDC Statuts")
@with_appcontext
def import_v16(skip_bdc_statuts):
    logger = logging.getLogger()

    import_taxref(
        logger,
        num_version="16",
        taxref_archive_name="TAXREF_v16_2022.zip",
        taxref_file_name="TAXREFv16.txt",
    )

    if not skip_bdc_statuts:
        import_bdc_statuts_v16(logger)
    else:
        logger.info("Skipping BDC statuts.")

    logger.info("Refresh materialized views…")
    refresh_taxref_vm()

    logger.info("Committing…")
    db.session.commit()


@click.command()
@with_appcontext
def import_bdc_v15():
    logger = logging.getLogger()
    import_bdc_statuts_v15(logger)
    db.session.commit()


@click.command()
@with_appcontext
def import_bdc_v16():
    logger = logging.getLogger()
    import_bdc_statuts_v16(logger)
    db.session.commit()


@click.command()
@with_appcontext
def link_bdc_statut_to_areas():
    """Insert or update table bdc_statut_cor_text_area"""
    logger = logging.getLogger()
    # test ref_geo.l_areas departements is populated
    q = db.session.query(
        LAreas.query.filter(LAreas.area_type.has(BibAreasTypes.type_code == "DEP")).exists()
    )
    deps_present = q.scalar()
    if not deps_present:
        logger.error(
            "Departements is not populated run 'flask db upgrade ref_geo_fr_departments@head' before…"
        )
        return
    # test taxonomie.taxref is populated
    nb_taxref = Taxref.query.count()
    if nb_taxref == 0:
        logger.error("Taxref is not populated run 'flask taxref import-v16' before…")
        return
    # Populate bdc_statut_cor_text_area
    populate_bdc_statut_cor_text_area(logger)
    db.session.commit()
    logger.info("done")


@click.command()
@click.option("--clean", is_flag=True, help="Disable all text of BDC Statuts before")
@click.option(
    "--dept", "-d", multiple=True, help="Code of departement. You can set multiple departments"
)
@with_appcontext
def enable_bdc_statut_text(clean, dept):
    """Enable texts of BDC Statuts for departements"""
    logger = logging.getLogger()
    populate_enable_bdc_statut_text(logger, clean, dept)
    db.session.commit()
    logger.info("done")

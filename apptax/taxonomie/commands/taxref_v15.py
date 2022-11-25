import logging
import importlib.resources
from zipfile import ZipFile

import click
import sqlalchemy as sa
from sqlalchemy import func
from sqlalchemy.schema import Table, MetaData
from flask.cli import with_appcontext

from utils_flask_sqla.migrations.utils import open_remote_file

from ref_geo.models import LAreas

from apptax.database import db
from apptax.taxonomie.commands.utils import (
    copy_from_csv,
    refresh_taxref_vm,
    import_bdc_statuts,
    insert_bdc_statut_cor_text_area,
)
from apptax.taxonomie.models import Taxref

base_url = "http://geonature.fr/data/inpn/taxonomie/"


@click.command()
@click.option("--skip-bdc-statuts", is_flag=True, help="Skip import of BDC Statuts")
@with_appcontext
def import_v15(skip_bdc_statuts):
    logger = logging.getLogger()
    bind = db.session.get_bind()
    metadata = MetaData(bind=bind)
    cursor = bind.raw_connection().cursor()
    with open_remote_file(base_url, "TAXREF_v15_2021.zip", open_fct=ZipFile) as archive:
        with archive.open("habitats_note.csv") as f:
            logger.info("Insert TAXREFv15 habitats…")
            copy_from_csv(f, "bib_taxref_habitats", encoding="WIN1252", delimiter=";")
        with archive.open("rangs_note.csv") as f:
            logger.info("Insert TAXREFv15 rangs…")
            copy_from_csv(
                f,
                "bib_taxref_rangs",
                encoding="WIN1252",
                delimiter=";",
                dest_cols=("tri_rang", "id_rang", "nom_rang", "nom_rang_en"),
            )
        with archive.open("statuts_note.csv") as f:
            logger.info("Insert TAXREFv15 statuts…")
            copy_from_csv(
                f,
                "bib_taxref_statuts",
                encoding="WIN1252",
                delimiter=";",
                dest_cols=("id_statut", "nom_statut"),
                source_cols=("statut", "description"),
            )
        with archive.open("TAXREFv15.txt") as f:
            logger.info("Insert TAXREFv15 referentiel…")
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

    if not skip_bdc_statuts:
        import_bdc_statuts(
            logger,
            base_url,
            "BDC-statuts-15.zip",
            "BDC_STATUTS_TYPES_15.csv",
            "BDC_STATUTS_15.csv",
        )
    else:
        logger.info("Skipping BDC statuts.")

    logger.info("Refresh materialized views…")
    refresh_taxref_vm()

    logger.info("Committing…")
    db.session.commit()


@click.command()
@with_appcontext
def populate_bdc_statut_cor_text_area():
    """Insert or update table bdc_statut_cor_text_area"""
    logger = logging.getLogger()
    # test ref_geo.l_areas departements is populated
    nb_deps = LAreas.query.filter(LAreas.id_type == func.ref_geo.get_id_area_type("DEP")).count()
    if nb_deps == 0:
        logger.error(
            "Departements is not populated run 'flask db upgrade ref_geo_fr_departments@head' before…"
        )
        return
    # test taxonomie.taxref is populated
    nb_taxref = Taxref.query.count()
    if nb_taxref == 0:
        logger.error("Taxref is not populated run 'flask taxref import-v15' before…")
        return
    insert_bdc_statut_cor_text_area(logger)
    logger.info("done")

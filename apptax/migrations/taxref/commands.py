from flask import Blueprint

import importlib
import click
from zipfile import ZipFile
from sqlalchemy import text
from utils_flask_sqla.migrations.utils import open_remote_file

from apptax.database import db
from .utils import test_missing_cd_nom, save_data, process_bib_noms, detect_changes, copy_from_csv
from . import logger

routes = Blueprint("taxref_migration", __name__, cli_group="taxref_migration")


base_url = "http://geonature.fr/data/inpn/taxonomie/"


@routes.cli.command()
def update_taxref_v15():
    """
    Procédure de migration de taxref
        Taxref v14 vers v15
        Test de la disparition des cd_noms
    """
    # Prerequis : deps_test_fk_dependencies_cd_nom
    query = text(
        importlib.resources.read_text(
            "apptax.migrations.data.migrate_taxref_version",
            "0.2_taxref_detection_repercussion_disparition_cd_nom.sql",
        )
    )
    db.session.execute(query)

    # import taxref v15 data
    import_taxref_v15()

    # test if deleted cd_nom can be correct without manual intervention
    if test_missing_cd_nom():
        logger.error("Some cd_nom will disappear without substitute. You can't continue")
        # TODO ??? Force exit or not ???
        exit()

    # Test missing cd_nom
    process_bib_noms()

    # Change detection and repport
    detect_changes()


@routes.cli.command()
@click.option("--keep-oldtaxref", is_flag=True)
@click.option("--keep-oldbdc", is_flag=True)
def apply_changes(keep_taxref, keep_bdc):
    """Procédure de migration de taxref
         Taxref v14 vers v15
         Application des changements
    :param keep_taxref: Indique si l'on souhaite concerver l'ancienne version du referentiel taxref
    :type keep_taxref: boolean
    :param keep_bdc:  Indique si l'on souhaite concerver l'ancienne version du referentiel bdc_status
    :type keep_bdc: boolean
    """

    # test if deleted cd_nom can be correct without manual intervention
    if test_missing_cd_nom():
        logger.error("Some cd_nom will disappear without substitute. You can't continue")
        # TODO ??? Force exit or not ???
        exit()

    # Change detection and repport
    nb_of_conflict = detect_changes()
    # si conflit > 1 exit()
    if nb_of_conflict > 1:
        logger.error(f"There is {nb_of_conflict} unresolved conflits. You can't continue")
        # TODO ??? Force exit or not ???
        exit()

    # Save taxref and bdc_status data
    save_data(14, keep_taxref, keep_bdc)

    # Update taxref v15
    logger.info("Migration of taxref ...")
    try:
        query = text(
            importlib.resources.read_text(
                "apptax.migrations.data.migrate_taxref_version", "3.2_alter_taxref_data.sql"
            )
        )
        db.session.execute(query)
        db.session.commit()
        logger.info("it's done")
    except Exception as e:
        logger.error(str(e))

    # Import bdc status data and insert into taxhub tables
    import_and_format_dbc_status()

    # Clean DB
    logger.info("Clean DB")
    query = text(
        importlib.resources.read_text(
            "apptax.migrations.data.migrate_taxref_version", "5_clean_db.sql"
        )
    )
    db.session.execute(query)

    db.session.commit()


def import_taxref_v15():
    """
    Import des données brutes de taxref v15 en base
    avant leur traitement
    """

    logger.info("Import TAXREFv15 into tmp table…")

    # Préparation création de table temporaire permettant d'importer taxref
    for sqlfile in [
        "0_taxrefv15_import_data.sql",
    ]:
        query = text(
            importlib.resources.read_text("apptax.migrations.data.migrate_taxref_version", sqlfile)
        )
        db.session.execute(query)
    db.session.commit()

    with open_remote_file(
        base_url, "TAXREF_v15_2021.zip", open_fct=ZipFile, data_dir="/home/sahl/dev/TaxHub/tmp"
    ) as archive:
        with archive.open("TAXREFv15.txt") as f:
            logger.info("Insert TAXREFv15 tmp table…")
            copy_from_csv(
                f,
                db.engine,
                table_name="cdnom_disparu",
                schema_name="taxonomie",
                header=True,
                encoding=None,
                delimiter="\t",
                dest_cols="",
            )
        with archive.open("CDNOM_DISPARUS.csv") as f:
            logger.info("Insert cdnom_disparu tmp table…")
            copy_from_csv(
                f,
                db.engine,
                table_name="cdnom_disparu",
                schema_name="taxonomie",
                header=True,
                encoding=None,
                delimiter=",",
                dest_cols="",
            )

        # No changes in taxref v15
        # with archive.open('rangs_note.csv') as f:
        #     logger.info("Insert rangs_note tmp table…")
        #     copy_from_csv(f, db.engine,
        #         table_name="import_taxref_rangs", schema_name="taxonomie",
        #         header=True, encoding="WIN1252", delimiter=";", dest_cols=''
        #     )


def import_and_format_dbc_status():
    """
    Import des données brutes de la base bdc_status  en base
    Puis traitement des données de façon à les ventiler dans les différentes tables
    """

    import_data_dbc_status_15()
    # Delete doublons
    logger.info("Remove duplicate bdc_statut")
    db.session.execute(
        text(
            """
        --- Suppression des données en double contenu dans la table  bdc_statut
        CREATE INDEX bdc_statut_id_idx ON taxonomie.bdc_statut (id);

        WITH d AS (
            SELECT
                count(*), min(id), array_agg(id)
            FROM taxonomie.bdc_statut
            GROUP BY
                cd_nom, cd_ref, cd_sup, cd_type_statut, lb_type_statut, regroupement_type, code_statut, label_statut, rq_statut,
                cd_sig, cd_doc, lb_nom, lb_auteur, nom_complet_html, nom_valide_html, regne, phylum, classe, ordre, famille, group1_inpn,
                group2_inpn, lb_adm_tr, niveau_admin, cd_iso3166_1, cd_iso3166_2, full_citation, doc_url, thematique, type_value
            HAVING count(*) >1
        ) , id_doublon AS (
            SELECT min, unnest(array_agg) as to_del
            FROM d
        )
        DELETE
        FROM  taxonomie.bdc_statut s
        USING id_doublon d
        WHERE s.id = d.to_del and not id = min;

        DROP INDEX taxonomie.bdc_statut_id_idx;

    """
        )
    )

    # Structure BDC_Statut
    logger.info("Import raw bdc_statut into structured table")
    query = text(
        importlib.resources.read_text("apptax.migrations.data", "taxonomie_bdc_statuts.sql")
    )
    db.session.execute(query)


def import_data_dbc_status_15():
    """
    Import des données brutes de la base bdc_status v14  en base
    """
    db.session.execute(
        text(
            """
        TRUNCATE TABLE  taxonomie.bdc_statut_type CASCADE;
        TRUNCATE TABLE  taxonomie.bdc_statut;
    """
        )
    )
    db.session.commit()

    with open_remote_file(
        base_url, "BDC-statuts-15.zip", open_fct=ZipFile, data_dir="/home/sahl/dev/TaxHub/tmp"
    ) as archive:
        with archive.open("BDC_STATUTS_TYPES_15.csv") as f:
            logger.info("Insert BDC_STATUTS_TYPES_15 table…")
            copy_from_csv(
                f,
                db.engine,
                table_name="bdc_statut_type",
                schema_name="taxonomie",
                header=True,
                encoding=None,
                delimiter=",",
                dest_cols="",
            )
        with archive.open("BDC_STATUTS_15.csv") as f:
            logger.info("Insert bdc_statut table…")
            copy_from_csv(
                f,
                db.engine,
                table_name="bdc_statut",
                schema_name="taxonomie",
                header=True,
                encoding="WIN1252",
                delimiter=",",
                dest_cols="(cd_nom, cd_ref, cd_sup, cd_type_statut, lb_type_statut, regroupement_type, code_statut, label_statut, rq_statut, cd_sig, cd_doc, lb_nom, lb_auteur, nom_complet_html, nom_valide_html, regne, phylum, classe, ordre, famille, group1_inpn, group2_inpn, lb_adm_tr, niveau_admin, cd_iso3166_1, cd_iso3166_2, full_citation, doc_url, thematique, type_value)",
            )

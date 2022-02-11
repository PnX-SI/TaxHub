import csv
import importlib
from pathlib import Path
from zipfile import ZipFile
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError


from apptax.database import db
from . import logger
from .queries import (
    EXPORT_QUERIES_MISSING_CD_NOMS_IN_BIB_NOMS,
    EXPORT_QUERIES_MISSING_CD_NOM_GN2_SYNTHESE,
    EXPORT_QUERIES_MISSING_CD_NOMS_IN_DB,
    EXPORT_QUERIES_MODIFICATION_NB,
    EXPORT_QUERIES_MODIFICATION_LIST,
    EXPORT_QUERIES_CONFLICTS,
)


def process_bib_noms():
    """
    Création d'une table copie de bib_noms
    """
    logger.info("Create working copy of bib_noms…")

    # Préparation création de table temporaire permettant d'importer taxref
    for sqlfile in [
        "0.1_generate_tmp_bib_noms_copy.sql",
    ]:
        query = text(
            importlib.resources.read_text("apptax.migrations.data.migrate_taxref_version", sqlfile)
        )
        db.session.execute(query)
    db.session.commit()


def detect_changes(script_predetection, script_postdetection):
    """Detection des changements et de leur implication
        sur bib_noms, les attributs et les médias

    :return: Nombre de conflit detecté
    :rtype: int
    """
    # Analyse des changements
    # for sqlfile in [
    #     "1.1_taxref_changes_detections.sql",
    #     "2.1_taxref_changes_corrections_pre_detections.sql",
    #     "1.2_taxref_changes_detections_cas_actions.sql",
    #     "2.2_taxref_changes_corrections_post_detections.sql",
    # ]:

    query = text(
        importlib.resources.read_text(
            "apptax.migrations.data.migrate_taxref_version", "1.1_taxref_changes_detections.sql"
        )
    )
    db.session.execute(query)

    if script_predetection:
        logger.info(f"Run script {script_predetection}")
        query = text(Path(script_predetection).read_text())
        try:
            db.session.execute(query)
        except ProgrammingError as e:
            logger.error(f"Error un sql script {script_predetection} - {str(e)}")
            return
    query = text(
        importlib.resources.read_text(
            "apptax.migrations.data.migrate_taxref_version",
            "1.2_taxref_changes_detections_cas_actions.sql",
        )
    )
    db.session.execute(query)

    if script_postdetection:
        logger.info(f"Run script {script_postdetection}")
        query = text(Path(script_postdetection).read_text())
        try:
            db.session.execute(query)
        except ProgrammingError as e:
            logger.error(f"Error un sql script {script_postdetection} - {str(e)}")
            return

    db.session.commit()

    # Export des changements
    results = db.session.execute(text(EXPORT_QUERIES_MODIFICATION_NB))
    export_as_csv(file_name="nb_changements.csv", columns=results.keys(), data=results.fetchall())
    results = db.session.execute(text(EXPORT_QUERIES_MODIFICATION_LIST))
    export_as_csv(
        file_name="liste_changements.csv", columns=results.keys(), data=results.fetchall()
    )

    logger.info(f"List of taxref changes done in tmp")

    results = db.session.execute(text(EXPORT_QUERIES_CONFLICTS))
    nb_of_conflict = results.fetchone()["count"]
    return nb_of_conflict


def save_data(version, keep_taxref, keep_bdc):
    """Sauvegarde des données de l'ancienne version de taxref

    :param version: numéro de version de taxref
    :type version: int
    :param keep_taxref: Indique si l'on souhaite concerver l'ancienne version du referentiel taxref
    :type keep_taxref: boolean
    :param keep_bdc:  Indique si l'on souhaite concerver l'ancienne version du referentiel bdc_status
    :type keep_bdc: boolean
    """

    if keep_taxref:
        db.session.execute(
            text(
                f"""
            DROP TABLE IF EXISTS taxonomie.taxref_v{str(version)};
            CREATE TABLE taxonomie.taxref_v{str(version)} AS
            SELECT * FROM taxonomie.taxref;
        """
            )
        )

    if keep_bdc:
        db.session.execute(
            text(
                f"""
            DROP TABLE IF EXISTS taxonomie.bdc_statut_v{str(version)};
            CREATE TABLE taxonomie.bdc_statut_v{str(version)} AS
            SELECT * FROM taxonomie.bdc_statut;
        """
            )
        )
        db.session.execute(
            text(
                f"""
            DROP TABLE IF EXISTS taxonomie.bdc_statut_type_v{str(version)};
            CREATE TABLE taxonomie.bdc_statut_type_v{str(version)} AS
            SELECT * FROM taxonomie.bdc_statut_type;
        """
            )
        )


def missing_cd_nom_query(query_name, export_file_name):
    results = db.session.execute(text(query_name))
    data = results.fetchall()
    if len(data) > 0:
        logger.warning(
            f"Some cd_nom referencing in gn_synthese.synthese where missing from taxref v15 -> see file {export_file_name}"
        )
        export_as_csv(file_name=export_file_name, columns=results.keys(), data=data)
    # Test cd_nom without cd_nom_remplacement
    return test_cd_nom_without_sustitute(data)


def test_cd_nom_without_sustitute(data, key="cd_nom_remplacement"):
    for d in data:
        # Si la requete ne comporte pas le champ cd_nom_remplacement
        if not "cd_nom_remplacement" in d:
            return False
        if not d["cd_nom_remplacement"]:
            return True
    return False


def test_missing_cd_nom():
    # test cd_nom disparus
    missing_cd_nom_bib_noms = missing_cd_nom_query(
        query_name=EXPORT_QUERIES_MISSING_CD_NOMS_IN_BIB_NOMS,
        export_file_name="missing_cd_nom_into_bib_nom.csv",
    )

    # TODO => Delete redondonance avec EXPORT_QUERIES_MISSING_CD_NOMS_IN_DB
    missing_cd_nom_gn2 = missing_cd_nom_query(
        query_name=EXPORT_QUERIES_MISSING_CD_NOM_GN2_SYNTHESE,
        export_file_name="missing_cd_nom_into_gn_synthese.csv",
    )
    missing_cd_nom_gn2 = missing_cd_nom_query(
        query_name=EXPORT_QUERIES_MISSING_CD_NOMS_IN_DB,
        export_file_name="missing_cd_nom_into_geonature.csv",
    )
    return missing_cd_nom_bib_noms + missing_cd_nom_gn2


def copy_from_csv(
    f,
    engine,
    table_name,
    schema_name="taxonomie",
    header=True,
    encoding=None,
    delimiter=None,
    dest_cols="",
):
    try:

        options = ["FORMAT CSV"]
        if header:
            options.append("HEADER")
        if encoding:
            options.append(f"ENCODING '{encoding}'")
        if delimiter:
            options.append(f"DELIMITER E'{delimiter}'")
        options = ", ".join(options)

        conn = engine.raw_connection()
        cursor = conn.cursor()
        cursor.copy_expert(
            f"""
            COPY {schema_name}.{table_name}{dest_cols}
            FROM STDIN WITH ({options})
        """,
            f,
        )

        conn.commit()
        cursor.close()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def export_as_csv(file_name, columns, data, separator=","):
    with open(f"tmp/{file_name}", "w") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(data)

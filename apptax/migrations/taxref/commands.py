
import pdb
from turtle import pd
from flask import (
    Blueprint
)

import csv
import importlib
from zipfile import ZipFile
from sqlalchemy import text
import logging
from utils_flask_sqla.migrations.utils import  open_remote_file

logger = logging.getLogger('taxref_migration')
logger.setLevel(logging.INFO)

# create console handler and set level to debug
ch = logging.StreamHandler()
# # create formatter
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
# add ch to logger
logger.addHandler(ch)

from apptax.database import db
routes = Blueprint("taxref_migration", __name__, cli_group='taxref_migration')



EXPORT_QUERIES_MISSING_CD_NOM_GN2_SYNTHESE = """
    SELECT DISTINCT s.cd_nom, string_agg(DISTINCT s.nom_cite, ',') as nom_cite, string_agg(DISTINCT ts.name_source::varchar, ',')  as sources, count(*) as nb, d.plus_recente_diffusion, d.cd_nom_remplacement, d.cd_raison_suppression
    FROM gn_synthese.synthese  s
    JOIN  gn_synthese.t_sources  ts
    ON ts.id_source = s.id_source
    LEFT OUTER JOIN taxonomie.cdnom_disparu d
    ON d.cd_nom = s.cd_nom
    LEFT OUTER JOIN taxonomie.import_taxref t
    ON s.cd_nom = t.cd_nom
    WHERE t.cd_nom IS NULL AND NOT s.cd_nom IS NULL
    GROUP BY s.cd_nom, d.plus_recente_diffusion, d.cd_nom_remplacement, d.cd_raison_suppression;
"""

EXPORT_QUERIES_MISSING_CD_NOMS_IN_BIB_NOMS = """
    SELECT s.cd_nom, t.nom_complet, d.plus_recente_diffusion, d.cd_nom_remplacement, d.cd_raison_suppression
    FROM taxonomie.cdnom_disparu d
    JOIN taxonomie.bib_noms s
    ON s.cd_nom = d.cd_nom
    JOIN taxonomie.taxref t
    ON s.cd_nom = t.cd_nom
    ORDER BY plus_recente_diffusion
"""

EXPORT_QUERIES_MISSING_CD_NOMS_IN_DB = """
    SELECT public.deps_test_fk_dependencies_cd_nom();

    SELECT fk.table_name, t.cd_nom, t.nom_complet, count(*) AS nb_occurence ,  d.plus_recente_diffusion, d.cd_nom_remplacement, d.cd_raison_suppression
    FROM tmp_taxref_changes.dps_fk_cd_nom fk
    JOIN taxonomie.taxref t
    ON t.cd_nom = fk.cd_nom
    JOIN taxonomie.cdnom_disparu d
    ON d.cd_nom = fk.cd_nom
    WHERE NOT fk.table_name='taxonomie.bdc_statut_taxons'
    GROUP BY fk.table_name, t.cd_nom, t.nom_complet,  d.plus_recente_diffusion, d.cd_nom_remplacement, d.cd_raison_suppression;
"""

# -- Décompte des changements de grappe de cd_nom qui vont être réalisé et les potentiels conflits qu'ils faur résoudre en amont
EXPORT_QUERIES_MODIFICATION_NB = """
    SELECT DISTINCT COALESCE(cas, 'no changes') AS cas, count(*)
    FROM tmp_taxref_changes.comp_grap c
    GROUP BY  cas
    ORDER BY count
"""
# -- Liste des changements  de grappe de cd_nom  avec potentiels conflicts et perte de données attributaires
EXPORT_QUERIES_MODIFICATION_LIST = """
    SELECT
        t.regne , t.group1_inpn , t.group2_inpn ,
        c.i_cd_ref, c.i_array_agg AS i_cd_nom_list, t.nom_valide AS i_nom_valid, i_count AS i_nb_cd_nom,
        f_cd_ref, f_array_agg AS f_cd_nom_list, it.nom_valide AS f_nom_valid, f_count AS f_nb_cd_nom,
        att_list, att_nb, media_nb, grappe_change, "action", cas
    FROM tmp_taxref_changes.comp_grap c
    JOIN taxonomie.taxref t
    ON t.cd_nom = c.i_cd_ref
    JOIN taxonomie.import_taxref it
    ON it.cd_nom = c.f_cd_ref
    WHERE NOT action ='no changes';
"""

EXPORT_QUERIES_CONFLICTS="""
    SELECT count(*) FROM tmp_taxref_changes.comp_grap WHERE action ilike '%Conflict%';
"""

base_url = 'http://geonature.fr/data/inpn/taxonomie/'

@routes.cli.command()
def update_taxref_v15():
    """
        Procédure de migration de taxref
            Taxref v14 vers v15
            Test de la disparition des cd_noms
    """
    # import taxref v15 data
    import_taxref()

    # test if deleted cd_nom can be correct without manual intervention
    if test_missing_cd_nom():
        logger.error("Some cd_nom will disappear without substitute. You can't continue")
        # TODO ??? Force exit or not ???
        exit()

    process_bib_noms()
    # Change dection and repport
    detect_changes()

@routes.cli.command()
def update_taxref_v15():
    """
        Procédure de migration de taxref
            Taxref v14 vers v15
            Test de la disparition des cd_noms
    """
    # import taxref v15 data
    import_taxref()

    # test if deleted cd_nom can be correct without manual intervention
    if test_missing_cd_nom():
        logger.error("Some cd_nom will disappear without substitute. You can't continue")
        # TODO ??? Force exit or not ???
        exit()

    process_bib_noms()

    # Change detection and repport
    detect_changes()


@routes.cli.command()
def apply_changes():
    """
        Procédure de migration de taxref
            Taxref v14 vers v15
            Application des changements
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

    # Update taxref v15
    logger.info("Migration of taxref ...")
    try:
        db.session.execute(text("DROP TABLE IF EXISTS taxonomie.taxref_v14; CREATE TABLE taxonomie.taxref_v14 AS SELECT * FROM taxonomie.taxref;"))
        query = text(importlib.resources.read_text('apptax.migrations.data.taxref_v15', '3.2_alter_taxref_data.sql'))
        db.session.execute(query)
        db.session.commit()
        logger.info("it's done")
    except Exception as e:
        logger.error(str(e))

    # Update bdc_status#
    db.session.execute(text("""
        DROP TABLE IF EXISTS taxonomie.bdc_statut_v14;
        CREATE TABLE taxonomie.bdc_statut_v14 AS
        SELECT * FROM taxonomie.bdc_statut;
    """))
    db.session.execute(text("""
        DROP TABLE IF EXISTS taxonomie.bdc_statut_type_v14;
        CREATE TABLE taxonomie.bdc_statut_type_v14 AS
        SELECT * FROM taxonomie.bdc_statut_type;
    """))


    db.session.execute(text("""
        TRUNCATE TABLE  taxonomie.bdc_statut_type CASCADE;
        TRUNCATE TABLE  taxonomie.bdc_statut;
    """))
    db.session.commit()

    with open_remote_file(base_url, 'BDC-statuts-15.zip', open_fct=ZipFile, data_dir="/home/sahl/dev/TaxHub/tmp") as archive:
        with archive.open('BDC_STATUTS_TYPES_15.csv') as f:
            logger.info("Insert BDC_STATUTS_TYPES_15 table…")
            copy_from_csv(f, db.engine,
                table_name="bdc_statut_type", schema_name="taxonomie",
                header=True, encoding=None, delimiter=",", dest_cols=''
            )
        with archive.open('BDC_STATUTS_15.csv') as f:
            logger.info("Insert bdc_statut table…")
            copy_from_csv(f, db.engine,
                table_name="bdc_statut", schema_name="taxonomie",
                header=True, encoding="WIN1252", delimiter=",",
                dest_cols='(cd_nom, cd_ref, cd_sup, cd_type_statut, lb_type_statut, regroupement_type, code_statut, label_statut, rq_statut, cd_sig, cd_doc, lb_nom, lb_auteur, nom_complet_html, nom_valide_html, regne, phylum, classe, ordre, famille, group1_inpn, group2_inpn, lb_adm_tr, niveau_admin, cd_iso3166_1, cd_iso3166_2, full_citation, doc_url, thematique, type_value)'
            )

    # Delete doublons
    logger.info("Remove duplicate bdc_statut")
    db.session.execute(text("""
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

    """))

    # Structure BDC_Statut
    logger.info("Import raw bdc_statut into structured table")
    query = text(importlib.resources.read_text('apptax.migrations.data', 'taxonomie_bdc_statuts.sql'))
    db.session.execute(query)

    # Structure BDC_Statut
    logger.info("Clean DB")
    query = text(importlib.resources.read_text('apptax.migrations.data.taxrefv15', '5_clean_db.sql'))
    db.session.execute(query)

    db.session.commit()

def import_taxref():

    logger.info("Import TAXREFv15 into tmp table…")

    # Préparation création de table temporaire permettant d'importer taxref
    for sqlfile in ['0_taxrefv15_import_data.sql',]:
        query = text(importlib.resources.read_text('apptax.migrations.data.taxref_v15', sqlfile))
        db.session.execute(query)
    db.session.commit()


    with open_remote_file(base_url, 'TAXREF_v15_2021.zip', open_fct=ZipFile, data_dir="/home/sahl/dev/TaxHub/tmp") as archive:
        with archive.open('TAXREFv15.txt') as f:
            logger.info("Insert TAXREFv15 tmp table…")
            copy_from_csv(f, db.engine,
                table_name="import_taxref", schema_name="taxonomie",
                header=True, encoding=None, delimiter="\t", dest_cols=''
            )
        with archive.open('CDNOM_DISPARUS.csv') as f:
            logger.info("Insert cdnom_disparu tmp table…")
            copy_from_csv(f, db.engine,
                table_name="cdnom_disparu", schema_name="taxonomie",
                header=True, encoding=None, delimiter=",", dest_cols=''
            )

        # No changes in taxref v15
        # with archive.open('rangs_note.csv') as f:
        #     logger.info("Insert rangs_note tmp table…")
        #     copy_from_csv(f, db.engine,
        #         table_name="import_taxref_rangs", schema_name="taxonomie",
        #         header=True, encoding="WIN1252", delimiter=";", dest_cols=''
        #     )

def process_bib_noms():
    """
        Création d'une table copie de bib_noms
    """
    logger.info("Create working copy of bib_noms…")

    # Préparation création de table temporaire permettant d'importer taxref
    for sqlfile in ['0.1_generate_tmp_bib_noms_copy.sql',]:
        query = text(importlib.resources.read_text('apptax.migrations.data.taxref_v15', sqlfile))
        db.session.execute(query)
    db.session.commit()

def detect_changes():
    # Analyse des changements
    for sqlfile in [
        '1.1_taxref_changes_detections.sql',
        '2.1_taxref_changes_corrections_pre_detections.sql',
        '1.2_taxref_changes_detections_cas_actions.sql',
        '2.2_taxref_changes_corrections_post_detections.sql'
    ]:
        try:
            query = text(importlib.resources.read_text('apptax.migrations.data.taxref_v15', sqlfile))
            db.session.execute(query)
        except FileNotFoundError:
            logger.warning(f"File not found {sqlfile}")
    db.session.commit()

    # Export des changements
    results = db.session.execute(text(EXPORT_QUERIES_MODIFICATION_NB))
    export_as_csv(
        file_name="nb_changements.csv",
        columns=results.keys(),
        data=results.fetchall()
    )
    results = db.session.execute(text(EXPORT_QUERIES_MODIFICATION_LIST))
    export_as_csv(
        file_name="liste_changements.csv",
        columns=results.keys(),
        data=results.fetchall()
    )

    logger.info(f"List of taxref changes done in tmp")

    results = db.session.execute(text(EXPORT_QUERIES_CONFLICTS))
    nb_of_conflict = results.fetchone()["count"]
    return nb_of_conflict


def missing_cd_nom_query(query_name, export_file_name):
    results = db.session.execute(text(query_name))
    data = results.fetchall()
    if len(data)>0:
        logger.warning(f"Some cd_nom referencing in gn_synthese.synthese where missing from taxref v15 -> see file {export_file_name}")
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
        query_name = EXPORT_QUERIES_MISSING_CD_NOMS_IN_BIB_NOMS,
         export_file_name="missing_cd_nom_into_bib_nom.csv"
    )

    # TODO => Delete redondonance avec EXPORT_QUERIES_MISSING_CD_NOMS_IN_DB
    missing_cd_nom_gn2 = missing_cd_nom_query(
        query_name = EXPORT_QUERIES_MISSING_CD_NOM_GN2_SYNTHESE,
        export_file_name="missing_cd_nom_into_gn_synthese.csv"
    )
    missing_cd_nom_gn2 = missing_cd_nom_query(
        query_name = EXPORT_QUERIES_MISSING_CD_NOMS_IN_DB,
        export_file_name="missing_cd_nom_into_geonature.csv"
    )
    return missing_cd_nom_bib_noms + missing_cd_nom_gn2


def copy_from_csv(f, engine,
    table_name, schema_name="taxonomie",
    header=True, encoding=None, delimiter=None, dest_cols=''
):
    try:

        options = ["FORMAT CSV"]
        if header: options.append("HEADER")
        if encoding: options.append(f"ENCODING '{encoding}'")
        if delimiter: options.append(f"DELIMITER E'{delimiter}'")
        options = ', '.join(options)

        conn = engine.raw_connection()
        cursor = conn.cursor()
        cursor.copy_expert(f"""
            COPY {schema_name}.{table_name}{dest_cols}
            FROM STDIN WITH ({options})
        """, f)

        conn.commit()
        cursor.close()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def export_as_csv(file_name, columns, data, separator=','):
    with open(f"tmp/{file_name}", "w") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(data)

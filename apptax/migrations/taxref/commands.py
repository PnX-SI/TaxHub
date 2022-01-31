
import pdb
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
    WHERE t.cd_nom IS NULL
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
    SELECT DISTINCT cas, count(*)
	FROM tmp_taxref_changes.comp_grap c
	GROUP BY  cas
	ORDER BY cas
"""
# -- Liste des changements  de grappe de cd_nom  avec potentiels conflicts et perte de données attributaires
EXPORT_QUERIES_MODIFICATION_LIST = """
    SELECT *
FROM tmp_taxref_changes.comp_grap
WHERE NOT action ='no changes'
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

    # test cd_nom disparus
    missing_cd_nom_bib_noms = missing_cd_nom_query(
        query_name = EXPORT_QUERIES_MISSING_CD_NOMS_IN_BIB_NOMS,
         export_file_name="missing_cd_nom_into_gn_synthese.csv"
    )

    missing_cd_nom_gn2 = missing_cd_nom_query(
        query_name = EXPORT_QUERIES_MISSING_CD_NOM_GN2_SYNTHESE,
        export_file_name="missing_cd_nom_into_bib_nom.csv"
    )
    missing_cd_nom_query(
        query_name = EXPORT_QUERIES_MISSING_CD_NOMS_IN_DB,
        export_file_name="missing_cd_nom_into_geonature.csv"
    )


    if missing_cd_nom_bib_noms or missing_cd_nom_gn2 :
        logger.error("Some cd_nom will disappear without substitute. You can't continue")
        # TODO ??? Force exit or not ???
        # exit()

    process_bib_noms()
    detect_changes()

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
        with archive.open('rangs_note.csv') as f:
            logger.info("Insert cdnom_disparu tmp table…")
            copy_from_csv(f, db.engine,
                table_name="import_taxref_rangs", schema_name="taxonomie",
                header=True, encoding="WIN1252", delimiter=";", dest_cols=''
            )

def process_bib_noms():

    logger.info("Create working copy of bib_noms…")

    # Préparation création de table temporaire permettant d'importer taxref
    for sqlfile in ['0.1_generate_tmp_bib_noms_copy.sql',]:
        query = text(importlib.resources.read_text('apptax.migrations.data.taxref_v15', sqlfile))
        db.session.execute(query)
    db.session.commit()

def detect_changes():
    # Analsye des changements
    for sqlfile in ['1.1_taxref_changes_detections.sql', '1.2_taxref_changes_detections_cas_actions.sql']:
        query = text(importlib.resources.read_text('apptax.migrations.data.taxref_v15', sqlfile))
        db.session.execute(query)
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

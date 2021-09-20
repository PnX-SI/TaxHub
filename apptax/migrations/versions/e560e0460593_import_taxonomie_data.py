"""taxonomie inpn data

Revision ID: e560e0460593
Revises: None
Create Date: 2021-09-20 10:33:29.047633

"""
import importlib.resources
from alembic import op
import sqlalchemy as sa

from utils_flask_sqla.migrations.utils import (
    logger,
    open_remote_file
)

# revision identifiers, used by Alembic.
revision = 'e560e0460593'
down_revision = None
branch_labels = ('taxonomie-data',)
depends_on = '9c2c0254aadc'


base_url = 'https://geonature.fr/data/inpn/taxonomie/'
TAXREF_URL = f"{base_url}TAXREF_v14_2020/"
ST_PR_URL = f"{base_url}BDC-Statuts-v14/"

TAXREF_FILES = {
    "import_taxref":  {
        "file_name": "TAXREFv14.txt.xz",
        "delimiter": "\t"
    },
    "bib_taxref_rangs": {
        "file_name": "rangs_note.csv",
        "cols": "tri_rang, id_rang, nom_rang, nom_rang_en",
        "delimiter": "\t"
    },
    "bib_taxref_statuts": {
        "file_name": "statuts_note.csv",
        "cols": "ordre, id_statut, nom_statut, definition",
        "delimiter": "\t"
    },
    "bib_taxref_habitats": {
        "file_name": "habitats_note.csv",
        "delimiter": "\t"
    }
}

ST_PROT_FILES = {
    "bdc_statut_type": {
        "file_name": "BDC_STATUTS_TYPES_14.csv"
    },
    "bdc_statut": {
        "file_name": "BDC_STATUTS_14_UTF8.csv.xz"
    }
}


def upgrade():
    cursor = op.get_bind().connection.cursor()
    #  Import des fichiers de taxref
    for temp_table_name in TAXREF_FILES:
        import_taxref_file(
            temp_table_name,
            TAXREF_FILES[temp_table_name],
            TAXREF_URL,
            cursor
        )

    #  Import des fichiers de statuts de protection
    for temp_table_name in ST_PROT_FILES:
        import_taxref_file(
            temp_table_name,
            ST_PROT_FILES[temp_table_name],
            ST_PR_URL,
            cursor
        )
    logger.info(f"Insertion  des données taxonomiques de l'inpn... (cette opération peut être longue)")
    op.execute(importlib.resources.read_text('apptax.migrations.data', 'taxhubdata_inpn.sql'))
    logger.info(f"Create materialized views")
    op.execute(importlib.resources.read_text('apptax.migrations.data', 'materialized_views.sql'))


def downgrade():
    logger.info(f"DROP MATERIALIZED VIEW")
    op.execute("""
        DROP TABLE IF EXISTS taxonomie.vm_taxref_hierarchie;
        DROP VIEW taxonomie.v_taxref_hierarchie_bibtaxons;
        DROP MATERIALIZED VIEW taxonomie.vm_regne;
        DROP MATERIALIZED VIEW taxonomie.vm_phylum;
        DROP MATERIALIZED VIEW taxonomie.vm_classe;
        DROP MATERIALIZED VIEW taxonomie.vm_ordre;
        DROP MATERIALIZED VIEW taxonomie.vm_famille;
        DROP MATERIALIZED VIEW taxonomie.vm_group1_inpn;
        DROP MATERIALIZED VIEW taxonomie.vm_group2_inpn;

        DROP INDEX IF EXISTS taxonomie.i_unique_ordre;
        DROP INDEX IF EXISTS taxonomie.i_unique_phylum;
        DROP INDEX IF EXISTS taxonomie.i_unique_regne;
        DROP INDEX IF EXISTS taxonomie.i_unique_famille;
        DROP INDEX IF EXISTS taxonomie.i_unique_classe;
        DROP INDEX IF EXISTS taxonomie.i_unique_group1_inpn;
        DROP INDEX IF EXISTS taxonomie.i_unique_group2_inpn;
    """)

    logger.info(f"TRUNCATE TABLE taxonomie.taxref")
    op.execute("""
        TRUNCATE TABLE taxonomie.taxref CASCADE;
        ALTER TABLE taxonomie.bdc_statut DROP id;
    """)

    for temp_table_name in {**TAXREF_FILES, **ST_PROT_FILES}:
        logger.info(f"Truncate table {temp_table_name}")
        op.execute(f"TRUNCATE TABLE taxonomie.{temp_table_name} CASCADE;")


def import_taxref_file(temp_table_name, data_def, url, cursor):
    """
        Fonction qui permet d'inséré une table dans
        la base de donnée

        temp_table_name : nom de la table d'import
        data_def : dictionnaire de définition de l'import
        url : lien de téléchargement du fichier
        cursor : curseur de BD
    """
    filename = data_def["file_name"]

    # Si la liste des colonnes à insérer est spécifié
    I_COLS = ""
    if "cols" in data_def:
        I_COLS = f"({data_def['cols']})"

    DELIMITER = ""
    if "delimiter" in data_def:
        DELIMITER = f"DELIMITER '{data_def['delimiter']}'"

    with open_remote_file(url, filename) as csvfile:
        logger.info(f"Inserting taxref data in temporary table {temp_table_name}")
        cursor.copy_expert(
            f"""
            COPY taxonomie.{temp_table_name} {I_COLS}
            FROM STDIN {DELIMITER} CSV HEADER
            """,
            csvfile
        )

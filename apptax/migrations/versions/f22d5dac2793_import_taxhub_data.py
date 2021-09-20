"""Insertion des données nécessaires à taxhub

Revision ID: f22d5dac2793
Revises: e560e0460593
Create Date: 2021-09-20 14:27:45.704383

"""

import importlib.resources
from alembic import op
import sqlalchemy as sa
from utils_flask_sqla.migrations.utils import (
    logger
)



# revision identifiers, used by Alembic.
revision = 'f22d5dac2793'
down_revision = 'e560e0460593'
branch_labels = None
depends_on = None


def upgrade():
    logger.info("Insertion de données de base")
    op.execute(importlib.resources.read_text('apptax.migrations.data', 'taxhubdata.sql'))


def downgrade():
    logger.info("Suppression donnees taxhub")
    op.execute("""
        DELETE FROM taxonomie.bib_themes WHERE id_theme = 1;
        DELETE FROM taxonomie.bib_listes WHERE id_liste = 1;

        DELETE FROM  taxonomie.bib_types_media
            WHERE id_type IN (1,2,3,4,5,6,7,8,9);
    """)

    logger.info("Suppression vm_taxref_list_forautocomplete")
    op.execute("""
        DROP INDEX taxonomie.i_vm_taxref_list_forautocomplete_gid;
        DROP INDEX taxonomie.i_vm_taxref_list_forautocomplete_cd_nom;
        DROP INDEX taxonomie.i_vm_taxref_list_forautocomplete_search_name;
        DROP INDEX taxonomie.i_tri_vm_taxref_list_forautocomplete_search_name;
        DROP MATERIALIZED VIEW IF EXISTS taxonomie.vm_taxref_list_forautocomplete;
    """)

    logger.info("Suppression donnees taxonomique")
    op.execute("""
        DELETE FROM taxonomie.bdc_statut_cor_text_values;
        DELETE FROM taxonomie.bdc_statut_taxons;
        DELETE FROM taxonomie.bdc_statut_text;
        DELETE FROM taxonomie.bdc_statut_values;
    """)

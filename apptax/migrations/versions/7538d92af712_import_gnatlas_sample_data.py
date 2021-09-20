"""Insertion de données pour Géonature Atlas

Revision ID: 7538d92af712
Revises: e560e0460593
Create Date: 2021-09-20 16:49:44.449414

"""
import importlib.resources
from alembic import op
import sqlalchemy as sa
from utils_flask_sqla.migrations.utils import (
    logger
)


# revision identifiers, used by Alembic.
revision = '7538d92af712'
down_revision = None
branch_labels = ('gn_atlas-samples',)
depends_on = 'f22d5dac2793'



def upgrade():
    op.execute(importlib.resources.read_text('apptax.migrations.data', 'taxhubdata_atlas.sql'))


def downgrade():
    op.execute("""
        DELETE FROM taxonomie.bib_attributs
        WHERE id_theme = (SELECT id_theme FROM taxonomie.bib_themes WHERE nom_theme='Atlas');

        DELETE FROM taxonomie.bib_themes WHERE nom_theme='Atlas';
    """)

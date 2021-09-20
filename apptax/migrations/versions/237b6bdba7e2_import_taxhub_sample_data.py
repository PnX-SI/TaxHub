"""Ajout de données d'exemple de taxhub

Revision ID: 237b6bdba7e2
Revises: e560e0460593
Create Date: 2021-09-20 16:47:04.883244

"""
import importlib.resources
from alembic import op
import sqlalchemy as sa
from utils_flask_sqla.migrations.utils import (
    logger
)



# revision identifiers, used by Alembic.
revision = '237b6bdba7e2'
down_revision = None
branch_labels = ('taxhub-samples',)
depends_on = 'f22d5dac2793'


def upgrade():
    op.execute(importlib.resources.read_text('apptax.migrations.data', 'taxhubdata_taxons_example.sql'))


def downgrade():
    op.execute("""
        DELETE FROM taxonomie.cor_nom_liste WHERE id_liste = 100;
        DELETE FROM taxonomie.bib_noms
            WHERE cd_nom IN (67111, 60612, 351, 8326, 11165, 81065, 95186, 713776);
        DELETE FROM taxonomie.bib_attributs WHERE nom_attribut = 'migrateur';
    """)

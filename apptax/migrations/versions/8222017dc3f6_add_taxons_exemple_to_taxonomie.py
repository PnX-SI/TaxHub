"""add taxons exemple to taxonomie

Revision ID: 8222017dc3f6
Create Date: 2021-09-22 16:35:03.480932

"""
import importlib.resources

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8222017dc3f6'
down_revision = None
branch_labels = ('taxonomie_taxons_example',)
depends_on = (
    '9c2c0254aadc',  # taxonomie
    'f61f95136ec3',  # taxonomie INPN data
)


def upgrade():
    op.execute(importlib.resources.read_text('apptax.migrations.data', 'taxonomie_taxons_example.sql'))


def downgrade():
    op.execute("""
    DELETE FROM taxonomie.cor_nom_liste nl
    USING taxonomie.bib_noms n
    WHERE n.cd_nom in (67111,60612,351,8326,11165,18437,81065,95186,713776)
    AND n.id_nom = nl.id_nom
    AND nl.id_liste = 100
    """)
    op.execute("""
    DELETE FROM taxonomie.bib_noms
    WHERE cd_nom in (67111,60612,351,8326,11165,18437,81065,95186,713776)
    """)

"""add attributes exemple to taxonomie

Revision ID: aa7533601e41
Create Date: 2021-09-22 16:30:31.642357

"""
import importlib.resources

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aa7533601e41'
down_revision = None
branch_labels = ('taxonomie_attributes_example',)
depends_on = (
    '9c2c0254aadc',  # taxonomie
)


def upgrade():
    op.execute(importlib.resources.read_text('apptax.migrations.data', 'taxonomie_attributes_example.sql'))


def downgrade():
    op.execute("""
    DELETE FROM taxonomie.bib_attributs WHERE nom_attribut = 'migrateur'
    """)

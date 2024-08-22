"""set field liste_valeur_attribut nullable

Revision ID: b250cfcaab64
Revises: 0db13d65cb27
Create Date: 2024-08-22 14:23:29.831794

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b250cfcaab64"
down_revision = "0db13d65cb27"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        table_name="bib_attributs",
        column_name="liste_valeur_attribut",
        nullable=True,
        schema="taxonomie",
    )


def downgrade():
    op.alter_column(
        table_name="bib_attributs",
        column_name="liste_valeur_attribut",
        nullable=False,
        schema="taxonomie",
    )

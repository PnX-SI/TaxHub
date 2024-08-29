"""Drop bib_themes.id_droit column

Revision ID: 6a20cd1055ec
Revises: 44447746cacc
Create Date: 2024-08-28 15:38:36.829167

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6a20cd1055ec"
down_revision = "44447746cacc"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column(table_name="bib_themes", column_name="id_droit", schema="taxonomie")


def downgrade():
    op.add_column(
        table_name="bib_themes",
        column=sa.Column("id_droit", sa.Integer(), nullable=False, server_default="0"),
        schema="taxonomie",
    )

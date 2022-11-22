"""remove picto

Revision ID: 5cef20a05a20
Revises: 1cf2cdc94f9b
Create Date: 2023-07-31 16:15:29.608981

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5cef20a05a20"
down_revision = "1cf2cdc94f9b"
branch_labels = None
depends_on = None
from sqlalchemy import Column, String


def upgrade():
    op.drop_column(table_name="bib_listes", column_name="picto", schema="taxonomie")


def downgrade():
    op.add_column(
        table_name="bib_listes", column=sa.Column("picto", String(250)), schema="taxonomie"
    )

"""[taxref] Taxref v18

Revision ID: da3172cecdb1
Revises: 2c68a907f74c
Create Date: 2025-01-14 11:44:12.356028

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "da3172cecdb1"
down_revision = "2c68a907f74c"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(table_name="taxref", column=sa.Column("cd_ba", sa.Integer()), schema="taxonomie")
    op.add_column(
        table_name="taxref",
        column=sa.Column("nomenclatural_comment", sa.String(500)),
        schema="taxonomie",
    )


def downgrade():
    op.drop_column(table_name="taxref", column_name="cd_ba", schema="taxonomie")
    op.drop_column(table_name="taxref", column_name="nomenclatural_comment", schema="taxonomie")

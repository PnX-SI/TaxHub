"""remove t admin log

Revision ID: a982df406ae8
Revises: 5cef20a05a20
Create Date: 2023-08-01 12:13:20.005850

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "a982df406ae8"
down_revision = "5cef20a05a20"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table(table_name="taxhub_admin_log", schema="taxonomie")


def downgrade():
    op.create_table(
        "taxhub_admin_log",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("action_time", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("id_role", sa.Integer()),
        sa.Column("object_type", sa.VARCHAR(50), nullable=False),
        sa.Column("object_id", sa.Integer()),
        sa.Column("object_repr", sa.VARCHAR(200)),
        sa.Column("change_type", sa.VARCHAR(250)),
        sa.Column("change_message", sa.VARCHAR(250)),
        schema="taxonomie",
    )

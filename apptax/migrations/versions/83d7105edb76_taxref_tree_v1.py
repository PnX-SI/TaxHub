"""create vm_taxref_tree v1

Revision ID: 83d7105edb76
Revises: 44447746cacc
Create Date: 2024-10-05 17:40:11.302423

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "83d7105edb76"
down_revision = "6a20cd1055ec"
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    op.execute("DROP MATERIALIZED VIEW IF EXISTS taxonomie.vm_taxref_tree")

"""add groupe3 inpn to bib_listes

Revision ID: fd5ed3f94d0f
Revises: 3bd542b72955
Create Date: 2023-07-03 17:30:51.995292

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "fd5ed3f94d0f"
down_revision = "3bd542b72955"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        ALTER TABLE taxonomie.bib_listes ADD group3_inpn varchar(255);
    """
    )


def downgrade():
    op.execute(
        """
        ALTER TABLE taxonomie.bib_listes DROP COLUMN group3_inpn;
    """
    )

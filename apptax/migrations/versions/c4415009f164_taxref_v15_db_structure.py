"""Taxref v15 db structure

Revision ID: c4415009f164
Revises: d768a5da908c
Create Date: 2022-02-04 17:28:55.485135

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c4415009f164"
down_revision = "4a549132d156"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        ALTER TABLE taxonomie.taxref ADD group3_inpn varchar(250);
    """
    )


def downgrade():
    op.execute(
        """
        ALTER TABLE taxonomie.taxref DROP COLUMN group3_inpn;
    """
    )

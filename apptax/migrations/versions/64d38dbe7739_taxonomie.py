"""taxonomie

Revision ID: 64d38dbe7739
Revises: fa5a90853c45
Create Date: 2022-08-04 13:32:37.891099

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "64d38dbe7739"
down_revision = "fa5a90853c45"
branch_labels = None
depends_on = ("1b1a3f5cd107",)  # taxonomie


def upgrade():
    pass


def downgrade():
    pass

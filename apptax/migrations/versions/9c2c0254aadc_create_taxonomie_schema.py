"""taxonomie schema 1.8.1

Revision ID: 9c2c0254aadc
Revises: fa35dfe5ff27
Create Date: 2021-08-24 16:02:01.413557

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9c2c0254aadc'
down_revision = None
branch_labels = ('taxonomie',)
depends_on = None


def upgrade():
    raise Exception("""
    You should manually migrate your database to 1.8.1 version of taxonomie schema, then stamp your database version to this revision :
        flask db stamp 9c2c0254aadc
    """)


def downgrade():
    raise Exception("""
    This revision do not support downgrade (yet).
    """)

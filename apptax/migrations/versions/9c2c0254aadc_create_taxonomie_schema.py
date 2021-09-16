"""taxonomie schema 1.8.1

Revision ID: 9c2c0254aadc
Revises: fa35dfe5ff27
Create Date: 2021-08-24 16:02:01.413557

"""

import importlib.resources
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9c2c0254aadc'
down_revision = None
branch_labels = ('taxonomie',)
depends_on = (
    'fa35dfe5ff27',  # utilisateurs schema 1.4.7
)

def upgrade():
    op.execute(importlib.resources.read_text('apptax.migrations.data', 'taxhubdb.sql'))

def downgrade():
    op.execute("""
    DROP SCHEMA taxonomie CASCADE;
    """)

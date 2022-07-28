"""create taxonomie schema version 1.8.1

Revision ID: 9c2c0254aadc
Create Date: 2021-08-24 16:02:01.413557

"""
import importlib.resources

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9c2c0254aadc"
down_revision = None
branch_labels = ("taxonomie",)
depends_on = None


def upgrade():
    for sqlfile in [
        "taxonomie.sql",
        "taxonomie_data.sql",
        "taxonomie_materialized_views.sql",
    ]:
        op.execute(importlib.resources.read_text("apptax.migrations.data", sqlfile))


def downgrade():
    op.execute("DROP SCHEMA taxonomie CASCADE")

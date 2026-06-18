"""get_taxref_version_pg_fct

Revision ID: 913634ce1da4
Revises: eb7fe5a32655
Create Date: 2026-06-18 09:34:43.648527

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "913634ce1da4"
down_revision = "eb7fe5a32655"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        CREATE OR REPLACE FUNCTION taxonomie.get_current_taxref_version()
            RETURNS integer
            LANGUAGE sql
            STABLE
            PARALLEL SAFE
        AS
        $tx_version$
        SELECT version
        FROM taxonomie.t_meta_taxref
        ORDER BY update_date DESC
        LIMIT 1
        $tx_version$;
        """)


def downgrade():
    op.execute("""
        DROP FUNCTION taxonomie.get_current_taxref_version();
        """)

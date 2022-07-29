"""add bdc_status indexes

Revision ID: d768a5da908c
Revises: 4fb7e197d241
Create Date: 2021-10-11 15:25:17.536833

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d768a5da908c"
down_revision = "4fb7e197d241"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "CREATE INDEX idx_bst_id_value_text ON taxonomie.bdc_statut_taxons (id_value_text);"
    )
    op.execute("CREATE INDEX idx_bsctv_id_text ON taxonomie.bdc_statut_cor_text_values (id_text);")
    op.execute(
        "CREATE INDEX idx_bsctv_id_value ON taxonomie.bdc_statut_cor_text_values (id_value);"
    )
    op.execute("CREATE INDEX idx_bstxt_cd_sig ON taxonomie.bdc_statut_text (cd_sig);")
    op.execute(
        """
        CREATE INDEX idx_bstxt_cd_type_statut 
        ON taxonomie.bdc_statut_text (cd_type_statut);
    """
    )


def downgrade():
    op.execute(
        """
        DROP INDEX
            taxonomie.idx_bst_id_value_text,
            taxonomie.idx_bsctv_id_text,
            taxonomie.idx_bstxt_cd_type_statut,
            taxonomie.idx_bstxt_cd_sig ;
    """
    )

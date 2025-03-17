"""Add cor_taxon_attribut taxref foreign key

Revision ID: eb7fe5a32655
Revises: 347f8dceb318
Create Date: 2025-03-17 11:04:46.777376

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "eb7fe5a32655"
down_revision = "347f8dceb318"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        ALTER TABLE taxonomie.cor_taxon_attribut ADD
	        CONSTRAINT cor_taxon_attrib_taxref_fkey FOREIGN KEY (cd_ref) REFERENCES taxonomie.taxref(cd_nom);
    """
    )


def downgrade():
    op.execute(
        """
        ALTER TABLE taxonomie.cor_taxon_attribut DROP
            CONSTRAINT cor_taxon_attrib_taxref_fkey;
    """
    )

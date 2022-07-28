"""Add unique constraints

Revision ID: 4a549132d156
Revises: 4fb7e197d241
Create Date: 2022-01-28 15:21:46.042686

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4a549132d156"
down_revision = "d768a5da908c"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        ALTER TABLE taxonomie.bib_attributs ADD CONSTRAINT unique_bib_attributs_nom_attribut UNIQUE (nom_attribut);
        ALTER TABLE taxonomie.bib_themes  ADD CONSTRAINT unique_bib_themes_nom_theme UNIQUE (nom_theme);
        ALTER TABLE taxonomie.cor_nom_liste ADD CONSTRAINT unique_cor_nom_liste_id_liste_id_nom UNIQUE (id_liste, id_nom);
    """
    )


def downgrade():
    op.execute(
        """
        ALTER TABLE taxonomie.bib_attributs DROP CONSTRAINT unique_bib_attributs_nom_attribut;
        ALTER TABLE taxonomie.bib_themes  DROP CONSTRAINT unique_bib_themes_nom_theme;
        ALTER TABLE taxonomie.cor_nom_liste DROP CONSTRAINT unique_cor_nom_liste_id_liste_id_nom;
    """
    )

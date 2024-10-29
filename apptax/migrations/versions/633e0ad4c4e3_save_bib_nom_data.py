"""Save bib_noms data

Revision ID: 633e0ad4c4e3
Revises: a982df406ae8
Create Date: 2023-08-03 15:21:18.772715

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "633e0ad4c4e3"
down_revision = "b9e157ffd8be"
branch_labels = None
depends_on = None


def upgrade():
    # Création d'une liste avec les cd_noms contenus dans bib_noms
    #   uniquement si la table bib_noms est peuplée (cas d'un upgrade)
    op.execute(
        """
        -- Création liste
        INSERT INTO taxonomie.bib_listes (nom_liste, desc_liste,  code_liste)
        SELECT 
            'Save bib_noms',
            'Liste contenant l''ensemble des cd_noms contenus historiquement dans la table bib_noms',
            'BIB_NOMS'
        FROM taxonomie.bib_noms AS bn 
        LIMIT 1;

        -- Insertion des valeurs de bib_noms dans la liste
        INSERT INTO taxonomie.cor_nom_liste (cd_nom, id_liste)
        SELECT
            cd_nom,
            (SELECT id_liste FROM taxonomie.bib_listes WHERE code_liste ='BIB_NOMS' LIMIT 1) AS id_liste
        FROM taxonomie.bib_noms AS bn ;
    """
    )


def downgrade():
    op.execute(
        """
        DELETE FROM taxonomie.cor_nom_liste
        WHERE id_liste = (SELECT id_liste FROM taxonomie.bib_listes WHERE code_liste ='BIB_NOMS' LIMIT 1);
        DELETE FROM taxonomie.bib_listes WHERE code_liste ='BIB_NOMS';
    """
    )

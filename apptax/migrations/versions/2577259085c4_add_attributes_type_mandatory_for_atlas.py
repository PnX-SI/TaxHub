"""add attributes type mandatory for atlas

Revision ID: 2577259085c4
Revises:
Create Date: 2025-12-03 14:23:13.654929

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2577259085c4"
down_revision = None
branch_labels = ("taxhub-atlas",)
depends_on = None


def upgrade():
    op.execute(
        """
        -- Insertion du thème regroupant les attributs utilisés par GeoNature-atlas
        INSERT INTO taxonomie.bib_themes (nom_theme, desc_theme, ordre) 
        VALUES ('Atlas', 'Informations relatives à GeoNature-atlas', 2);

        -- Insertion des attributs utilisés par GeoNature-atlas
        INSERT INTO taxonomie.bib_attributs (id_attribut, nom_attribut, label_attribut, liste_valeur_attribut, obligatoire, desc_attribut, type_attribut, type_widget, regne, group2_inpn, id_theme, ordre) VALUES 
        (100, 'atlas_description', 'Description', '{}', false, 'Donne une description du taxon pour l''atlas', 'text', 'textarea', NULL, NULL, (SELECT id_theme FROM taxonomie.bib_themes WHERE nom_theme= 'Atlas'), 1),
        (101, 'atlas_commentaire', 'Commentaire', '{}', false, 'Commentaire contextualisé sur le taxon pour GeoNature-Atlas', 'text', 'textarea', NULL, NULL, (SELECT id_theme FROM taxonomie.bib_themes WHERE nom_theme= 'Atlas'), 2),
        (102, 'atlas_milieu', 'Milieu', '{"values":["Forêt","Prairie","eau"]}', false, 'Habitat, milieu principal du taxon', 'text', 'multiselect', NULL, NULL, (SELECT id_theme FROM taxonomie.bib_themes WHERE nom_theme= 'Atlas'), 3),
        (103, 'atlas_chorologie', 'Chorologie', '{"values":["Méditéranéenne","Alpine","Océanique"]}', false, 'Distribution, répartition, région à grande échelle du taxon', 'text', 'select', NULL, NULL, (SELECT id_theme FROM taxonomie.bib_themes WHERE nom_theme= 'Atlas'), 4);
  
        """
    )


def downgrade():
    op.execute(
        """DELETE FROM taxonomie.bib_attributs 
           WHERE nom_attribut IN ('atlas_description', 'atlas_commentaire', 'atlas_milieu', 'atlas_chorologie' );
           DELETE FROM taxonomie.bib_themes WHERE nom_theme = 'Atlas';
        """
    )

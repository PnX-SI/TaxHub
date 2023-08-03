"""Save bib_nom data

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
    op.execute(
        """
        -- Création liste
        INSERT INTO taxonomie.bib_listes (nom_liste, desc_liste,  code_liste)
        VALUES(
            'Save bib_nom',
            'Liste contenant l''ensemble des cd_noms contenus historiquement dans la table bib_nom',
            'BIB_NOM'
        );
        -- Insertion des valeurs de bib_noms dans la liste
        INSERT INTO taxonomie.cor_nom_liste (cd_nom, id_liste)
        SELECT
            cd_nom,
            (SELECT id_liste FROM taxonomie.bib_listes WHERE code_liste ='BIB_NOM' LIMIT 1) AS id_liste
        FROM taxonomie.bib_noms AS bn ;
    """
    )
    # Création des attributs nom_vern et comments qui contiendrons les données contenues dans la table bib_nom
    op.execute(
        """
        INSERT INTO taxonomie.bib_themes (nom_theme, desc_theme, ordre)
        VALUES(
            'Save bib_nom',
            'Thème contenant les attributs correspondants aux données de la table bib_noms',
            100
        );

        INSERT INTO taxonomie.bib_attributs
        (nom_attribut, label_attribut, liste_valeur_attribut, desc_attribut, type_attribut, type_widget, regne, group2_inpn, id_theme, ordre)
        SELECT
            'bib_nom_comments',
            'Champ comments de la table bib_noms',
            '{}',
            'Champ comments de la table bib_noms',
            'text',
            'text',
            NULL,
            NULL,
            id_theme,
            1
        FROM taxonomie.bib_themes
        WHERE nom_theme = 'Save bib_nom';

        INSERT INTO taxonomie.bib_attributs
        (nom_attribut, label_attribut, liste_valeur_attribut, desc_attribut, type_attribut, type_widget, regne, group2_inpn, id_theme, ordre)
        SELECT
            'bib_nom_francais',
            'Champ nom français de la table bib_noms',
            '{}',
            'Champ nom français de la table bib_noms',
            'text',
            'text',
            NULL,
            NULL,
            id_theme,
            1
        FROM taxonomie.bib_themes
        WHERE nom_theme = 'Save bib_nom';

        INSERT INTO taxonomie.cor_taxon_attribut (id_attribut, valeur_attribut, cd_ref)
        SELECT
            (SELECT id_attribut FROM taxonomie.bib_attributs WHERE nom_attribut = 'bib_nom_francais' LIMIT 1),
            string_agg(DISTINCT nom_francais, ',') ,
            t.cd_ref
        FROM taxonomie.bib_noms AS bn
        JOIN taxonomie.taxref AS t
        ON t.cd_nom = bn.cd_nom
        WHERE NOT nom_francais IS NULL AND NOT nom_francais = ''
        GROUP BY t.cd_ref;

        INSERT INTO taxonomie.cor_taxon_attribut (id_attribut, valeur_attribut, cd_ref)
        SELECT
            (SELECT id_attribut FROM taxonomie.bib_attributs WHERE nom_attribut = 'bib_nom_comments' LIMIT 1),
            string_agg(DISTINCT comments, ',') ,
            t.cd_ref
        FROM taxonomie.bib_noms AS bn
        JOIN taxonomie.taxref AS t
        ON t.cd_nom = bn.cd_nom
        WHERE NOT comments IS NULL AND NOT COMMENTS = ''
        GROUP BY t.cd_ref;

    """
    )


def downgrade():
    op.execute(
        """
        DELETE FROM taxonomie.cor_nom_liste
        WHERE id_liste = (SELECT id_liste FROM taxonomie.bib_listes WHERE code_liste ='BIB_NOM' LIMIT 1);
        DELETE FROM taxonomie.bib_listes WHERE code_liste ='BIB_NOM';
    """
    )
    op.execute(
        """
        DELETE FROM taxonomie.cor_taxon_attribut
        WHERE id_attribut IN (
            SELECT id_attribut
            FROM taxonomie.bib_attributs
            WHERE nom_attribut IN ( 'bib_nom_comments' , 'bib_nom_francais')
        );
        DELETE FROM taxonomie.bib_attributs
        WHERE nom_attribut IN ( 'bib_nom_comments' , 'bib_nom_francais');
        DELETE FROM taxonomie.bib_attributs
        WHERE nom_attribut IN ( 'bib_nom_comments' , 'bib_nom_francais');
        DELETE FROM taxonomie.bib_themes
        WHERE nom_theme = 'Save bib_nom';
    """
    )

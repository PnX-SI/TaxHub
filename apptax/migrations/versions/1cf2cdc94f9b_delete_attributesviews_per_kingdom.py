"""Delete attributesviews_per_kingdom

Revision ID: 1cf2cdc94f9b
Revises: f6abb7857493
Create Date: 2023-03-23 09:50:20.148765

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "1cf2cdc94f9b"
down_revision = "f6abb7857493"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        DROP FUNCTION  IF EXISTS taxonomie.fct_build_bibtaxon_attributs_view(sregne character varying);
        DROP FUNCTION taxonomie.trg_fct_refresh_attributesviews_per_kingdom() CASCADE;
        """
    )


def downgrade():
    op.execute(
        """
        CREATE OR REPLACE FUNCTION taxonomie.fct_build_bibtaxon_attributs_view(sregne character varying)
        RETURNS void
        LANGUAGE plpgsql
        AS $function$
        DECLARE
            r taxonomie.bib_attributs%rowtype;
            sql_select text;
            sql_join text;
            sql_where text;
        BEGIN
            sql_join :=' FROM taxonomie.bib_noms b JOIN taxonomie.taxref taxref USING(cd_nom) ';
            sql_select := 'SELECT b.* ';
            sql_where := ' WHERE regne=''' ||$1 || '''';
            FOR r IN
                SELECT id_attribut, nom_attribut, label_attribut, liste_valeur_attribut,
                    obligatoire, desc_attribut, type_attribut, type_widget, regne,
                    group2_inpn
                FROM taxonomie.bib_attributs
                WHERE regne IS NULL OR regne=sregne
            LOOP
                sql_select := sql_select || ', ' || r.nom_attribut || '.valeur_attribut::' || r.type_attribut || ' as ' || r.nom_attribut;
                sql_join := sql_join || ' LEFT OUTER JOIN (SELECT valeur_attribut, cd_ref FROM taxonomie.cor_taxon_attribut WHERE id_attribut= '
                    || r.id_attribut || ') as  ' || r.nom_attribut || '  ON b.cd_ref= ' || r.nom_attribut || '.cd_ref ';

            --RETURN NEXT r; -- return current row of SELECT
            END LOOP;
            EXECUTE 'DROP VIEW IF EXISTS taxonomie.v_bibtaxon_attributs_' || sregne ;
            EXECUTE 'CREATE OR REPLACE VIEW taxonomie.v_bibtaxon_attributs_' || sregne ||  ' AS ' || sql_select || sql_join || sql_where ;
        END
        $function$
        ;

        CREATE OR REPLACE FUNCTION taxonomie.trg_fct_refresh_attributesviews_per_kingdom()
        RETURNS trigger AS
        $$
        DECLARE
        sregne text;
        BEGIN
            if NEW.regne IS NULL THEN
                FOR sregne IN
                    SELECT DISTINCT regne
                    FROM taxonomie.taxref t
                    JOIN taxonomie.bib_noms n
                    ON t.cd_nom = n.cd_nom
                    WHERE t.regne IS NOT NULL
                LOOP
                    PERFORM taxonomie.fct_build_bibtaxon_attributs_view(sregne);
                END LOOP;
            ELSE
                PERFORM taxonomie.fct_build_bibtaxon_attributs_view(NEW.regne);
            END IF;
        RETURN NEW;
        END
        $$  LANGUAGE plpgsql;


        CREATE TRIGGER trg_refresh_attributes_views_per_kingdom
            AFTER INSERT OR UPDATE OR DELETE ON taxonomie.bib_attributs
            FOR EACH ROW EXECUTE PROCEDURE taxonomie.trg_fct_refresh_attributesviews_per_kingdom();
        """
    )

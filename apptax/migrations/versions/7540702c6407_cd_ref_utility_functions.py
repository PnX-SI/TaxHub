"""cd_ref utility functions

Revision ID: 7540702c6407
Revises: 9c2c0254aadc
Create Date: 2021-08-24 16:44:49.250635

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7540702c6407"
down_revision = "9c2c0254aadc"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
    CREATE OR REPLACE FUNCTION taxonomie.match_binomial_taxref(mytaxonname character varying)
    RETURNS integer
    LANGUAGE plpgsql
    IMMUTABLE
    AS $function$
    --fonction permettant de rattacher un nom latin à son cd_nom taxref sur le principe suivant :
    -- - Si un seul cd_nom existe pour ce nom latin, la fonction retourne le cd_nom en question
    -- - Si plusieurs cd_noms existent pour ce nom latin, mais qu'ils appartiennent tous à un unique cd_ref, la fonction renvoie le cd_ref (= cd_nom valide)
    -- - Si plusieurs cd_noms existent pour ce nom latin et qu'ils correspondent à plusieurs cd_ref, la fonction renvoie NULL : le rattachement devra être fait manuellement
    DECLARE
        matching_cd integer;
    BEGIN
        IF (SELECT count(DISTINCT cd_nom) FROM taxonomie.taxref WHERE lb_nom=mytaxonname OR nom_valide=mytaxonname)=1 THEN matching_cd:= cd_nom FROM taxonomie.taxref WHERE lb_nom=mytaxonname OR nom_valide=mytaxonname ;
        ELSIF (SELECT count(DISTINCT cd_ref) FROM taxonomie.taxref WHERE lb_nom=mytaxonname OR nom_valide=mytaxonname)=1 THEN matching_cd:= DISTINCT(cd_ref) FROM taxonomie.taxref WHERE lb_nom=mytaxonname OR nom_valide=mytaxonname ;
        ELSE matching_cd:= NULL;
        END IF;
        RETURN matching_cd;
    END ;
    $function$
    """
    )

    op.execute(
        """
    CREATE OR REPLACE FUNCTION taxonomie.check_is_cd_ref(mycdnom integer)
     RETURNS boolean
     LANGUAGE plpgsql
     IMMUTABLE
    AS $function$
    --fonction permettant de vérifier si une valeur est bien un cd_ref existant
    --peut notamment servir pour les contraintes de certaines tables comme "gn_profiles.cor_taxons_profiles_parameters"
      BEGIN
        IF EXISTS( SELECT cd_ref FROM taxonomie.taxref WHERE cd_ref=mycdnom )
            THEN
          RETURN true;
        ELSE
            RAISE EXCEPTION 'Error : The code entered as argument is not a valid cd_ref' ;
        END IF;
        RETURN false;
      END;
    $function$
    """
    )


def downgrade():
    op.execute("DROP FUNCTION taxonomie.match_binomial_taxref")
    op.execute("DROP FUNCTION taxonomie.check_is_cd_ref")

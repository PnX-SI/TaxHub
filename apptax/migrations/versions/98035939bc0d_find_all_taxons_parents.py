"""find_all_taxons_parents

Revision ID: 98035939bc0d
Revises: 7540702c6407
Create Date: 2021-08-24 17:00:50.263855

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "98035939bc0d"
down_revision = "7540702c6407"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
    CREATE OR REPLACE FUNCTION taxonomie.find_all_taxons_parents(mycdnom integer)
     RETURNS TABLE(cd_nom integer, distance smallint)
     LANGUAGE plpgsql
     IMMUTABLE
    AS $function$
     -- Param : cd_nom d'un taxon quelque soit son rang.
     -- Retourne une table avec le cd_nom de tout les taxons parents et leur distance au dessus du cd_nom
     -- donné en argument. Les cd_nom sont ordonnées du plus bas (celui passé en argument) vers le plus
     -- haut (Dumm). Usage SELECT * FROM taxonomie.find_all_taxons_parents(457346);
      DECLARE
        inf RECORD;
     BEGIN
        RETURN QUERY
            WITH RECURSIVE parents AS (
                SELECT tx1.cd_nom,tx1.cd_sup, tx1.id_rang, 0 AS nr
                FROM taxonomie.taxref tx1
                WHERE tx1.cd_nom = taxonomie.find_cdref(mycdnom)
                UNION ALL
                SELECT tx2.cd_nom,tx2.cd_sup, tx2.id_rang, nr + 1
                    FROM parents p
                    JOIN taxonomie.taxref tx2 ON tx2.cd_nom = p.cd_sup
            )
            SELECT parents.cd_nom, nr::smallint AS distance FROM parents
            ORDER BY parents.nr;
      END;
    $function$
    """
    )


def downgrade():
    op.execute("DROP FUNCTION taxonomie.find_all_taxons_parents")

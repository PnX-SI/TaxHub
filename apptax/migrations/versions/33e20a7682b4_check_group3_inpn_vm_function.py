"""check_group3_inpn_vm_and_function

Revision ID: 33e20a7682b4
Revises: 32c5ed42bdbd
Create Date: 2023-09-04 08:23:34.336383

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "33e20a7682b4"
down_revision = "32c5ed42bdbd"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
            CREATE INDEX i_taxref_group3_inpn ON taxonomie.taxref USING btree (group3_inpn);
        """
    )

    op.execute(
        """
                CREATE OR REPLACE FUNCTION taxonomie.check_is_group3inpn(mygroup text)
                RETURNS boolean
                LANGUAGE plpgsql
                IMMUTABLE
                AS $function$
                --fonction permettant de vérifier si un texte proposé correspond à un group3_inpn dans la table taxref
                BEGIN
                    IF EXISTS (SELECT 1 FROM taxonomie.taxref WHERE group3_inpn = mygroup ) OR mygroup IS NULL THEN
                    RETURN true;
                    ELSE
                    RETURN false;
                    END IF;
                END;
                $function$;

"""
    )


def downgrade():
    op.execute("DROP INDEX taxonomie.i_taxref_group3_inpn")
    op.execute("DROP FUNCTION taxonomie.check_is_group3inpn")

"""Change tmedia before insert trigger

Revision ID: b9e157ffd8be
Revises: b7d734f490ff
Create Date: 2022-11-22 17:41:07.543733

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b9e157ffd8be"
down_revision = "b7d734f490ff"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
    CREATE OR REPLACE FUNCTION taxonomie.insert_t_medias()
    RETURNS trigger
    LANGUAGE plpgsql
    AS $function$
    DECLARE
        trimtitre text;
    BEGIN
        new.date_media = now();
        new.cd_ref = taxonomie.find_cdref(new.cd_ref);
        trimtitre = replace(new.titre, ' ', '');
        RETURN NEW;
    END;
    $function$
    ;
    """
    )


def downgrade():
    op.execute(
        """
    CREATE OR REPLACE FUNCTION taxonomie.insert_t_medias()
    RETURNS trigger
    LANGUAGE plpgsql
    AS $function$
    DECLARE
        trimtitre text;
    BEGIN
        new.date_media = now();
        trimtitre = replace(new.titre, ' ', '');
        RETURN NEW;
    END;
    $function$
    ;
    """
    )

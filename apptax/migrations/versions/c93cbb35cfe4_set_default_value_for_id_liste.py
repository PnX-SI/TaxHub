"""set default value for id_liste

Revision ID: c93cbb35cfe4
Revises: 98035939bc0d
Create Date: 2021-09-15 16:08:34.786123

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c93cbb35cfe4"
down_revision = "98035939bc0d"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TABLE taxonomie.bib_listes ALTER COLUMN id_liste DROP DEFAULT")
    op.execute("DROP SEQUENCE IF EXISTS taxonomie.bib_listes_id_liste_seq")

    op.execute(
        """
    CREATE SEQUENCE taxonomie.bib_listes_id_liste_seq
        START WITH 1
        INCREMENT BY 1
        NO MINVALUE
        NO MAXVALUE
        CACHE 1
    """
    )
    op.execute(
        "ALTER SEQUENCE taxonomie.bib_listes_id_liste_seq OWNED BY taxonomie.bib_listes.id_liste"
    )
    op.execute(
        "SELECT setval('taxonomie.bib_listes_id_liste_seq', (SELECT max(id_liste) FROM taxonomie.bib_listes), true)"
    )
    op.execute(
        "ALTER TABLE taxonomie.bib_listes ALTER COLUMN id_liste SET DEFAULT nextval('taxonomie.bib_listes_id_liste_seq')"
    )


def downgrade():
    op.execute("ALTER TABLE taxonomie.bib_listes ALTER COLUMN id_liste DROP DEFAULT")
    op.execute("DROP SEQUENCE IF EXISTS taxonomie.bib_listes_id_liste_seq")

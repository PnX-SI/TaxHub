"""delete bib_noms

Revision ID: f6abb7857493
Revises: b9e157ffd8be
Create Date: 2022-12-19 11:39:46.910735

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f6abb7857493'
down_revision = 'b9e157ffd8be'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
         DROP TABLE taxonomie.bib_noms;
    """)

def downgrade():
        op.execute(
        """

        CREATE TABLE taxonomie.bib_noms (
            id_nom SERIAL PRIMARY KEY,
            cd_nom integer,
            cd_ref integer,
            nom_francais character varying(1000),
            comments character varying(1000),
            CONSTRAINT check_is_valid_cd_ref CHECK ((cd_ref = taxonomie.find_cdref(cd_ref)))
        );

        ALTER TABLE ONLY taxonomie.bib_noms
            ADD CONSTRAINT bib_noms_cd_nom_key UNIQUE (cd_nom);

        CREATE INDEX i_bib_noms_cd_ref ON taxonomie.bib_noms USING btree (cd_ref);


        ALTER TABLE ONLY taxonomie.bib_noms
            ADD CONSTRAINT fk_bib_nom_taxref FOREIGN KEY (cd_nom) REFERENCES taxonomie.taxref(cd_nom);
        """)

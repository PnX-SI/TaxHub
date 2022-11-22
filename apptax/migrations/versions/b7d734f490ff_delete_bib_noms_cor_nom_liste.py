"""delete bib_noms cor_nom_liste

Revision ID: b7d734f490ff
Revises: 64d38dbe7739
Create Date: 2022-11-22 16:50:15.520049

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b7d734f490ff'
down_revision = '64d38dbe7739'
branch_labels = None
depends_on = None


def upgrade():
     op.execute(
        """
        ALTER TABLE taxonomie.cor_nom_liste ADD cd_nom int;

        UPDATE taxonomie.cor_nom_liste AS cnl SET  cd_nom = bn.cd_nom
        FROM taxonomie.bib_noms AS bn
        WHERE bn.id_nom = cnl.id_nom;

        ALTER TABLE taxonomie.cor_nom_liste DROP CONSTRAINT cor_nom_liste_pkey;
        ALTER TABLE taxonomie.cor_nom_liste DROP CONSTRAINT unique_cor_nom_liste_id_liste_id_nom;
        ALTER TABLE taxonomie.cor_nom_liste DROP CONSTRAINT cor_nom_listes_bib_listes_fkey;
        ALTER TABLE taxonomie.cor_nom_liste DROP CONSTRAINT cor_nom_listes_bib_noms_fkey;

        ALTER TABLE taxonomie.cor_nom_liste ADD CONSTRAINT cor_nom_liste_pkey PRIMARY KEY (cd_nom, id_liste);
        ALTER TABLE taxonomie.cor_nom_liste ADD CONSTRAINT unique_cor_nom_liste_id_liste_cd_nom UNIQUE (id_liste, cd_nom);
        ALTER TABLE taxonomie.cor_nom_liste ADD CONSTRAINT cor_nom_listes_bib_listes_fkey FOREIGN KEY (id_liste) REFERENCES taxonomie.bib_listes(id_liste) ON UPDATE CASCADE;
        ALTER TABLE taxonomie.cor_nom_liste ADD CONSTRAINT cor_nom_listes_taxref_fkey FOREIGN KEY (cd_nom) REFERENCES taxonomie.taxref(cd_nom) ON DELETE CASCADE ON UPDATE CASCADE;


        ALTER TABLE taxonomie.cor_nom_liste ALTER COLUMN id_nom DROP NOT NULL;

        """
     )


def downgrade():
     op.execute(
        """
        ALTER TABLE taxonomie.cor_nom_liste ADD CONSTRAINT cor_nom_liste_pkey;
        ALTER TABLE taxonomie.cor_nom_liste ADD CONSTRAINT unique_cor_nom_liste_id_liste_id_nom;
        ALTER TABLE taxonomie.cor_nom_liste ADD CONSTRAINT cor_nom_listes_bib_listes_fkey;
        ALTER TABLE taxonomie.cor_nom_liste ADD CONSTRAINT cor_nom_listes_bib_noms_fkey;

        ALTER TABLE taxonomie.cor_nom_liste DROP CONSTRAINT cor_nom_liste_pkey PRIMARY KEY (cd_nom, id_liste);
        ALTER TABLE taxonomie.cor_nom_liste DROP CONSTRAINT unique_cor_nom_liste_id_liste_cd_nom UNIQUE (id_liste, cd_nom);
        ALTER TABLE taxonomie.cor_nom_liste DROP CONSTRAINT cor_nom_listes_bib_listes_fkey FOREIGN KEY (id_liste) REFERENCES taxonomie.bib_listes(id_liste) ON UPDATE CASCADE;
        ALTER TABLE taxonomie.cor_nom_liste DROP CONSTRAINT cor_nom_listes_taxref_fkey FOREIGN KEY (cd_nom) REFERENCES taxonomie.taxref(cd_nom) ON DELETE CASCADE ON UPDATE CASCADE;


        ALTER TABLE taxonomie.cor_nom_liste ALTER COLUMN id_nom ADD NOT NULL;


        ALTER TABLE taxonomie.cor_nom_liste DROP cd_nom;
        """
     )

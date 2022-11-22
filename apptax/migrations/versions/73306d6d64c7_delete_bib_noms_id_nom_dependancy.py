"""delete bib_noms id_nom dependancy

Revision ID: 73306d6d64c7
Revises: b7d734f490ff
Create Date: 2022-11-22 17:13:15.380256

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '73306d6d64c7'
down_revision = 'b7d734f490ff'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
    CREATE OR REPLACE VIEW taxonomie.v_taxref_all_listes AS
    SELECT t.regne,
        t.phylum,
        t.classe,
        t.ordre,
        t.famille,
        t.group1_inpn,
        t.group2_inpn,
        t.cd_nom,
        t.cd_ref,
        t.nom_complet,
        t.nom_valide,
        t.nom_vern AS nom_vern,
        t.lb_nom,
        d.id_liste
   FROM taxonomie.taxref t
   JOIN taxonomie.cor_nom_liste d ON t.cd_nom = d.cd_nom;
   """)


def downgrade():
    op.execute("""
    CREATE OR REPLACE VIEW taxonomie.v_taxref_all_listes
    AS WITH bib_nom_lst AS (
            SELECT cor_nom_liste.id_nom,
                bib_noms.cd_nom,
                bib_noms.nom_francais,
                cor_nom_liste.id_liste
            FROM taxonomie.cor_nom_liste
                JOIN taxonomie.bib_noms USING (id_nom)
            )
    SELECT t.regne,
        t.phylum,
        t.classe,
        t.ordre,
        t.famille,
        t.group1_inpn,
        t.group2_inpn,
        t.cd_nom,
        t.cd_ref,
        t.nom_complet,
        t.nom_valide,
        d.nom_francais AS nom_vern,
        t.lb_nom,
        d.id_liste
    FROM taxonomie.taxref t
        JOIN bib_nom_lst d ON t.cd_nom = d.cd_nom;
   """)

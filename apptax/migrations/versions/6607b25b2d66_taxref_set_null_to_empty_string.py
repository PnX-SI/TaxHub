"""Taxref : set null to empty string

Revision ID: 6607b25b2d66
Revises: 23c25552d707
Create Date: 2023-04-27 15:41:41.657864

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6607b25b2d66"
down_revision = "23c25552d707"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        UPDATE taxonomie.taxref SET id_statut = NULL WHERE id_statut = '';
        UPDATE taxonomie.taxref SET id_rang = NULL WHERE id_rang = '';
        UPDATE taxonomie.taxref SET regne = NULL WHERE regne = '';
        UPDATE taxonomie.taxref SET phylum = NULL WHERE phylum = '';
        UPDATE taxonomie.taxref SET classe = NULL WHERE classe = '';
        UPDATE taxonomie.taxref SET ordre = NULL WHERE ordre = '';
        UPDATE taxonomie.taxref SET famille = NULL WHERE famille = '';
        UPDATE taxonomie.taxref SET sous_famille = NULL WHERE sous_famille = '';
        UPDATE taxonomie.taxref SET tribu = NULL WHERE tribu = '';
        UPDATE taxonomie.taxref SET lb_nom = NULL WHERE lb_nom = '';
        UPDATE taxonomie.taxref SET lb_auteur = NULL WHERE lb_auteur = '';
        UPDATE taxonomie.taxref SET nom_complet = NULL WHERE nom_complet = '';
        UPDATE taxonomie.taxref SET nom_complet_html = NULL WHERE nom_complet_html = '';
        UPDATE taxonomie.taxref SET nom_valide = NULL WHERE nom_valide = '';
        UPDATE taxonomie.taxref SET nom_vern = NULL WHERE nom_vern = '';
        UPDATE taxonomie.taxref SET nom_vern_eng = NULL WHERE nom_vern_eng = '';
        UPDATE taxonomie.taxref SET group1_inpn = NULL WHERE group1_inpn = '';
        UPDATE taxonomie.taxref SET group2_inpn = NULL WHERE group2_inpn = '';
        UPDATE taxonomie.taxref SET url = NULL WHERE url = '';
        UPDATE taxonomie.taxref SET group3_inpn = NULL WHERE group3_inpn = '';
    """
    )


def downgrade():
    op.execute(
        """
        UPDATE taxonomie.taxref SET id_statut = '' WHERE id_statut IS NULL AND id_statut IN (SELECT id_statut FROM taxonomie.bib_taxref_statuts );
        UPDATE taxonomie.taxref SET id_rang = '' WHERE id_rang IS NULL AND id_rang IN (SELECT id_rang FROM taxonomie.bib_taxref_statuts );
        UPDATE taxonomie.taxref SET regne = '' WHERE regne IS NULL;
        UPDATE taxonomie.taxref SET phylum = '' WHERE phylum IS NULL;
        UPDATE taxonomie.taxref SET classe = '' WHERE classe IS NULL;
        UPDATE taxonomie.taxref SET ordre = '' WHERE ordre IS NULL;
        UPDATE taxonomie.taxref SET famille = '' WHERE famille IS NULL;
        UPDATE taxonomie.taxref SET sous_famille = '' WHERE sous_famille IS NULL;
        UPDATE taxonomie.taxref SET tribu = '' WHERE tribu IS NULL;
        UPDATE taxonomie.taxref SET lb_nom = '' WHERE lb_nom IS NULL;
        UPDATE taxonomie.taxref SET lb_auteur = '' WHERE lb_auteur IS NULL;
        UPDATE taxonomie.taxref SET nom_complet = '' WHERE nom_complet IS NULL;
        UPDATE taxonomie.taxref SET nom_complet_html = '' WHERE nom_complet_html IS NULL;
        UPDATE taxonomie.taxref SET nom_valide = '' WHERE nom_valide IS NULL;
        UPDATE taxonomie.taxref SET nom_vern = '' WHERE nom_vern IS NULL;
        UPDATE taxonomie.taxref SET nom_vern_eng = '' WHERE nom_vern_eng IS NULL;
        UPDATE taxonomie.taxref SET group1_inpn = '' WHERE group1_inpn IS NULL;
        UPDATE taxonomie.taxref SET group2_inpn = '' WHERE group2_inpn IS NULL;
        UPDATE taxonomie.taxref SET url = '' WHERE url IS NULL;
        UPDATE taxonomie.taxref SET group3_inpn = '' WHERE group3_inpn IS NULL;
    """
    )

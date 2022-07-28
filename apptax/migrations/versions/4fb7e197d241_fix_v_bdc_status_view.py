"""create taxonomie.v_bdc_status view

Revision ID: 4fb7e197d241
Revises: c93cbb35cfe4
Create Date: 2021-09-16 15:28:42.193677

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4fb7e197d241"
down_revision = "c93cbb35cfe4"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
CREATE OR REPLACE VIEW taxonomie.v_bdc_status AS
  SELECT s.cd_nom, s.cd_ref, s.rq_statut, v.code_statut , v.label_statut,
    t.cd_type_statut, ty.thematique, ty.lb_type_statut, ty.regroupement_type, 
    cd_st_text, t.cd_sig, t.cd_doc, t.niveau_admin, t.cd_iso3166_1, t.cd_iso3166_2,
    t.full_citation, t.doc_url, ty.type_value
  FROM taxonomie.bdc_statut_taxons AS s
    JOIN taxonomie.bdc_statut_cor_text_values AS c
      ON s.id_value_text  = c.id_value_text
    JOIN taxonomie.bdc_statut_text AS t
      ON t.id_text  = c.id_text
    JOIN taxonomie.bdc_statut_values AS v
      ON v.id_value = c.id_value
    JOIN taxonomie.bdc_statut_type AS ty
      ON ty.cd_type_statut = t.cd_type_statut
  WHERE t.ENABLE = true ;
"""
    )


def downgrade():
    op.execute("DROP VIEW IF EXISTS taxonomie.v_bdc_status ;")

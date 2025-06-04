"""add taxon-area-status materialized view

Revision ID: d669606710b3
Revises: eb7fe5a32655
Create Date: 2025-06-04 11:58:39.247005

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d669606710b3"
down_revision = "eb7fe5a32655"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        CREATE MATERIALIZED VIEW taxonomie.taxon_area_status AS
            WITH agg_code_status AS (
                SELECT
                    ta.cd_ref AS cd_ref,
                    cta.id_area,
                    te.cd_type_statut,
                    jsonb_agg(DISTINCT bdc_statut_values.code_statut) AS code_statuts
                FROM taxonomie.bdc_statut_taxons AS ta
                    JOIN taxonomie.bdc_statut_cor_text_values AS bsctv
                        ON bsctv.id_value_text = ta.id_value_text
                    JOIN taxonomie.bdc_statut_text AS te
                        ON te.id_text = bsctv.id_text
                    JOIN taxonomie.bdc_statut_cor_text_area AS cta
                        ON cta.id_text = te.id_text
                    LEFT JOIN taxonomie.bdc_statut_values
                        ON bdc_statut_values.id_value = bsctv.id_value
                GROUP BY
                    ta.cd_ref,
                    cta.id_area,
                    te.cd_type_statut
            )
            SELECT
                acs.cd_ref,
                acs.id_area,
                jsonb_object_agg(
                    acs.cd_type_statut,
                    acs.code_statuts
                ) AS status
            FROM agg_code_status AS acs
            GROUP BY acs.cd_ref, acs.id_area
            WITH DATA;
        """
    )
    op.execute(
        """
        CREATE INDEX taxon_area_status_cd_ref_id_area_idx
        ON taxonomie.taxon_area_status USING btree (cd_ref, id_area) ;
        """
    )

    op.execute(
        """
        CREATE INDEX taxon_area_status_status_idx
        ON taxonomie.taxon_area_status USING gin (status) ;
        """
    )


def downgrade():
    op.execute(
        """
        DROP MATERIALIZED VIEW taxonomie.taxon_area_status;
        """
    )

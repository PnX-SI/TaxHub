"""Add table to link bdc_status and ref_geo

Revision ID: 1b1a3f5cd107
Revises: c4415009f164
Create Date: 2022-03-29 15:55:49.337701

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "1b1a3f5cd107"
down_revision = "c4415009f164"
branch_labels = None
depends_on = ("e0ac4c9f5c0a",)  # ref_geo schema


def upgrade():
    op.execute(
        """
    CREATE TABLE taxonomie.bdc_statut_cor_text_area (
        id_text int4 NOT NULL,
        id_area int4 NOT NULL,
        CONSTRAINT bdc_statut_cor_text_area_pkey PRIMARY KEY (id_text, id_area),
        CONSTRAINT fk_bdc_statut_cor_text_area_id_text FOREIGN KEY (id_text) REFERENCES taxonomie.bdc_statut_text(id_text) ON UPDATE CASCADE,
        CONSTRAINT fk_bdc_statut_cor_text_area_id_area FOREIGN KEY (id_area) REFERENCES ref_geo.l_areas(id_area) ON UPDATE CASCADE
    )
    """
    )


def downgrade():
    op.execute("DROP TABLE taxonomie.bdc_statut_cor_text_area")

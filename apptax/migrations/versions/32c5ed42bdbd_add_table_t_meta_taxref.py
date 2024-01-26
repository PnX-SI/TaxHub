"""Add table: t_meta_taxref

Revision ID: 32c5ed42bdbd
Revises: 3bd542b72955
Create Date: 2023-06-23 15:51:00.031901

"""

import datetime
from alembic import op
from sqlalchemy import Column, Unicode, DateTime, Integer, func
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "32c5ed42bdbd"
down_revision = "3bd542b72955"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "t_meta_taxref",
        Column("referencial_name", Unicode, primary_key=True),
        Column("version", Integer, primary_key=True),
        Column("update_date", DateTime, server_default=func.now()),
        schema="taxonomie",
    )
    op.execute(
        """
        WITH meta_taxref AS (
            SELECT 1019039 as max_cd_nom, 16 AS taxref_version
            UNION
            SELECT 1002708  as max_cd_nom, 15 AS taxref_version
            UNION
            SELECT 972486  as max_cd_nom, 14 AS taxref_version
            UNION
            SELECT 935095  as max_cd_nom, 13 AS taxref_version
            UNION
            SELECT 887126  as max_cd_nom, 11 AS taxref_version
        )
        INSERT INTO taxonomie.t_meta_taxref (referencial_name, version)
        SELECT 'taxref', taxref_version
        FROM taxonomie.taxref AS t
        JOIN meta_taxref m
        ON t.cd_nom = max_cd_nom
        ORDER BY cd_nom DESC
        LIMIT 1;
    """
    )


def downgrade():
    op.drop_table(table_name="t_meta_taxref", schema="taxonomie")

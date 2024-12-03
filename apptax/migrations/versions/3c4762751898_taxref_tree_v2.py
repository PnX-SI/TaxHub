"""create vm_taxref_tree v2

Revision ID: 3c4762751898
Revises: 83d7105edb76
Create Date: 2024-12-03 13:30:26.521216

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3c4762751898"
down_revision = "83d7105edb76"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("DROP MATERIALIZED VIEW IF EXISTS taxonomie.vm_taxref_tree")
    op.execute(
        """
        CREATE MATERIALIZED VIEW taxonomie.vm_taxref_tree AS
        WITH RECURSIVE
        biota AS (
                SELECT
                    t.cd_nom,
                    t.cd_ref::TEXT::ltree AS path
                FROM
                    taxonomie.taxref t
                WHERE
                    t.cd_nom = 349525
            UNION ALL
                SELECT
                    child.cd_nom AS cd_nom,
                    parent.path || child.cd_ref::TEXT AS path
                FROM
                    taxonomie.taxref child
                JOIN
                    taxonomie.taxref child_ref ON child.cd_ref = child_ref.cd_nom
                JOIN
                    biota parent ON parent.cd_nom = child_ref.cd_sup
        ),
        orphans AS (
                SELECT
                    t.cd_nom,
                    t.cd_ref::TEXT::ltree AS path
                FROM
                    taxonomie.taxref t
                JOIN
                    taxonomie.taxref t_ref ON t.cd_ref = t_ref.cd_nom
                LEFT JOIN
                    taxonomie.taxref parent ON t_ref.cd_sup = parent.cd_nom AND parent.cd_nom != t_ref.cd_nom
                WHERE
                    parent.cd_nom IS NULL
        )
        SELECT
            cd_nom,
            path
        FROM
            biota
        UNION DISTINCT -- do not include biota twice
        SELECT
            cd_nom,
            path
        FROM
            orphans
        WITH DATA;
        """
    )
    op.create_index(
        index_name="taxref_tree_cd_nom_idx",
        schema="taxonomie",
        table_name="vm_taxref_tree",
        columns=["cd_nom"],
        unique=True,
    )
    # required for these operators: <, <=, =, >=, >, @>, <@, @, ~, ?
    op.create_index(
        index_name="taxref_tree_path_idx",
        schema="taxonomie",
        table_name="vm_taxref_tree",
        columns=["path"],
        postgresql_using="gist",
    )


def downgrade():
    op.execute("DROP MATERIALIZED VIEW taxonomie.vm_taxref_tree")

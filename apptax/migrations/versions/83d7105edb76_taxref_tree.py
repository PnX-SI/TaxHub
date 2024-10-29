"""create vm_taxref_tree

Revision ID: 83d7105edb76
Revises: 44447746cacc
Create Date: 2024-10-05 17:40:11.302423

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "83d7105edb76"
down_revision = "6a20cd1055ec"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        CREATE MATERIALIZED VIEW taxonomie.vm_taxref_tree AS
        WITH RECURSIVE childs AS (
                SELECT
                    t.cd_nom,
                    t.cd_ref::TEXT::ltree AS path,
                    1 AS path_length,
                    t_ref.cd_sup AS cd_sup
                FROM
                    taxonomie.taxref t
                JOIN taxonomie.taxref t_ref ON
                    t.cd_ref = t_ref.cd_nom
            UNION ALL
                SELECT
                    child.cd_nom AS cd_nom,
                    parent.cd_ref::TEXT || child.path AS path,
                    child.path_length + 1 AS path_length,
                    parent_ref.cd_sup AS cd_sup
                FROM
                    childs child
                JOIN taxonomie.taxref parent ON
                    child.cd_sup = parent.cd_nom
                JOIN taxonomie.taxref parent_ref ON
                    parent.cd_ref = parent_ref.cd_nom
        )
        SELECT
            DISTINCT ON
            (cd_nom) cd_nom,
            path
        FROM
            childs
        ORDER BY
            cd_nom,
            path_length DESC
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

"""Add vm_taxref_list_forautocomplete index

Revision ID: 27fd7e2b4b79
Revises: f2c36312b3de
Create Date: 2023-01-09 12:17:41.143889

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "27fd7e2b4b79"
down_revision = "f2c36312b3de"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        -- Creation des index de la vue matérialisée vm_taxref_list_forautocomplete
        CREATE unique INDEX i_vm_taxref_list_forautocomplete_gid
        ON taxonomie.vm_taxref_list_forautocomplete (gid);
        CREATE INDEX i_vm_taxref_list_forautocomplete_cd_nom
        ON taxonomie.vm_taxref_list_forautocomplete (cd_nom ASC NULLS LAST);
        CREATE INDEX i_vm_taxref_list_forautocomplete_search_name
        ON taxonomie.vm_taxref_list_forautocomplete (search_name ASC NULLS LAST);
        CREATE INDEX i_tri_vm_taxref_list_forautocomplete_search_name
        ON taxonomie.vm_taxref_list_forautocomplete
        USING gist
        (search_name  gist_trgm_ops);
    """
    )


def downgrade():
    op.execute(
        """
        -- Suppression des index de la vue matérialisée vm_taxref_list_forautocomplete
        DROP INDEX taxonomie.i_vm_taxref_list_forautocomplete_gid;
        DROP INDEX taxonomie.i_vm_taxref_list_forautocomplete_cd_nom;
        DROP INDEX taxonomie.i_vm_taxref_list_forautocomplete_search_name;
        DROP INDEX taxonomie.i_tri_vm_taxref_list_forautocomplete_search_name;
    """
    )

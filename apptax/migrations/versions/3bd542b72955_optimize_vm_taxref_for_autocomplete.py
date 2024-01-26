"""optimize_vm_taxref_for_autocomplete

Revision ID: 3bd542b72955
Revises: 188bc535258a
Create Date: 2023-04-25 09:46:47.311160

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "3bd542b72955"
down_revision = "6607b25b2d66"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        DROP MATERIALIZED VIEW taxonomie.vm_taxref_list_forautocomplete;
        CREATE MATERIALIZED VIEW taxonomie.vm_taxref_list_forautocomplete AS
        SELECT row_number() OVER () AS gid,
        t.cd_nom,
        t.cd_ref,
        t.search_name,
        unaccent(t.search_name) AS unaccent_search_name,
        t.nom_valide,
        t.lb_nom,
        t.nom_vern,
        t.regne,
        t.group2_inpn
        FROM ( SELECT t_1.cd_nom,
                    t_1.cd_ref,
                    concat(t_1.lb_nom, ' = <i>', t_1.nom_valide, '</i>', ' - [', t_1.id_rang, ' - ', t_1.cd_nom, ']') AS search_name,
                    t_1.nom_valide,
                    t_1.lb_nom,
                    t_1.nom_vern,
                    t_1.regne,
                    t_1.group2_inpn
                FROM taxonomie.taxref t_1
                UNION
                SELECT DISTINCT t_1.cd_nom,
                    t_1.cd_ref,
                    concat(split_part(t_1.nom_vern::text, ','::text, 1), ' = <i>', t_1.nom_valide, '</i>', ' - [', t_1.id_rang, ' - ', t_1.cd_ref, ']') AS search_name,
                    t_1.nom_valide,
                    t_1.lb_nom,
                    t_1.nom_vern,
                    t_1.regne,
                    t_1.group2_inpn
                FROM taxonomie.taxref t_1
                WHERE t_1.nom_vern IS NOT NULL AND t_1.cd_nom = t_1.cd_ref
                )t
        WITH DATA;
        """
    )

    op.execute(
        """
        CREATE INDEX i_tri_vm_taxref_list_forautocomplete_search_name ON taxonomie.vm_taxref_list_forautocomplete USING gin (unaccent_search_name gin_trgm_ops);
        CREATE INDEX i_vm_taxref_list_forautocomplete_cd_nom ON taxonomie.vm_taxref_list_forautocomplete USING btree (cd_nom);
        CREATE UNIQUE INDEX i_vm_taxref_list_forautocomplete_gid ON taxonomie.vm_taxref_list_forautocomplete USING btree (gid);
        """
    )


def downgrade():
    op.execute(
        """
        DROP MATERIALIZED VIEW taxonomie.vm_taxref_list_forautocomplete;
        CREATE MATERIALIZED VIEW taxonomie.vm_taxref_list_forautocomplete AS
        SELECT row_number() OVER () AS gid,
        t.cd_nom,
        t.cd_ref,
        t.search_name,
        t.nom_valide,
        t.lb_nom,
        t.nom_vern,
        t.regne,
        t.group2_inpn
        FROM ( SELECT t_1.cd_nom,
                    t_1.cd_ref,
                    concat(t_1.lb_nom, ' = <i>', t_1.nom_valide, '</i>', ' - [', t_1.id_rang, ' - ', t_1.cd_nom, ']') AS search_name,
                    t_1.nom_valide,
                    t_1.lb_nom,
                    t_1.nom_vern,
                    t_1.regne,
                    t_1.group2_inpn
                FROM taxonomie.taxref t_1
                UNION
                SELECT DISTINCT t_1.cd_nom,
                    t_1.cd_ref,
                    concat(split_part(t_1.nom_vern::text, ','::text, 1), ' = <i>', t_1.nom_valide, '</i>', ' - [', t_1.id_rang, ' - ', t_1.cd_ref, ']') AS search_name,
                    t_1.nom_valide,
                    t_1.lb_nom,
                    t_1.nom_vern,
                    t_1.regne,
                    t_1.group2_inpn
                FROM taxonomie.taxref t_1
                WHERE t_1.nom_vern IS NOT NULL AND t_1.cd_nom = t_1.cd_ref
                )t
        WITH DATA;
        """
    )

    op.execute(
        """
        CREATE unique INDEX i_vm_taxref_list_forautocomplete_gid ON taxonomie.vm_taxref_list_forautocomplete (gid);
        CREATE INDEX i_vm_taxref_list_forautocomplete_cd_nom ON taxonomie.vm_taxref_list_forautocomplete (cd_nom ASC NULLS LAST);
        CREATE INDEX i_vm_taxref_list_forautocomplete_search_name ON taxonomie.vm_taxref_list_forautocomplete (search_name ASC NULLS LAST);
        CREATE INDEX i_tri_vm_taxref_list_forautocomplete_search_name ON taxonomie.vm_taxref_list_forautocomplete USING gist (search_name  gist_trgm_ops);
        """
    )

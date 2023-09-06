"""fix nom_vern in vm_taxref_list_forautocomplete

Revision ID: 0db13d65cb27
Revises: 52d1b5dd965e
Create Date: 2023-09-06 06:49:50.248414

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0db13d65cb27"
down_revision = "52d1b5dd965e"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
            -- taxonomie.vm_taxref_list_forautocomplete source

            DROP MATERIALIZED VIEW IF EXISTS taxonomie.vm_taxref_list_forautocomplete;

            CREATE MATERIALIZED VIEW taxonomie.vm_taxref_list_forautocomplete
            TABLESPACE pg_default
            AS SELECT row_number() OVER () AS gid,
                t.cd_nom,
                t.cd_ref,
                t.search_name,
                unaccent(t.search_name) AS unaccent_search_name,
                t.nom_valide,
                t.lb_nom,
                t.nom_vern,
                t.regne,
                t.group2_inpn,
                t.group3_inpn
            FROM ( SELECT t_1.cd_nom,
                        t_1.cd_ref,
                        concat(t_1.lb_nom, ' = <i>', t_1.nom_valide, '</i>', ' - [', t_1.id_rang, ' - ', t_1.cd_nom, ']') AS search_name,
                        t_1.nom_valide,
                        t_1.lb_nom,
                        t_1.nom_vern,
                        t_1.regne,
                        t_1.group2_inpn,
                        t_1.group3_inpn
                    FROM taxonomie.taxref t_1
                    UNION
                    SELECT DISTINCT t_1.cd_nom,
                        t_1.cd_ref,
                        concat(t_1.nom_vern::text, ' = <i>', t_1.nom_valide, '</i>', ' - [', t_1.id_rang, ' - ', t_1.cd_ref, ']') AS search_name,
                        t_1.nom_valide,
                        t_1.lb_nom,
                        t_1.nom_vern,
                        t_1.regne,
                        t_1.group2_inpn,
                        t_1.group3_inpn
                    FROM taxonomie.taxref t_1
                    WHERE t_1.nom_vern IS NOT NULL AND t_1.cd_nom = t_1.cd_ref) t
            WITH DATA;

            -- View indexes:
            CREATE INDEX i_tri_vm_taxref_list_forautocomplete_search_name ON taxonomie.vm_taxref_list_forautocomplete USING gin (unaccent_search_name gin_trgm_ops);
            CREATE INDEX i_vm_taxref_list_forautocomplete_cd_nom ON taxonomie.vm_taxref_list_forautocomplete USING btree (cd_nom);
            CREATE UNIQUE INDEX i_vm_taxref_list_forautocomplete_gid ON taxonomie.vm_taxref_list_forautocomplete USING btree (gid);
        """
    )


def downgrade():
    op.execute(
        """
            -- taxonomie.vm_taxref_list_forautocomplete source

            DROP MATERIALIZED VIEW IF EXISTS taxonomie.vm_taxref_list_forautocomplete;

            CREATE MATERIALIZED VIEW taxonomie.vm_taxref_list_forautocomplete
            TABLESPACE pg_default
            AS SELECT row_number() OVER () AS gid,
                t.cd_nom,
                t.cd_ref,
                t.search_name,
                unaccent(t.search_name) AS unaccent_search_name,
                t.nom_valide,
                t.lb_nom,
                t.nom_vern,
                t.regne,
                t.group2_inpn,
                t.group3_inpn
            FROM ( SELECT t_1.cd_nom,
                        t_1.cd_ref,
                        concat(t_1.lb_nom, ' = <i>', t_1.nom_valide, '</i>', ' - [', t_1.id_rang, ' - ', t_1.cd_nom, ']') AS search_name,
                        t_1.nom_valide,
                        t_1.lb_nom,
                        t_1.nom_vern,
                        t_1.regne,
                        t_1.group2_inpn,
                        t_1.group3_inpn
                    FROM taxonomie.taxref t_1
                    UNION
                    SELECT DISTINCT t_1.cd_nom,
                        t_1.cd_ref,
                        concat(split_part(t_1.nom_vern, ',', 1), ' = <i>', t_1.nom_valide, '</i>', ' - [', t_1.id_rang, ' - ', t_1.cd_ref, ']') AS search_name,
                        t_1.nom_valide,
                        t_1.lb_nom,
                        t_1.nom_vern,
                        t_1.regne,
                        t_1.group2_inpn,
                        t_1.group3_inpn
                    FROM taxonomie.taxref t_1
                    WHERE t_1.nom_vern IS NOT NULL AND t_1.cd_nom = t_1.cd_ref) t
            WITH DATA;

            -- View indexes:
            CREATE INDEX i_tri_vm_taxref_list_forautocomplete_search_name ON taxonomie.vm_taxref_list_forautocomplete USING gin (unaccent_search_name gin_trgm_ops);
            CREATE INDEX i_vm_taxref_list_forautocomplete_cd_nom ON taxonomie.vm_taxref_list_forautocomplete USING btree (cd_nom);
            CREATE UNIQUE INDEX i_vm_taxref_list_forautocomplete_gid ON taxonomie.vm_taxref_list_forautocomplete USING btree (gid);
        """
    )

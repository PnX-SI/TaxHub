"""fix vm_taxref_for_autocomplete

Revision ID: f2c36312b3de
Revises: 1b1a3f5cd107
Create Date: 2022-10-17 14:13:26.169134

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f2c36312b3de"
down_revision = "1b1a3f5cd107"
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


def downgrade():
    op.execute(
        """
        CREATE MATERIALIZED VIEW taxonomie.vm_taxref_list_forautocomplete
        TABLESPACE pg_default
        AS SELECT row_number() OVER () AS gid,
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
                    concat(t_1.lb_nom, ' =  <i> ', t_1.nom_valide, '</i>', ' - [', t_1.id_rang, ' - ', t_1.cd_nom, ']') AS search_name,
                    t_1.nom_valide,
                    t_1.lb_nom,
                    t_1.nom_vern,
                    t_1.regne,
                    t_1.group2_inpn
                FROM taxonomie.taxref t_1
                UNION
                SELECT DISTINCT t_1.cd_nom,
                    t_1.cd_ref,
                    concat(split_part(t_1.nom_vern::text, ','::text, 1), ' =  <i> ', t_1.nom_valide, '</i>', ' - [', t_1.id_rang, ' - ', t_1.cd_ref, ']') AS search_name,
                    t_1.nom_valide,
                    t_1.lb_nom,
                    t_1.nom_vern,
                    t_1.regne,
                    t_1.group2_inpn
                FROM taxonomie.taxref t_1
                WHERE t_1.nom_vern IS NOT NULL AND t_1.cd_nom = t_1.cd_ref) t
        WITH DATA;
        """
    )

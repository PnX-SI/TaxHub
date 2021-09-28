""" Create herited attributes view

Revision ID: dbb7d939fef0
Revises: 4fb7e197d241
Create Date: 2021-09-28 11:49:57.654351

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dbb7d939fef0'
down_revision = '4fb7e197d241'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        CREATE MATERIALIZED VIEW taxonomie.taxref_tree
        AS WITH RECURSIVE x AS (
                SELECT t.cd_nom as cd_ref,
                    t.cd_nom::text::ltree AS path
                FROM taxonomie.taxref t
                WHERE t.cd_sup IS NULL AND t.cd_nom = t.cd_ref
                UNION ALL
                SELECT y.cd_nom AS cd_ref,
                    ltree_addtext(x_1.path, y.cd_nom::text) AS path
                FROM x x_1,
                    taxonomie.taxref y
                WHERE y.cd_nom = y.cd_ref AND x_1.cd_ref = y.cd_sup
                )
        SELECT x.cd_ref,
            x.path
        FROM x
        WITH DATA;

        -- View indexes:
        CREATE UNIQUE INDEX taxref_tree_cd_nom_idx ON taxonomie.taxref_tree USING btree (cd_ref);
        CREATE INDEX taxref_tree_path_idx ON taxonomie.taxref_tree USING gist (path); -- TRES important pour les perfs
    """)
    op.execute("""
        ALTER TABLE taxonomie.bib_attributs ADD recursif BOOLEAN DEFAULT(false);
    """)
    op.execute("""
        CREATE OR REPLACE VIEW taxonomie.v_recursif_cor_taxon_attribut AS
        WITH rec_bib_nom AS (
            SELECT p.cd_ref p_cd_ref, nlevel(p.path), bn.*
            FROM taxonomie.taxref_tree child
            JOIN taxonomie.bib_noms bn
            ON child.cd_ref = bn.cd_ref
            JOIN taxonomie.taxref_tree p
            ON child.path <@ p.PATH
        )
        SELECT * -- Attributs hérités c-a-d avec la propriétée récursif à TRUE
        FROM (
            SELECT  DISTINCT ON (n.cd_nom, n.cd_ref, cta.id_attribut) n.p_cd_ref, cta.id_attribut , cta.valeur_attribut , n.cd_ref
            FROM taxonomie.cor_taxon_attribut cta
            JOIN taxonomie.bib_attributs ba
            ON ba.id_attribut = cta.id_attribut AND recursif IS TRUE
            JOIN rec_bib_nom n
            ON n.p_cd_ref = cta.cd_ref
            ORDER BY n.cd_nom, cd_ref, cta.id_attribut , nlevel DESC
        ) AS h
        UNION -- Attributs non hérités
        SELECT cta.cd_ref, cta.id_attribut , cta.valeur_attribut , cta.cd_ref
        FROM taxonomie.cor_taxon_attribut cta
        JOIN taxonomie.bib_attributs ba
        ON ba.id_attribut = cta.id_attribut AND recursif IS FALSE;
    """)


def downgrade():
    op.execute("""
        DROP VIEW taxonomie.v_recursif_cor_taxon_attribut;
    """)
    op.execute("""
        ALTER TABLE taxonomie.bib_attributs DROP COLUMN recursif;
    """)
    op.execute("""
        DROP INDEX taxonomie.taxref_tree_cd_nom_idx;
        DROP INDEX taxonomie.taxref_tree_path_idx;
        DROP MATERIALIZED VIEW taxonomie.taxref_tree;
    """)

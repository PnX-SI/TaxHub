--Construction

CREATE EXTENSION IF NOT EXISTS ltree;

CREATE MATERIALIZED VIEW taxonomie.taxref_tree
AS WITH RECURSIVE x AS (
         SELECT t.cd_nom,
            t.cd_nom::text::ltree AS path
           FROM taxonomie.taxref t
          WHERE t.cd_sup IS NULL AND t.cd_nom = t.cd_ref
        UNION ALL
         SELECT y.cd_nom,
            ltree_addtext(x_1.path, y.cd_nom::text) AS path
           FROM x x_1,
            taxonomie.taxref y
          WHERE y.cd_nom = y.cd_ref AND x_1.cd_nom = y.cd_sup
        )
 SELECT x.cd_nom,
    x.path
   FROM x
WITH DATA;

-- View indexes:
CREATE UNIQUE INDEX taxref_tree_cd_nom_idx ON taxonomie.taxref_tree USING btree (cd_nom);
CREATE INDEX taxref_tree_path_idx ON taxonomie.taxref_tree USING gist (path); -- TRES important pour les perfs

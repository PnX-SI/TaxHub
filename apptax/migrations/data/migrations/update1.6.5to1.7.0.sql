
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- suppresion de la colonne id_liste de la table vm_taxref_for_autocomplete
-- la table devient une vue matérialisée et contient une seule fois tout taxref

-- Creation d'une vue matérialis&ée de tous les noms de Taxref mis en forme pour la recherche de taxons
DROP TABLE IF EXISTS taxonomie.vm_taxref_list_forautocomplete;
DROP MATERIALIZED VIEW IF EXISTS taxonomie.vm_taxref_list_forautocomplete;

CREATE MATERIALIZED VIEW taxonomie.vm_taxref_list_forautocomplete AS
SELECT
  row_number() OVER() as gid,
  t.cd_nom,
  t.cd_ref,
  t.search_name,
  t.nom_valide,
  t.lb_nom,
  t.regne,
  t.group2_inpn
FROM (
  -- PARTIE NOM SCIENTIFIQUE : ici on prend TOUS les synonymes.
  SELECT
    t_1.cd_nom,
    t_1.cd_ref,
    concat(t_1.lb_nom, ' =  <i> ', t_1.nom_valide, '</i>', ' - [', t_1.id_rang, ' - ', t_1.cd_nom , ']') AS search_name,
    t_1.nom_valide,
    t_1.lb_nom,
    t_1.regne,
    t_1.group2_inpn
  FROM taxonomie.taxref t_1
  UNION
  -- PARTIE NOM FRANCAIS : ici on prend une seule fois (DISTINCT) dans Taxref tous les taxons de références
  -- On ne prend pas les taxons qui n'ont pas de nom vern dans taxref,
  -- donc si un taxon n'a pas de nom vern dans Taxref, il n'est accessible que par son nom scientifique.
  SELECT DISTINCT
    t_1.cd_nom,
    t_1.cd_ref,
    concat(split_part(t_1.nom_vern, ',', 1), ' =  <i> ', t_1.nom_valide, '</i>', ' - [', t_1.id_rang, ' - ', t_1.cd_ref , ']' ) AS search_name,
    t_1.nom_valide,
    t_1.lb_nom,
    t_1.regne,
    t_1.group2_inpn
  FROM taxonomie.taxref t_1
  WHERE t_1.nom_vern IS NOT null and t_1.cd_nom = t_1.cd_ref
) t;
COMMENT ON MATERIALIZED VIEW taxonomie.vm_taxref_list_forautocomplete
    IS 'Vue matérialisée permettant de faire des autocomplete construite à partir d''une requete sur tout taxref.';

-- Creation des index de la table vm_taxref_list_forautocomplete
CREATE unique index i_vm_taxref_list_forautocomplete_gid
  ON taxonomie.vm_taxref_list_forautocomplete (gid);

CREATE INDEX i_vm_taxref_list_forautocomplete_cd_nom
  ON taxonomie.vm_taxref_list_forautocomplete (cd_nom ASC NULLS LAST);

CREATE INDEX i_vm_taxref_list_forautocomplete_search_name
  ON taxonomie.vm_taxref_list_forautocomplete (search_name ASC NULLS LAST);
CREATE INDEX i_tri_vm_taxref_list_forautocomplete_search_name
  ON taxonomie.vm_taxref_list_forautocomplete
  USING gist
  (search_name  gist_trgm_ops);

-- suppression des triggers qui alimentaient cette table
 DROP TRIGGER trg_refresh_mv_taxref_list_forautocomplete ON taxonomie.cor_nom_liste;
 DROP TRIGGER trg_refresh_nomfrancais_mv_taxref_list_forautocomplete ON taxonomie.bib_noms;

-- et des fonctions triggers
DROP FUNCTION taxonomie.trg_fct_refresh_nomfrancais_mv_taxref_list_forautocomplete();
DROP FUNCTION taxonomie.trg_fct_refresh_mv_taxref_list_forautocomplete();


-- Modification des fonction find_all_taxons_children :
---     utilisation de cd_sup au lieu de cd_taxsup pour prendre
--        en compte des rangs intermediares
CREATE OR REPLACE FUNCTION taxonomie.find_all_taxons_children(id integer)
  RETURNS TABLE (cd_nom int, cd_ref int) AS
$BODY$
 --Param : cd_nom ou cd_ref d'un taxon quelque soit son rang
 --Retourne le cd_nom de tous les taxons enfants sous forme d'un jeu de données utilisable comme une table
 --Usage SELECT taxonomie.find_all_taxons_children(197047);
 --ou SELECT * FROM atlas.vm_taxons WHERE cd_ref IN(SELECT * FROM taxonomie.find_all_taxons_children(197047))
  BEGIN
      RETURN QUERY
      WITH RECURSIVE descendants AS (
        SELECT tx1.cd_nom, tx1.cd_ref FROM taxonomie.taxref tx1 WHERE tx1.cd_sup = id
      UNION ALL
      SELECT tx2.cd_nom, tx2.cd_ref FROM descendants d JOIN taxonomie.taxref tx2 ON tx2.cd_sup = d.cd_nom
      )
      SELECT * FROM descendants;

  END;
$BODY$
  LANGUAGE plpgsql IMMUTABLE;



CREATE OR REPLACE FUNCTION taxonomie.find_all_taxons_children(IN ids integer[])
  RETURNS TABLE(cd_nom integer, cd_ref integer) AS
$BODY$
 --Param : cd_nom ou cd_ref d'un taxon quelque soit son rang
 --Retourne le cd_nom de tous les taxons enfants sous forme d'un jeu de données utilisable comme une table
 --Usage SELECT taxonomie.find_all_taxons_children(197047);
 --ou SELECT * FROM atlas.vm_taxons WHERE cd_ref IN(SELECT * FROM taxonomie.find_all_taxons_children(197047))
  BEGIN
      RETURN QUERY
      WITH RECURSIVE descendants AS (
        SELECT tx1.cd_nom, tx1.cd_ref FROM taxonomie.taxref tx1 WHERE tx1.cd_sup = ANY(ids)
      UNION ALL
      SELECT tx2.cd_nom, tx2.cd_ref FROM descendants d JOIN taxonomie.taxref tx2 ON tx2.cd_sup = d.cd_nom
      )
      SELECT * FROM descendants;

  END;
$BODY$
  LANGUAGE plpgsql IMMUTABLE;
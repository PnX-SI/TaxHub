
-- Creation d'une vue matérialis&ée de tous les noms de Taxref mis en forme pour la recherche de taxons
--    avec le nom vernaculaire
DROP MATERIALIZED VIEW IF EXISTS taxonomie.vm_taxref_list_forautocomplete;

CREATE MATERIALIZED VIEW taxonomie.vm_taxref_list_forautocomplete AS
SELECT
  row_number() OVER() as gid,
  t.cd_nom,
  t.cd_ref,
  t.search_name,
  t.nom_valide,
  t.lb_nom,
  t.nom_vern,
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
    t_1.nom_vern,
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
    t_1.nom_vern,
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

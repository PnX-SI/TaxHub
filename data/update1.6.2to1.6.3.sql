DROP TABLE IF EXISTS taxonomie.vm_taxref_list_forautocomplete;
CREATE TABLE taxonomie.vm_taxref_list_forautocomplete AS
SELECT t.cd_nom,
  t.cd_ref,
  t.search_name,
  t.nom_valide,
  t.lb_nom,
  t.regne,
  t.group2_inpn,
  l.id_liste
FROM (
  SELECT t_1.cd_nom,
        t_1.cd_ref,
        concat(t_1.lb_nom, ' =  <i> ', t_1.nom_valide, '</i>', ' - [', t_1.id_rang, ' - ', t_1.cd_nom , ']') AS search_name,
        t_1.nom_valide,
        t_1.lb_nom,
        t_1.regne,
        t_1.group2_inpn
  FROM taxonomie.taxref t_1
  UNION
  SELECT t_1.cd_nom,
        t_1.cd_ref,
        concat(n.nom_francais, ' =  <i> ', t_1.nom_valide, '</i>', ' - [', t_1.id_rang, ' - ', t_1.cd_nom , ']' ) AS search_name,
        t_1.nom_valide,
        t_1.lb_nom,
        t_1.regne,
        t_1.group2_inpn
  FROM taxonomie.taxref t_1
  JOIN taxonomie.bib_noms n
  ON t_1.cd_nom = n.cd_nom
  WHERE n.nom_francais IS NOT NULL AND t_1.cd_nom = t_1.cd_ref
) t
JOIN taxonomie.v_taxref_all_listes l ON t.cd_nom = l.cd_nom;
COMMENT ON TABLE taxonomie.vm_taxref_list_forautocomplete
     IS 'Table construite à partir d''une requete sur la base et mise à jour via le trigger trg_refresh_mv_taxref_list_forautocomplete de la table cor_nom_liste';



CREATE OR REPLACE FUNCTION taxonomie.trg_fct_refresh_attributesviews_per_kingdom()
  RETURNS trigger AS
$BODY$
DECLARE
   sregne text;
   lregne text;
BEGIN
    RAISE NOTICE '%', TG_OP;
    IF TG_OP = 'DELETE' OR TG_OP = 'TRUNCATE' THEN
        sregne := OLD.regne;
    ELSE
        sregne := NEW.regne;
    END IF;

    IF sregne IS NULL THEN
        FOR lregne IN
            SELECT DISTINCT regne
            FROM taxonomie.taxref t
            JOIN taxonomie.bib_noms n
            ON t.cd_nom = n.cd_nom
            WHERE t.regne IS NOT NULL
        LOOP
            PERFORM taxonomie.fct_build_bibtaxon_attributs_view(lregne);
        END LOOP;
    ELSE
        PERFORM taxonomie.fct_build_bibtaxon_attributs_view(sregne);
    END IF;
    
    IF TG_OP = 'DELETE' OR TG_OP = 'TRUNCATE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
    
END
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

  -- Suppression d'un index inutile sur une clé primaire
DROP INDEX IF EXISTS taxonomie.i_taxref_cd_nom;

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
        SELECT tx1.cd_nom, tx1.cd_ref FROM taxonomie.taxref tx1 WHERE tx1.cd_taxsup = id
      UNION ALL
      SELECT tx2.cd_nom, tx2.cd_ref FROM descendants d JOIN taxonomie.taxref tx2 ON tx2.cd_taxsup = d.cd_nom
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
        SELECT tx1.cd_nom, tx1.cd_ref FROM taxonomie.taxref tx1 WHERE tx1.cd_taxsup = ANY(ids)
      UNION ALL
      SELECT tx2.cd_nom, tx2.cd_ref FROM descendants d JOIN taxonomie.taxref tx2 ON tx2.cd_taxsup = d.cd_nom
      )
      SELECT * FROM descendants;

  END;
$BODY$
  LANGUAGE plpgsql IMMUTABLE;
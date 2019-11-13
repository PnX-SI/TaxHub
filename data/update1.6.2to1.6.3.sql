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
                                                              
--Fonction pour lister les taxons parents
CREATE OR REPLACE FUNCTION taxonomie.find_all_taxons_parents(id integer)
 RETURNS SETOF integer
 LANGUAGE plpgsql
 IMMUTABLE
AS $function$
 --Param : cd_nom d'un taxon quelque soit son rang
 --Retourne le cd_nom de tous les taxons parents sous forme d'un jeu de données utilisable comme une table
 --Usage SELECT atlas.find_all_taxons_parents(197047);
  DECLARE
    inf RECORD;
  BEGIN
  FOR inf IN
	WITH RECURSIVE parents AS (
		SELECT tx1.cd_nom,tx1.cd_sup FROM taxonomie.taxref tx1 WHERE tx1.cd_nom = id
		UNION ALL 
		SELECT tx2.cd_nom,tx2.cd_sup
			FROM parents p
			JOIN taxonomie.taxref tx2 ON tx2.cd_nom = p.cd_sup
	)
	SELECT parents.cd_nom FROM parents
	JOIN taxonomie.taxref taxref ON taxref.cd_nom = parents.cd_nom
	WHERE parents.cd_nom!=id
  LOOP
      RETURN NEXT inf.cd_nom;
  END LOOP;
  END;
$function$
;

--Variante de la fonction précédente qui retourne une table incluant le rang des taxons parents
CREATE OR REPLACE FUNCTION taxonomie.find_all_taxons_parents_t(id integer)
 RETURNS TABLE(cd_nom integer, id_rang varchar)
 LANGUAGE plpgsql
 IMMUTABLE
AS $function$
 --Param : cd_nom d'un taxon quelque soit son rang
 --Retourne une table avec le cd_nom de tout les taxons parents et leur id_rang.
 --Retourne le cd_nom de tous les taxons parents sous forme d'un jeu de données utilisable comme une table. Les cd_nom sont ordonnées du plus bas vers le plus haut (Dumm)
 --Usage SELECT * FROM taxonomie.find_all_taxons_parents_t(457346);
  DECLARE
    inf RECORD;
  BEGIN
  RETURN QUERY
	WITH RECURSIVE parents AS (
		SELECT tx1.cd_nom,tx1.cd_sup, tx1.id_rang, 0 AS nr FROM taxonomie.taxref tx1 WHERE tx1.cd_nom = id
		UNION ALL 
		SELECT tx2.cd_nom,tx2.cd_sup, tx2.id_rang, nr + 1
			FROM parents p
			JOIN taxonomie.taxref tx2 ON tx2.cd_nom = p.cd_sup
	)
	SELECT parents.cd_nom, parents.id_rang FROM parents
	JOIN taxonomie.taxref taxref ON taxref.cd_nom = parents.cd_nom
	ORDER BY parents.nr;
  END;
$function$
;									      
							      
--Fonction qui retourne le cd_nom de l'ancêtre commune le plus proche
CREATE OR REPLACE FUNCTION taxonomie.find_lowest_common_ancestor(ida integer,idb integer)
 RETURNS integer
 LANGUAGE plpgsql
 IMMUTABLE
AS $function$
  --Param : cd_nom de 2 taxons
  --Retourne le cd_nom de l'ancêtre commun le plus proche
  DECLARE
  out_cd_nom integer;
BEGIN
	SELECT INTO out_cd_nom cd_nom FROM taxonomie.taxref taxref
	JOIN taxonomie.bib_taxref_rangs rg ON rg.id_rang=taxref.id_rang
	WHERE cd_nom IN 
	(SELECT taxonomie.find_all_taxons_parents(ida) INTERSECT SELECT taxonomie.find_all_taxons_parents(idb))
	ORDER BY rg.tri_rang DESC LIMIT 1;
	RETURN out_cd_nom;
END;
$function$
;                                                              

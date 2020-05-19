-------------
--FUNCTIONS--
-------------

-- Création de la fonction taxonomie.match_binomial_taxref

CREATE OR REPLACE FUNCTION taxonomie.match_binomial_taxref(my_taxa_name character varying)
RETURNS integer
LANGUAGE plpgsql
IMMUTABLE
AS $function$
--fonction permettant de rattacher un nom latin aux cd_nom du taxref sur le principe suivant :
-- - Si un seul cd_nom existe pour ce nom latin, la fonction retourne le cd_nom
-- - Si plusieurs cd_noms existent pour ce nom latin, mais qu'ils appartiennent tous à un unique cd_ref, la fonction renvoie le cd_ref (= cd_nom valide)
-- - Si plusieurs cd_noms existent pour ce nom latin et qu'ils appartiennent à plusieurs cd_ref, la fonction renvoie NULL : le rattachement devra être fait manuellement
DECLARE 
	matching_cd integer;
BEGIN
	IF (SELECT count(DISTINCT cd_nom) FROM taxonomie.taxref WHERE lb_nom ILIKE my_taxa_name OR nom_valide ILIKE my_taxa_name)=1 THEN matching_cd:= cd_nom FROM taxonomie.taxref WHERE lb_nom ILIKE my_taxa_name OR nom_valide ILIKE my_taxa_name ;
	ELSIF (SELECT count(DISTINCT cd_ref) FROM taxonomie.taxref WHERE lb_nom ILIKE my_taxa_name OR nom_valide ILIKE my_taxa_name)=1 THEN matching_cd:= DISTINCT(cd_ref) FROM taxonomie.taxref WHERE lb_nom ILIKE my_taxa_name OR nom_valide ILIKE my_taxa_name ;
	ELSE matching_cd:= NULL;
	END IF; 
	RETURN matching_cd;
END ;
$function$
;

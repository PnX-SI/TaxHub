
---- #################################################################################
---- #################################################################################
----		Cd nom disparus
---- #################################################################################
---- #################################################################################

-- Ajout temporaire de champs permettant d'identifier les changements de cd_nom
ALTER TABLE taxonomie.bib_noms ADD commentaire_disparition Varchar(500);
ALTER TABLE taxonomie.bib_noms ADD cd_nom_remplacement int;
ALTER TABLE taxonomie.bib_noms ADD deleted boolean DEFAULT (FALSE);
ALTER TABLE taxonomie.bib_noms ADD tmp_import boolean;

--UPDATE taxonomie.bib_noms SET deleted = FALSE;

--suppression de la clé étrangère vers taxref car certains cd_nom de remplacement pourraient ne pas avoir de correspondance dans l'ancien taxref.
-- Attention cette FK ne sera rétablie qu'en fin de migration.
ALTER TABLE taxonomie.bib_noms DROP CONSTRAINT fk_bib_nom_taxref;

--- CAS 1 - cd_nom de remplacement à utiliser.
UPDATE taxonomie.bib_noms n  SET deleted = true ,
	commentaire_disparition = raison_suppression ||  COALESCE(' nouveau cd_nom :' || a.cd_nom_remplacement, ''),
	cd_nom_remplacement =  a.cd_nom_remplacement
FROM (
	SELECT d.*
	FROM taxonomie.bib_noms n
	JOIN taxonomie.cdnom_disparu d
	ON n.cd_nom = d.cd_nom
) a
WHERE n.cd_nom = a.cd_nom;


------------- Cas avec cd_nom de remplacement
-- Ajout du cd_nom de remplacement quand il n'existait pas dans bib_noms
INSERT INTO taxonomie.bib_noms(cd_nom, cd_ref, nom_francais, tmp_import)
SELECT d.cd_nom_remplacement, n.cd_ref, n.nom_francais, true
FROM taxonomie.bib_noms n
JOIN taxonomie.cdnom_disparu d ON n.cd_nom = d.cd_nom
WHERE NOT n.cd_nom_remplacement IS NULL
ON CONFLICT DO NOTHING;

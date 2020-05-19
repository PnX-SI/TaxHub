
---- #################################################################################
---- #################################################################################
----		Cd nom disparus
---- #################################################################################
---- #################################################################################

-- Ajout temporaire de champs permettant d'identifier les changements de cd_nom
ALTER TABLE taxonomie.bib_noms ADD commentaire_disparition Varchar(500);
ALTER TABLE taxonomie.bib_noms ADD deleted boolean DEFAULT (FALSE);
UPDATE taxonomie.bib_noms SET deleted = FALSE;


--- CAS 1 - cd_nom de remplacement à utiliser.
UPDATE taxonomie.bib_noms n  SET deleted = true , commentaire_disparition = raison_suppression || ' nouveau cd_nom :' || cd_nom_remplacement
FROM (
	SELECT d.*
	FROM taxonomie.bib_noms n
	JOIN taxonomie.cdnom_disparu d
	ON n.cd_nom = d.cd_nom
	--AND cd_nom_remplacement IN (SELECT DISTINCT cd_nom FROM taxonomie.bib_noms)
)a
WHERE n.cd_nom = a.cd_nom;



-- Ajout du cd_nom de remplacement quand il n'existait pas dans bib_noms
INSERT INTO taxonomie.bib_noms(cd_nom, cd_ref, nom_francais)
SELECT cd_nom_remplacement, n.cd_ref, n.nom_francais
FROM taxonomie.bib_noms n
JOIN taxonomie.cdnom_disparu d
ON n.cd_nom = d.cd_nom
AND NOT cd_nom_remplacement IN (SELECT DISTINCT cd_nom FROM taxonomie.bib_noms);

------------- AUTRES CAS à GERER

UPDATE taxonomie.bib_noms n  SET deleted = true , commentaire_disparition = raison_suppression
FROM (
	SELECT d.*
	FROM taxonomie.bib_noms n
	JOIN taxonomie.cdnom_disparu d
	ON n.cd_nom = d.cd_nom
)a
WHERE n.cd_nom = a.cd_nom AND not deleted = true;


-- ###############   Répercussion dans bib_listes
--- !!!!!!!!! Ne doit pas obligatoirement etre lancer dans ce script mais doit quand même l'être un jour

-- Remplacement des anciens cd_nom par leurs remplaçants dans cor_nom_liste
-- ALTER TABLE taxonomie.cor_nom_liste DROP CONSTRAINT cor_nom_liste_pkey;
-- ALTER TABLE  taxonomie.cor_nom_liste ADD tmp_id serial;

-- UPDATE taxonomie.cor_nom_liste l SET id_nom = repl_nom
-- FROM (
-- 	SELECT id_liste, l.id_nom, cd_nom_remplacement, n.cd_nom, repl.id_nom as repl_nom
-- 	FROM taxonomie.cor_nom_liste l
-- 	JOIN (
-- 		SELECT n.id_nom, d.*
-- 		FROM taxonomie.bib_noms n
-- 		JOIN taxonomie.cdnom_disparu d
-- 		ON n.cd_nom = d.cd_nom
-- 	) n
-- 	ON n.id_nom = l.id_nom
-- 	JOIN taxonomie.bib_noms repl
-- 	ON repl.cd_nom = cd_nom_remplacement
-- ) a
-- WHERE a.id_liste = l.id_liste AND a.id_nom = l.id_nom;


-- --- Suppression des doublons
-- DELETE FROM taxonomie.cor_nom_liste
-- WHERE tmp_id IN (
-- 	SELECT tmp_id FROM taxonomie.cor_nom_liste l
-- 	JOIN  (
-- 		SELECT  id_liste, id_nom, max(tmp_id)
-- 		FROM taxonomie.cor_nom_liste
-- 		GROUP BY id_liste, id_nom
-- 		HAVING count(*) >1
-- 	)a
-- 	ON l.id_liste = a.id_liste AND l.id_nom = a.id_nom
-- 		AND NOT tmp_id = max
-- );

-- -- supression dans les cas ou il n'y a pas de taxons de remplacements
-- DELETE FROM taxonomie.cor_nom_liste
-- WHERE id_nom IN (SELECT id_nom FROM taxonomie.bib_noms WHERE deleted=true);

-- -- Restauration de la clé primaire de cor_nom_liste
-- ALTER TABLE taxonomie.cor_nom_liste
--   ADD CONSTRAINT cor_nom_liste_pkey PRIMARY KEY(id_nom, id_liste);

-- -- Suppression de la colonne temporaire cor_nom_liste
-- ALTER TABLE  taxonomie.cor_nom_liste DROP COLUMN tmp_id ;


-- Export des données supprimées
-- Attention l'utilisateur qui exécute ce script doit être superuser
COPY (
	SELECT *
	FROM taxonomie.bib_noms
	WHERE  deleted = true
) TO '/tmp/liste_cd_nom_disparus_bib_noms.csv'
DELIMITER ';' CSV HEADER;


------##################################################################################
------   EXPORT DE DONNEES A REALISER
------  indique les changements qui vont être réalisé et les potentiels conflits qu'ils faur résoudre en amont
------##################################################################################
-- Décompte des changements
COPY (
	SELECT DISTINCT cas, count(*)
	FROM tmp_taxref_changes.comp_grap c
	GROUP BY  cas
	ORDER BY cas
) TO '/tmp/nb_changements.csv'
DELIMITER ';' CSV HEADER;

---------------------------
-- Liste des changements avec potentiels conflicts et perte de données attributaires
COPY (
	SELECT *
	FROM tmp_taxref_changes.comp_grap
	WHERE NOT action ='no changes'
) TO '/tmp/liste_changements.csv'
DELIMITER ';' CSV HEADER;

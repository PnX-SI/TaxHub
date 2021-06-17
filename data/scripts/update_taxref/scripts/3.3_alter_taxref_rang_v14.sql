-- MISE A JOUR DES RANGS


INSERT INTO taxonomie.bib_taxref_rangs (id_rang, nom_rang, nom_rang_en, tri_rang)
SELECT rang, detail_fr, detail_en, level
FROM taxonomie.import_taxref_rangs
ON CONFLICT (id_rang)
DO
   UPDATE SET nom_rang = EXCLUDED.nom_rang,  tri_rang = EXCLUDED.tri_rang, nom_rang_en = EXCLUDED.nom_rang_en;

DELETE FROM taxonomie.bib_taxref_rangs b
WHERE b.id_rang IN (
	SELECT b.id_rang
	FROM taxonomie.bib_taxref_rangs b
	LEFT JOIN taxonomie.import_taxref_rangs tr
	ON tr.rang = b.id_rang
	WHERE tr.rang IS NULL
);
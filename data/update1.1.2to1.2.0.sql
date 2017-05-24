-- Nettoyage de la table d'import temporaire de taxref.
TRUNCATE TABLE taxonomie.import_taxref;

-- Convertir l'id_liste de bib_listes de serial vers integer.
ALTER TABLE taxonomie.bib_listes ALTER COLUMN id_liste DROP DEFAULT;
DROP SEQUENCE taxonomie.bib_listes_id_liste_seq;

--Rendre le picto de bib_listes obligatoire avec une valeur par défaut.
ALTER TABLE taxonomie.bib_listes ALTER COLUMN picto SET NOT NULL;
ALTER TABLE taxonomie.bib_listes ALTER COLUMN picto SET DEFAULT 'images/pictos/nopicto.gif';
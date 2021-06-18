-- Suppression des objets temporaires lié à la migration
DROP SCHEMA tmp_taxref_changes CASCADE;
TRUNCATE TABLE taxonomie.import_taxref;

DROP TABLE IF EXISTS taxonomie.import_protection_especes;

DROP FUNCTION  IF EXISTS public.deps_test_fk_dependencies_cd_nom();

DROP TABLE IF EXISTS taxonomie.dps_fk_cd_nom;

DROP TABLE IF EXISTS taxonomie.import_taxref_rangs;

DROP TABLE IF EXISTS taxonomie.cdnom_disparu;

-- Restauration de la structure originnele de la table bib_noms
ALTER TABLE taxonomie.bib_noms DROP IF EXISTS deleted CASCADE;
ALTER TABLE taxonomie.bib_noms DROP IF EXISTS commentaire_disparition CASCADE;

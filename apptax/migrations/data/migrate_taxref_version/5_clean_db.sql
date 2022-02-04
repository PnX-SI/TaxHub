-- Suppression des objets temporaires lié à la migration
DROP SCHEMA tmp_taxref_changes CASCADE;
TRUNCATE TABLE taxonomie.import_taxref;

DROP TABLE IF EXISTS taxonomie.import_protection_especes;

DROP FUNCTION  IF EXISTS public.deps_test_fk_dependencies_cd_nom();

DROP TABLE IF EXISTS taxonomie.dps_fk_cd_nom;

DROP TABLE IF EXISTS taxonomie.import_taxref_rangs;

DROP TABLE IF EXISTS taxonomie.cdnom_disparu;

DROP TABLE IF EXISTS taxonomie.tmp_bib_noms_copy;

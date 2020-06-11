-- Suppression des objets temporaires lié à la migration
DROP SCHEMA tmp_taxref_changes CASCADE;
TRUNCATE TABLE taxonomie.import_taxref;

DROP TABLE taxonomie.import_protection_especes;

DROP FUNCTION public.deps_test_fk_dependencies_cd_nom();
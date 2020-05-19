-- rétablir la contrainte de clé étrangère entre bib_noms et le nouveau taxref
ALTER TABLE taxonomie.bib_noms ADD CONSTRAINT fk_bib_nom_taxref FOREIGN KEY (cd_nom) REFERENCES taxonomie.taxref(cd_nom);

DROP SCHEMA tmp_taxref_changes CASCADE;
TRUNCATE TABLE taxonomie.import_taxref;

DROP TABLE taxonomie.import_protection_especes;

DROP FUNCTION public.deps_test_fk_dependencies_cd_nom();
DROP TABLE taxonomie.dps_fk_cd_nom;
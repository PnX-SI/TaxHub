-- Passage des chaines vides à NULL dans taxref
UPDATE taxonomie.taxref SET id_statut = NULL WHERE id_statut = '';
UPDATE taxonomie.taxref SET id_rang = NULL WHERE id_rang = '';
UPDATE taxonomie.taxref SET regne = NULL WHERE regne = '';
UPDATE taxonomie.taxref SET phylum = NULL WHERE phylum = '';
UPDATE taxonomie.taxref SET classe = NULL WHERE classe = '';
UPDATE taxonomie.taxref SET ordre = NULL WHERE ordre = '';
UPDATE taxonomie.taxref SET famille = NULL WHERE famille = '';
UPDATE taxonomie.taxref SET sous_famille = NULL WHERE sous_famille = '';
UPDATE taxonomie.taxref SET tribu = NULL WHERE tribu = '';
UPDATE taxonomie.taxref SET lb_nom = NULL WHERE lb_nom = '';
UPDATE taxonomie.taxref SET lb_auteur = NULL WHERE lb_auteur = '';
UPDATE taxonomie.taxref SET nom_complet = NULL WHERE nom_complet = '';
UPDATE taxonomie.taxref SET nom_complet_html = NULL WHERE nom_complet_html = '';
UPDATE taxonomie.taxref SET nom_valide = NULL WHERE nom_valide = '';
UPDATE taxonomie.taxref SET nom_vern = NULL WHERE nom_vern = '';
UPDATE taxonomie.taxref SET nom_vern_eng = NULL WHERE nom_vern_eng = '';
UPDATE taxonomie.taxref SET group1_inpn = NULL WHERE group1_inpn = '';
UPDATE taxonomie.taxref SET group2_inpn = NULL WHERE group2_inpn = '';
UPDATE taxonomie.taxref SET url = NULL WHERE url = '';
UPDATE taxonomie.taxref SET group3_inpn = NULL WHERE group3_inpn = '';

-- Suppression des objets temporaires lié à la migration
DROP SCHEMA tmp_taxref_changes CASCADE;
TRUNCATE TABLE taxonomie.import_taxref;

DROP TABLE IF EXISTS taxonomie.import_protection_especes;

DROP FUNCTION  IF EXISTS public.deps_test_fk_dependencies_cd_nom();

DROP TABLE IF EXISTS taxonomie.dps_fk_cd_nom;

DROP TABLE IF EXISTS taxonomie.import_taxref_rangs;

DROP TABLE IF EXISTS taxonomie.cdnom_disparu;


DROP TABLE IF EXISTS taxonomie.import_taxref_rangs;

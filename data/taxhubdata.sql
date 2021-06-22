SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = taxonomie, pg_catalog, public;

-- Insertion d'un thème d'exemple permettant de gérer les attributs et informations taxonomiques spécifiques à un territoire
INSERT INTO bib_themes (id_theme, nom_theme, desc_theme, ordre, id_droit)
    VALUES (1, 'Mon territoire', 'Informations relatives à mon territoire', 1, 4);
SELECT setval('taxonomie.bib_themes_id_theme_seq', (SELECT max(id_theme)+1 FROM taxonomie.bib_themes), true);

-- Insertion d'une liste permettant de définir les noms pouvant être saisis dans le module Occtax
INSERT INTO bib_listes (id_liste, code_liste,  nom_liste,desc_liste,picto)
    VALUES (100, '100', 'Saisie Occtax','Liste des noms dont la saisie est proposée dans le module Occtax','images/pictos/nopicto.gif');

-- Insertion des types de média associables aux taxons
INSERT INTO bib_types_media (id_type, nom_type_media, desc_type_media) VALUES (1, 'Photo_principale', 'Photo principale du taxon à utiliser pour les vignettes par exemple');
INSERT INTO bib_types_media (id_type, nom_type_media, desc_type_media) VALUES (2, 'Photo', 'Autres photos du taxon');
INSERT INTO bib_types_media (id_type, nom_type_media, desc_type_media) VALUES (3, 'Page web', 'URL d''une page web');
INSERT INTO bib_types_media (id_type, nom_type_media, desc_type_media) VALUES (4, 'PDF', 'Document de type PDF');
INSERT INTO bib_types_media (id_type, nom_type_media, desc_type_media) VALUES (5, 'Audio', 'Fichier audio MP3');
INSERT INTO bib_types_media (id_type, nom_type_media, desc_type_media) VALUES (6, 'Video (fichier)', 'Fichier video hébergé');
INSERT INTO bib_types_media (id_type, nom_type_media, desc_type_media) VALUES (7, 'Video Youtube', 'ID d''une video hébergée sur Youtube');
INSERT INTO bib_types_media (id_type, nom_type_media, desc_type_media) VALUES (8, 'Video Dailymotion', 'ID d''une video hébergée sur Dailymotion');
INSERT INTO bib_types_media (id_type, nom_type_media, desc_type_media) VALUES (9, 'Video Vimeo', 'ID d''une video hébergée sur Vimeo');

-- Creation d'une vue matérialis&ée de tous les noms de Taxref mis en forme pour la recherche de taxons
DROP MATERIALIZED VIEW IF EXISTS taxonomie.vm_taxref_list_forautocomplete;

CREATE MATERIALIZED VIEW taxonomie.vm_taxref_list_forautocomplete AS
SELECT
  row_number() OVER() as gid,
  t.cd_nom,
  t.cd_ref,
  t.search_name,
  t.nom_valide,
  t.lb_nom,
  t.nom_vern,
  t.regne,
  t.group2_inpn
FROM (
  -- PARTIE NOM SCIENTIFIQUE : ici on prend TOUS les synonymes.
  SELECT
    t_1.cd_nom,
    t_1.cd_ref,
    concat(t_1.lb_nom, ' =  <i> ', t_1.nom_valide, '</i>', ' - [', t_1.id_rang, ' - ', t_1.cd_nom , ']') AS search_name,
    t_1.nom_valide,
    t_1.lb_nom,
    t_1.nom_vern,
    t_1.regne,
    t_1.group2_inpn
  FROM taxonomie.taxref t_1
  UNION
  -- PARTIE NOM FRANCAIS : ici on prend une seule fois (DISTINCT) dans Taxref tous les taxons de références
  -- On ne prend pas les taxons qui n'ont pas de nom vern dans taxref,
  -- donc si un taxon n'a pas de nom vern dans Taxref, il n'est accessible que par son nom scientifique.
  SELECT DISTINCT
    t_1.cd_nom,
    t_1.cd_ref,
    concat(split_part(t_1.nom_vern, ',', 1), ' =  <i> ', t_1.nom_valide, '</i>', ' - [', t_1.id_rang, ' - ', t_1.cd_ref , ']' ) AS search_name,
    t_1.nom_valide,
    t_1.lb_nom,
    t_1.nom_vern,
    t_1.regne,
    t_1.group2_inpn
  FROM taxonomie.taxref t_1
  WHERE t_1.nom_vern IS NOT null and t_1.cd_nom = t_1.cd_ref
) t;
COMMENT ON MATERIALIZED VIEW taxonomie.vm_taxref_list_forautocomplete
    IS 'Vue matérialisée permettant de faire des autocomplete construite à partir d''une requete sur tout taxref.';

-- Creation des index de la table vm_taxref_list_forautocomplete
CREATE unique index i_vm_taxref_list_forautocomplete_gid
  ON taxonomie.vm_taxref_list_forautocomplete (gid);
CREATE INDEX i_vm_taxref_list_forautocomplete_cd_nom
  ON taxonomie.vm_taxref_list_forautocomplete (cd_nom ASC NULLS LAST);
CREATE INDEX i_vm_taxref_list_forautocomplete_search_name
  ON taxonomie.vm_taxref_list_forautocomplete (search_name ASC NULLS LAST);
CREATE INDEX i_tri_vm_taxref_list_forautocomplete_search_name
  ON taxonomie.vm_taxref_list_forautocomplete
  USING gist
  (search_name  gist_trgm_ops);

-- ##############################################"""""
--------- BDC statuts
-- ##############################################"""""


--- ### populate
-- bdc_statut_text
ALTER  TABLE taxonomie.bdc_statut_text ADD id int[];

INSERT INTO taxonomie.bdc_statut_text
(cd_type_statut, cd_sig, cd_doc, niveau_admin, cd_iso3166_1, cd_iso3166_2, lb_adm_tr, full_citation, doc_url,  id)
SELECT DISTINCT  cd_type_statut,
	-- code_statut , label_statut ,
	cd_sig , cd_doc , niveau_admin , cd_iso3166_1 , cd_iso3166_2 , lb_adm_tr,
	full_citation, doc_url ,
	array_agg(DISTINCT tbs.id) id
FROM taxonomie.bdc_statut tbs
GROUP BY  cd_type_statut,
	-- code_statut , label_statut ,
	cd_sig , cd_doc , niveau_admin , cd_iso3166_1 , cd_iso3166_2 , lb_adm_tr,
	full_citation, doc_url ;

UPDATE taxonomie.bdc_statut_text tbst  SET doc_url = NULL
WHERE doc_url ='';

-- bdc_statut_values
ALTER  TABLE taxonomie.bdc_statut_values ADD id int[];
ALTER  TABLE taxonomie.bdc_statut_values ADD ids_text int[];

INSERT INTO taxonomie.bdc_statut_values (code_statut, label_statut, ids_text, id)
SELECT DISTINCT tbs.code_statut , label_statut,  array_agg(DISTINCT t.id_text) ids_text,  array_agg(DISTINCT tbs.id) id
FROM taxonomie.bdc_statut tbs
JOIN taxonomie.bdc_statut_text t
ON t.cd_type_statut = tbs.cd_type_statut
	AND (t.cd_sig = tbs.cd_sig OR  t.cd_sig IS NULL)
	AND t.full_citation = tbs.full_citation
GROUP BY  tbs.code_statut , label_statut;

-- bdc_statut_cor_text_values
INSERT INTO taxonomie.bdc_statut_cor_text_values (id_value, id_text)
SELECT id_value, unnest(ids_text) AS id_text
FROM taxonomie.bdc_statut_values ;

-- Mise en correspondances des textes, values et taxon
ALTER TABLE taxonomie.bdc_statut DROP IF EXISTS id_text;
ALTER TABLE taxonomie.bdc_statut ADD id_text int;

UPDATE taxonomie.bdc_statut s SET  id_text = a.id_text
FROM (
	SELECT unnest(id) AS id, id_text
	FROM  taxonomie.bdc_statut_text
)a
WHERE a.id = s.id;


ALTER TABLE taxonomie.bdc_statut DROP IF EXISTS id_value ;
ALTER TABLE taxonomie.bdc_statut ADD id_value int;
UPDATE taxonomie.bdc_statut s SET  id_value = a.id_value
FROM (
	SELECT unnest(id) AS id, id_value
	FROM  taxonomie.bdc_statut_values
)a
WHERE a.id = s.id;


ALTER TABLE taxonomie.bdc_statut DROP IF EXISTS id_value_text ;
ALTER TABLE taxonomie.bdc_statut ADD id_value_text int;
UPDATE taxonomie.bdc_statut s SET  id_value_text = c.id_value_text
FROM taxonomie.bdc_statut_cor_text_values  c
WHERE c.id_text = s.id_text AND s.id_value = c.id_value;

-- bdc_statut_taxons
INSERT INTO taxonomie.bdc_statut_taxons (id, id_value_text, cd_nom, cd_ref, rq_statut)
SELECT id, id_value_text, t.cd_nom, t.cd_ref, rq_statut
FROM  taxonomie.bdc_statut s
JOIN taxonomie.taxref t
ON s.cd_nom = t.cd_nom; -- Jointure sur taxref car 3 cd_nom n'existent pas : 847285, 973500, 851332


--- ### populate
ALTER  TABLE taxonomie.bdc_statut_text DROP id;

ALTER  TABLE taxonomie.bdc_statut_values DROP id;
ALTER  TABLE taxonomie.bdc_statut_values DROP ids_text;

ALTER TABLE taxonomie.bdc_statut DROP IF EXISTS id_value_text ;
ALTER TABLE taxonomie.bdc_statut DROP IF EXISTS id_value ;
ALTER TABLE taxonomie.bdc_statut DROP IF EXISTS id_text;

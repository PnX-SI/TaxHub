-- Peuplement des tables de la BDC Statut en version 1.8.1
-- A partir de la version 1.9.0, les évolutions de la BDD sont gérées dans des migrations Alembic

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = taxonomie, pg_catalog, public;

-- ##############################################"""""
--------- BDC statuts
-- ##############################################"""""

DELETE FROM taxonomie.bdc_statut_taxons;
DELETE FROM taxonomie.bdc_statut_cor_text_values;
DELETE FROM taxonomie.bdc_statut_text;
DELETE FROM taxonomie.bdc_statut_values;

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

CREATE INDEX IF NOT EXISTS bdc_statut_code_statut_idx ON taxonomie.bdc_statut USING btree (code_statut);
CREATE INDEX IF NOT EXISTS bdc_statut_label_statut_idx ON taxonomie.bdc_statut USING btree (label_statut);

INSERT INTO taxonomie.bdc_statut_values (code_statut, label_statut, ids_text, id)
SELECT DISTINCT tbs.code_statut , tbs.label_statut,  array_agg(DISTINCT t.id_text) ids_text,  array_agg(DISTINCT tbs.id) id
FROM taxonomie.bdc_statut tbs
JOIN taxonomie.bdc_statut_text t
ON t.cd_type_statut = tbs.cd_type_statut
	AND (t.cd_sig = tbs.cd_sig OR  t.cd_sig IS NULL)
	AND t.full_citation = tbs.full_citation
GROUP BY  tbs.code_statut , tbs.label_statut;

-- bdc_statut_cor_text_values
INSERT INTO taxonomie.bdc_statut_cor_text_values (id_value, id_text)
SELECT id_value, unnest(ids_text) AS id_text
FROM taxonomie.bdc_statut_values ;

-- Mise en correspondances des textes, values et taxon
ALTER TABLE taxonomie.bdc_statut ADD id_text int;

UPDATE taxonomie.bdc_statut s SET  id_text = a.id_text
FROM (
	SELECT unnest(id) AS id, id_text
	FROM  taxonomie.bdc_statut_text
)a
WHERE a.id = s.id;


ALTER TABLE taxonomie.bdc_statut ADD id_value int;
UPDATE taxonomie.bdc_statut s SET  id_value = a.id_value
FROM (
	SELECT unnest(id) AS id, id_value
	FROM  taxonomie.bdc_statut_values
)a
WHERE a.id = s.id;


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

ALTER TABLE taxonomie.bdc_statut DROP id_value_text ;
ALTER TABLE taxonomie.bdc_statut DROP id_value ;
ALTER TABLE taxonomie.bdc_statut DROP id_text;


-- ##############################################
--------- CREATE TABLE
-- ##############################################
DROP TABLE IF EXISTS taxonomie.bdc_statut_cor_text_values CASCADE;
DROP TABLE IF EXISTS taxonomie.bdc_statut_text CASCADE;
DROP TABLE IF EXISTS taxonomie.bdc_statut_values ;
DROP TABLE IF EXISTS taxonomie.bdc_statut_taxons ;

CREATE TABLE taxonomie.bdc_statut_text (
	id_text serial NOT NULL PRIMARY KEY,
	cd_st_text  varchar(50),
	cd_type_statut varchar(50) NOT NULL,
	cd_sig varchar(50),
	cd_doc int4,
	niveau_admin varchar(250),
	cd_iso3166_1 varchar(50),
	cd_iso3166_2 varchar(50),
	lb_adm_tr varchar(250),
	full_citation text,
	doc_url TEXT,
	ENABLE boolean DEFAULT(true)
);

ALTER TABLE taxonomie.bdc_statut_text
	ADD CONSTRAINT bdc_statut_text_fkey FOREIGN KEY (cd_type_statut)
REFERENCES taxonomie.bdc_statut_type(cd_type_statut) ON DELETE CASCADE ON UPDATE CASCADE;

CREATE TABLE taxonomie.bdc_statut_values (
	id_value serial NOT NULL PRIMARY KEY,
	code_statut varchar(50) NOT NULL,
	label_statut varchar(250)
);

CREATE TABLE taxonomie.bdc_statut_cor_text_values (
	id_value_text serial NOT NULL PRIMARY KEY,
	id_value int4 NOT NULL,
	id_text int4 NOT NULL
);

ALTER TABLE taxonomie.bdc_statut_cor_text_values
	ADD CONSTRAINT tbdc_statut_cor_text_values_id_value_fkey FOREIGN KEY (id_value)
REFERENCES taxonomie.bdc_statut_values(id_value) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE taxonomie.bdc_statut_cor_text_values
	ADD CONSTRAINT tbdc_statut_cor_text_values_id_text_fkey FOREIGN KEY (id_text)
REFERENCES taxonomie.bdc_statut_text(id_text) ON DELETE CASCADE ON UPDATE CASCADE;


CREATE TABLE taxonomie.bdc_statut_taxons (
	id int4 NOT NULL PRIMARY KEY,
	id_value_text int4 NOT NULL,
	cd_nom int4 NOT NULL,
	cd_ref int4 NOT NULL, -- TO KEEP?
	rq_statut varchar(1000)
);

ALTER TABLE taxonomie.bdc_statut_taxons
	ADD CONSTRAINT bdc_statut_taxons_id_value_text_fkey FOREIGN KEY (id_value_text)
REFERENCES taxonomie.bdc_statut_cor_text_values(id_value_text) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE taxonomie.bdc_statut_taxons
	ADD CONSTRAINT bdc_statut_taxons_cd_nom_fkey FOREIGN KEY (cd_nom)
REFERENCES taxonomie.taxref(cd_nom) ON DELETE CASCADE ON UPDATE CASCADE;

COMMENT ON TABLE taxonomie.bdc_statut_text IS 'Table contenant les textes et leur zone d''application';
COMMENT ON TABLE taxonomie.bdc_statut_type IS 'Table des grands type de statuts';
COMMENT ON TABLE taxonomie.bdc_statut IS 'Table initialement fournie par l''INPN. Contient tout les statuts sous leur forme brute';
COMMENT ON TABLE taxonomie.bdc_statut_values IS 'Table contenant la liste des valeurs possible pour les textes';
COMMENT ON TABLE taxonomie.bdc_statut_taxons IS 'Table d''association entre les textes et les taxons';
COMMENT ON TABLE taxonomie.bdc_statut_cor_text_values IS 'Table d''association entre les textes, les taxons et la valeur';

-- ##############################################"""""
--------- POPULATE TABLE
-- ##############################################"""""

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


-- ##############################################"""""
--------- CLEAN
-- ##############################################"""""
ALTER  TABLE taxonomie.bdc_statut_text DROP id;

ALTER  TABLE taxonomie.bdc_statut_values DROP id;
ALTER  TABLE taxonomie.bdc_statut_values DROP ids_text;

ALTER TABLE taxonomie.bdc_statut DROP IF EXISTS id_value_text ;
ALTER TABLE taxonomie.bdc_statut DROP IF EXISTS id_value ;
ALTER TABLE taxonomie.bdc_statut DROP IF EXISTS id_text;




CREATE OR REPLACE VIEW taxonomie.v_bdc_status AS
SELECT s.cd_nom, s.cd_ref, s.rq_statut, v.code_statut , v.label_statut,
t.cd_type_statut, ty.thematique, ty.lb_type_statut, ty.regroupement_type,cd_st_text, t.cd_sig, t.cd_doc, t.niveau_admin, t.cd_iso3166_1, t.cd_iso3166_2,
t.full_citation, t.doc_url, ty.type_value
FROM taxonomie.bdc_statut_taxons s
JOIN taxonomie.bdc_statut_cor_text_values c
ON s.id_value_text  = c.id_value_text
JOIN taxonomie.bdc_statut_text t
ON t.id_text  = c.id_text
JOIN taxonomie.bdc_statut_values v
ON v.id_value = c.id_value
JOIN taxonomie.bdc_statut_type ty
ON ty.cd_type_statut = t.cd_type_statut
WHERE t.ENABLE = true;
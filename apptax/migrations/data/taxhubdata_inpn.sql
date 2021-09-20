--
-- Insertion des dictionnaires taxref
--


--
--
-- Data for Name: bib_taxref_categories_lr; Type: TABLE DATA; Schema: taxonomie; Owner: -
--

-- TO KEEP ???
-- INSERT INTO bib_taxref_categories_lr VALUES ('EX', 'Disparues', 'Eteinte à l''état sauvage', 'Eteinte au niveau mondial');
-- INSERT INTO bib_taxref_categories_lr VALUES ('EW', 'Disparues', 'Eteinte à l''état sauvage', 'Eteinte à l''état sauvage');
-- INSERT INTO bib_taxref_categories_lr VALUES ('RE', 'Disparues', 'Disparue au niveau régional', 'Disparue au niveau régional');
-- INSERT INTO bib_taxref_categories_lr VALUES ('CR', 'Menacées de disparition', 'En danger critique', 'En danger critique');
-- INSERT INTO bib_taxref_categories_lr VALUES ('EN', 'Menacées de disparition', 'En danger', 'En danger');
-- INSERT INTO bib_taxref_categories_lr VALUES ('VU', 'Menacées de disparition', 'Vulnérable', 'Vulnérable');
-- INSERT INTO bib_taxref_categories_lr VALUES ('NT', 'Autre', 'Quasi menacée', 'Espèce proche du seuil des espèces menacées ou qui pourrait être menacée si des mesures de conservation spécifiques n''étaient pas prises');
-- INSERT INTO bib_taxref_categories_lr VALUES ('LC', 'Autre', 'Préoccupation mineure', 'Espèce pour laquelle le risque de disparition est faible');
-- INSERT INTO bib_taxref_categories_lr VALUES ('DD', 'Autre', 'Données insuffisantes', 'Espèce pour laquelle l''évaluation n''a pas pu être réalisée faute de données suffisantes');
-- INSERT INTO bib_taxref_categories_lr VALUES ('NA', 'Autre', 'Non applicable', 'Espèce non soumise à évaluation car (a) introduite dans la période récente ou (b) présente en métropole de manière occasionnelle ou marginale');
-- INSERT INTO bib_taxref_categories_lr VALUES ('NE', 'Autre', 'Non évaluée', 'Espèce non encore confrontée aux critères de la Liste rouge');


--insertion dans la table taxref
TRUNCATE TABLE taxonomie.taxref CASCADE;
INSERT INTO taxonomie.taxref
      SELECT cd_nom, fr as id_statut, habitat::int as id_habitat, rang as  id_rang, regne, phylum, classe,
             ordre, famille,  sous_famille, tribu, cd_taxsup, cd_sup, cd_ref, lb_nom, substring(lb_auteur, 1, 250),
             nom_complet, nom_complet_html,nom_valide, substring(nom_vern,1,1000), nom_vern_eng, group1_inpn, group2_inpn, url
        FROM taxonomie.import_taxref;



-- Nettoyage de la table d'import temporaire de taxref
TRUNCATE TABLE taxonomie.import_taxref;

ALTER TABLE taxonomie.bdc_statut ADD id serial;


--- Suppression des données en double contenu dans la table  bdc_statut
CREATE INDEX bdc_statut_id_idx ON taxonomie.bdc_statut (id);

WITH d AS (
    SELECT
        count(*), min(id), array_agg(id)
    FROM taxonomie.bdc_statut
    GROUP BY
        cd_nom, cd_ref, cd_sup, cd_type_statut, lb_type_statut, regroupement_type, code_statut, label_statut, rq_statut,
        cd_sig, cd_doc, lb_nom, lb_auteur, nom_complet_html, nom_valide_html, regne, phylum, classe, ordre, famille, group1_inpn,
        group2_inpn, lb_adm_tr, niveau_admin, cd_iso3166_1, cd_iso3166_2, full_citation, doc_url, thematique, type_value
    HAVING count(*) >1
) , id_doublon AS (
    SELECT min, unnest(array_agg) as to_del
    FROM d
)
DELETE
FROM  taxonomie.bdc_statut s
USING id_doublon d
WHERE s.id = d.to_del and not id = min;

DROP INDEX taxonomie.bdc_statut_id_idx;

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

ALTER TABLE taxonomie.bdc_statut DROP IF EXISTS id_value_text;
ALTER TABLE taxonomie.bdc_statut DROP IF EXISTS id_value;
ALTER TABLE taxonomie.bdc_statut DROP IF EXISTS id_text;

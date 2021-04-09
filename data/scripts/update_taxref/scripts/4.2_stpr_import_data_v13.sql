DROP TABLE  IF EXISTS taxonomie.bdc_statut_type ;
CREATE TABLE taxonomie.bdc_statut_type (
    cd_type_statut varchar(50) PRIMARY KEY,
    lb_type_statut varchar(250),
    regroupement_type varchar(250),
    thematique varchar(50),
    type_value varchar(50)
);

DROP TABLE  IF EXISTS taxonomie.bdc_statut ;
CREATE TABLE taxonomie.bdc_statut (
    cd_nom int NOT NULL,
    cd_ref int NOT NULL,
    cd_sup int,
    cd_type_statut varchar(50) NOT NULL,
    lb_type_statut varchar(250),
    regroupement_type varchar(250),
    code_statut varchar(50),
    label_statut varchar(250),
    rq_statut varchar(1000),
    cd_sig varchar(50),
    cd_doc int,
    lb_nom varchar(100) NULL,
    lb_auteur varchar(250) NULL,
    nom_complet_html varchar(500) NULL,
    nom_valide_html varchar(500),
    regne varchar(250) NULL,
    phylum varchar(250) NULL,
    classe varchar(250) NULL,
    ordre varchar(250) NULL,
    famille varchar(250) NULL,
    group1_inpn varchar(255) NULL,
    group2_inpn varchar(255) NULL,
    lb_adm_tr varchar(50),
    niveau_admin varchar(250),
    cd_iso3166_1 varchar(50),
    cd_iso3166_2 varchar(50),
    full_citation text,
    doc_url text,
    thematique varchar(50),
    type_value varchar(50)
);

---------------------------
---------------------------
-- COPY DATA
---------------------------
---------------------------

COPY taxonomie.bdc_statut_type
FROM  '/tmp/taxhub/BDC_STATUTS_TYPES_13.csv'
WITH  CSV HEADER;


COPY taxonomie.bdc_statut
FROM  '/tmp/taxhub/BDC_STATUTS_13.csv'
WITH  CSV HEADER
  ENCODING 'ISO 8859-1';

---------------------------
---------------------------

-- Suppression des doublons
-- 773 doublons lorsque l'on test tous les champs
ALTER TABLE taxonomie.bdc_statut ADD id serial;

WITH d AS (
    SELECT
        count(*), min(id), array_agg(id),  cd_nom, cd_ref, cd_sup, cd_type_statut, lb_type_statut, regroupement_type, code_statut, label_statut, rq_statut,
        cd_sig, cd_doc, lb_nom, lb_auteur, nom_complet_html, nom_valide_html, regne, phylum, classe, ordre, famille, group1_inpn,
        group2_inpn, lb_adm_tr, niveau_admin, cd_iso3166_1, cd_iso3166_2, full_citation, doc_url, thematique, type_value
    FROM taxonomie.bdc_statut
    GROUP BY
        cd_nom, cd_ref, cd_sup, cd_type_statut, lb_type_statut, regroupement_type, code_statut, label_statut, rq_statut,
        cd_sig, cd_doc, lb_nom, lb_auteur, nom_complet_html, nom_valide_html, regne, phylum, classe, ordre, famille, group1_inpn,
        group2_inpn, lb_adm_tr, niveau_admin, cd_iso3166_1, cd_iso3166_2, full_citation, doc_url, thematique, type_value
    HAVING count(*) >1
) , id_liste AS (
  cd_sig varchar(50),
  lb_adm_tr varchar(50),
  niveau_admin varchar(250),
  cd_iso3166_1 varchar(50),
  cd_iso3166_2 varchar(50),

    SELECT id_d
  CD_DOC
    FROM id_liste
    WHERE NOT id_d = min
)
DELETE FROM  taxonomie.bdc_statut
WHERE id IN (SELECT id_d FROM id_doublon);


-- correction cd_sig Deux-Sèvres, Charente-Maritime et Vienne
-- Reste des cd_sig non associés à des données (INSEERN84, INSEENR32, TER984)
UPDATE taxonomie.bdc_statut d SET
    cd_sig = a.cd_sig,
    lb_adm_tr = a.lb_adm_tr,
    niveau_admin = a.niveau_admin,
    cd_iso3166_1 = a.cd_iso3166_1,
    cd_iso3166_2 = a.cd_iso3166_2
FROM (
    SELECT DISTINCT cd_sig, lb_adm_tr, niveau_admin, cd_iso3166_1, cd_iso3166_2
    FROM taxonomie.bdc_statut
    WHERE cd_sig IN ('INSEED79',  'INSEED17', 'INSEED86')
) a
WHERE d.cd_sig ilike 'INSEED %' AND a.cd_sig = REPLACE(d.cd_sig, ' ', '')

-- correction cd_sig manquant
--    UEPOMACEA : Interdiction d’introduction et de propagation dans l’Union le genre Pomacea (Perry)
UPDATE taxonomie.bdc_statut d SET
    cd_sig = 'ETATFRA',
    lb_adm_tr = 'France',
    niveau_admin = 'État'
WHERE code_statut = 'UEPOMACEA';




-----------------------------------
--- Création  modèle
----------------------------------

DROP TABLE IF EXISTS taxonomie.bib_taxref_statut_values;
CREATE TABLE taxonomie.bib_taxref_statut_values
(
  cd_value character(50) PRIMARY KEY,
  label character varying(50) NOT NULL,
  description character varying(255)
);

DROP TABLE IF EXISTS taxonomie.taxref_statut_types;
CREATE TABLE taxonomie.taxref_statut_types (
    cd_type_statut varchar(50) PRIMARY KEY,
    lb_type_statut varchar(250),
    regroupement_type varchar(250),
    thematique varchar(50),
    type_value varchar(50)
);

DROP TABLE IF EXISTS taxonomie.taxref_statut_articles;
CREATE TABLE taxonomie.taxref_statut_articles
(
  cd_statut character varying(50) NOT NULL,
  label_statut varchar(250),
  rq_statut varchar(1000),
  --article character varying(100), -- => cf label_statut
  --intitule text,  -- => cf label_statut
  --arrete text, -- Pas présent
  full_citation text,

  --cd_arrete integer, -- Pas présent
  --url_inpn character varying(1000),

  cd_doc integer,
  --url character varying(1000), -- => cf doc_url
  doc_url text,

  date_arrete integer,
  cd_type_statut varchar(50),

  cd_sig varchar(50),
  lb_adm_tr varchar(50),
  niveau_admin varchar(250),
  cd_iso3166_1 varchar(50),
  cd_iso3166_2 varchar(50),

  concerne_mon_territoire boolean DEFAULT ((true)),

  CONSTRAINT taxref_statut_articles_pkey PRIMARY KEY (cd_statut),
  CONSTRAINT taxref_statut_articles_cd_type_statut_fkey FOREIGN KEY (cd_type_statut)
      REFERENCES taxonomie.taxref_statut_types (cd_type_statut) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
);

DROP TABLE IF EXISTS taxonomie.taxref_statut_especes;
CREATE TABLE taxonomie.taxref_statut_especes (
  cd_nom integer NOT NULL,
  cd_statut character varying(50) NOT NULL,
  cd_value character varying(50) NOT NULL,
  -- nom_cite character varying(200),
  -- syn_cite character varying(200),
  -- nom_francais_cite character varying(100),
  precisions text,
  -- cd_nom_cite character varying(255) NOT NULL,
  CONSTRAINT taxref_statut_especes_pkey PRIMARY KEY (cd_nom, cd_statut, cd_value),
  CONSTRAINT taxref_statut_especes_cd_nom_fkey FOREIGN KEY (cd_nom)
      REFERENCES taxonomie.taxref (cd_nom) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE NO ACTION,
  CONSTRAINT taxref_statut_especes_cd_statut_fkey FOREIGN KEY (cd_statut)
      REFERENCES taxonomie.taxref_statut_articles (cd_statut) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT taxref_statut_especes_cd_value_fkey FOREIGN KEY (cd_value)
      REFERENCES taxonomie.bib_taxref_statut_values (cd_value) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE NO ACTION
);



-----------------------------------
--- Import données
----------------------------------


INSERT INTO taxonomie.taxref_statut_types (cd_type_statut, lb_type_statut, regroupement_type, thematique, type_value)
SELECT cd_type_statut, lb_type_statut, regroupement_type, thematique, type_value
FROM taxonomie.bdc_statut_type
WHERE NOT regroupement_type IN ('SENSIBILITE', 'Statut biogéographique');


INSERT INTO taxonomie.bib_taxref_statut_values (cd_value, "label", description) VALUES('true', '', NULL);

-- ## articles
-- # Directives européenne => rq_statut == precision de taxref_statut_especes
-- # Conventions internationales => rq_statut == precision de taxref_statut_especes
-- Protection => rq_statut == precision de taxref_statut_especes

INSERT INTO taxonomie.taxref_statut_articles (
code_statut, label_statut, rq_statut, full_citation, cd_doc, doc_url, date_arrete, cd_type_statut,
cd_sig, lb_adm_tr, niveau_admin, cd_iso3166_1, cd_iso3166_2)
SELECT DISTINCT cd_type_statut AS cd_statut,
label_statut, NULL , tbs.full_citation, cd_doc, doc_url, SUBSTRING(full_citation, '((19|20)\d{2})') AS date_arrete,  cd_type_statut,
cd_sig, lb_adm_tr, niveau_admin, cd_iso3166_1, cd_iso3166_2
FROM taxonomie.bdc_statut tbs
WHERE regroupement_type IN ('Directives européennes', 'Conventions internationales', 'Protection');


-- # ZNIEFF => rq_statut == precision de taxref_statut_especes

DROP TABLE IF EXISTS  taxonomie.import_znieff ;
CREATE TABLE taxonomie.import_znieff (
annee int, 	taxo varchar(100),	code	varchar(100), full_citation text
);
COPY taxonomie.import_znieff
FROM  '/tmp/taxhub/bdc_statut_znieff.csv'
WITH  CSV HEADER;


INSERT INTO taxonomie.taxref_statut_articles (
cd_statut, label_statut, rq_statut, full_citation, cd_doc, doc_url, date_arrete, cd_type_statut,
cd_sig, lb_adm_tr, niveau_admin, cd_iso3166_1, cd_iso3166_2)
SELECT DISTINCT cd_type_statut || '_' || SUBSTRING(cd_sig, '.\d+$') || '_' || code AS cd_statut,
taxo AS label_statut, NULL , tbs.full_citation, cd_doc, doc_url, annee::int AS date_arrete,  cd_type_statut,
cd_sig, lb_adm_tr, niveau_admin, cd_iso3166_1, cd_iso3166_2
FROM taxonomie.bdc_statut tbs
JOIN taxonomie.import_znieff iz
ON iz.full_citation = tbs.full_citation
WHERE regroupement_type = 'ZNIEFF';


INSERT INTO taxonomie.taxref_statut_especes (cd_nom, cd_statut, cd_value, precisions)
SELECT DISTINCT cd_nom, cd_statut, 'true', string_agg(tbs.rq_statut, '; ')
FROM taxonomie.bdc_statut tbs
JOIN taxonomie.taxref_statut_articles a
ON a.full_citation  = tbs.full_citation AND a.cd_sig = tbs.cd_sig
WHERE regroupement_type = 'ZNIEFF'
GROUP BY cd_nom, cd_statut, TRUE;

--------------------------------------------------------------------------------------------------------------------------------------------
-----------------------------------
--- TESTS
-----------------------------------
-----------------------------------
-- selection des statuts de protection d'interets


ALTER TABLE taxonomie.bdc_statut_type ADD enable boolean DEFAULT (false);

UPDATE  taxonomie.bdc_statut_type  SET enable = true
WHERE  (
    regroupement_type  IN ('Protection', 'Conventions internationales', 'Directives européennes')
    OR
    cd_type_statut IN ('REGL', 'REGLSO')
);


CREATE TABLE taxonomie.bdc_statut_geo  AS (
    cd_sig varchar(50) PRIMARY KEY,
    lb_adm_tr varchar(50),
    niveau_admin varchar(250),
    cd_iso3166_1 varchar(50),
    cd_iso3166_2 varchar(50)

);

INSERT INTO taxonomie.bdc_statut_geo
SELECT DISTINCT
    cd_sig,
    lb_adm_tr,
    niveau_admin,
    cd_iso3166_1,
    cd_iso3166_2
FROM taxonomie.bdc_statut;

ALTER TABLE taxonomie.bdc_statut_geo ADD enable boolean DEFAULT (false);



--- protection article

CREATE TABLE taxonomie.taxref_protection_articles
(
  cd_protection character varying(20) NOT NULL,
  article character varying(100),
  intitule text,
  arrete text,
  cd_arrete integer,
  url_inpn character varying(250),
  cd_doc integer,
  url character varying(250),
  date_arrete integer,
  type_protection character varying(250),
  concerne_mon_territoire boolean,
  CONSTRAINT taxref_protection_articles_pkey PRIMARY KEY (cd_protection)
)



CREATE MATERIALIZED VIEW taxonomie.taxref_protection_articles AS
SELECT
    -- -- Regroupement
    st.cd_type_statut,
    st.lb_type_statut,
    st.regroupement_type,
    st.thematique,
    st.type_value,

    -- -- Statut
    st.code_statut,
    label_statut,
    --rq_statut, -- s'applique au niveau du taxon
    st.full_citation,
    st.cd_doc,
    st.doc_url,
    -- emprise géographique du statut
    st.cd_sig,
    st.lb_adm_tr,
    st.niveau_admin,
    st.cd_iso3166_1,
    st.cd_iso3166_2

FROM taxonomie.bdc_statut st
JOIN taxonomie.bdc_statut_geo g
ON g.cd_sig = st.cd_sig AND g.enable = true
JOIN taxonomie.bdc_statut_type t
ON t.cd_type_statut = st.cd_type_statut AND t.enable = true



SELECT DISTINCT
    -- -- Regroupement
    cd_type_statut,
    lb_type_statut,
    regroupement_type,
    thematique,
    type_value,

    -- -- Statut
    code_statut,
    label_statut,
    --rq_statut, -- s'applique au niveau du taxon
    full_citation,
    cd_doc,
    doc_url,
    -- emprise géographique du statut
    cd_sig,
    lb_adm_tr,
    niveau_admin,
    cd_iso3166_1,
    cd_iso3166_2
FROM taxonomie.bdc_statut
WHERE (regroupement_type  IN ('Protection', 'Conventions internationales') OR cd_type_statut IN ('REGL', 'REGLSO'))
    AND (
        cd_sig IN ('TERFXFR', 'ETATFRA')
        OR  cd_sig IN ('INSEED07', 'INSEED12', 'INSEED30', 'INSEED48', 'INSEER91', 'INSEER73')  --zone interet PNC
    )



CREATE TABLE  IF NOT EXISTS taxonomie.bdc_statut_type (
    cd_type_statut varchar(50) PRIMARY KEY,
    lb_type_statut varchar(250),
    regroupement_type varchar(250),
    thematique varchar(50),
    type_value varchar(50)
);

CREATE TABLE  IF NOT EXISTS taxonomie.bdc_statut(
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

ALTER TABLE taxonomie.bdc_statut_type OWNER TO :MYPGUSER;
ALTER TABLE taxonomie.bdc_statut OWNER TO :MYPGUSER;

TRUNCATE TABLE  taxonomie.bdc_statut_type CASCADE;
TRUNCATE TABLE  taxonomie.bdc_statut ;

ALTER TABLE taxonomie.bdc_statut DROP COLUMN IF EXISTS id;

---------------------------
---------------------------
-- COPY DATA
---------------------------
---------------------------

COPY taxonomie.bdc_statut_type
FROM  '/tmp/taxhub/BDC-Statuts-v14/BDC_STATUTS_TYPES_14.csv'
WITH  CSV HEADER;


COPY taxonomie.bdc_statut
FROM  '/tmp/taxhub/BDC-Statuts-v14/BDC_STATUTS_14.csv'
WITH  CSV HEADER
    ENCODING 'ISO 8859-1';

---------------------------
---------------------------

-- Suppression des doublons
-- 829 doublons lorsque l'on test tous les champs
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
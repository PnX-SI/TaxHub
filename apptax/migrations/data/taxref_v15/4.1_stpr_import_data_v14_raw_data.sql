
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

TRUNCATE TABLE  taxonomie.bdc_statut_type CASCADE;
TRUNCATE TABLE  taxonomie.bdc_statut ;

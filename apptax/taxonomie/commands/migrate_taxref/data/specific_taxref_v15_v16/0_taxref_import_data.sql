-- Créer la table import_taxref


DROP TABLE IF EXISTS taxonomie.import_taxref;
CREATE TABLE taxonomie.import_taxref
(
    regne character varying(20),
    phylum character varying(50),
    classe character varying(50),
    ordre character varying(50),
    famille character varying(50),
    SOUS_FAMILLE character varying(50),
    TRIBU character varying(50),
    group1_inpn character varying(50),
    group2_inpn character varying(50),
    group3_inpn character varying(50),
    cd_nom integer NOT NULL,
    cd_taxsup integer,
    cd_sup integer,
    cd_ref integer,
    rang character varying(10),
    lb_nom character varying(100),
    lb_auteur character varying(500),
    nom_complet character varying(500),
    nom_complet_html character varying(500),
    nom_valide character varying(500),
    nom_vern text,
    nom_vern_eng character varying(500),
    habitat character varying(10),
    fr character varying(10),
    gf character varying(10),
    mar character varying(10),
    gua character varying(10),
    sm character varying(10),
    sb character varying(10),
    spm character varying(10),
    may character varying(10),
    epa character varying(10),
    reu character varying(10),
    SA character varying(10),
    TA character varying(10),
    taaf character varying(10),
    pf character varying(10),
    nc character varying(10),
    wf character varying(10),
    cli character varying(10),
    url text
);

ALTER TABLE taxonomie.import_taxref ADD CONSTRAINT pk_import_taxref PRIMARY KEY (cd_nom);

-- Créer la table cdnom_disparus
DROP TABLE IF EXISTS taxonomie.cdnom_disparu;
CREATE TABLE taxonomie.cdnom_disparu (
    CD_NOM	int,
    PLUS_RECENTE_DIFFUSION character varying(50),
    CD_NOM_REMPLACEMENT	int,
    CD_RAISON_SUPPRESSION int,
    RAISON_SUPPRESSION text
);


DROP TABLE IF EXISTS taxonomie.import_taxref_rangs;
CREATE TABLE taxonomie.import_taxref_rangs (
	level int NOT NULL,
	rang varchar(20) NOT NULL,
	detail_fr varchar(50) NOT NULL,
  detail_en varchar(50) NOT NULL
);

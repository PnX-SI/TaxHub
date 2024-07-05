-- ----------------------------------------------------------------------
-- Crate import_taxref table
DROP TABLE IF EXISTS taxonomie.import_taxref;
CREATE TABLE taxonomie.import_taxref (
    regne character varying(20),
    phylum character varying(50),
    classe character varying(50),
    ordre character varying(50),
    famille character varying(50),
    sous_famille character varying(50),
    tribu character varying(50),
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
    sa character varying(10),
    ta character varying(10),
    taaf character varying(10),
    pf character varying(10),
    nc character varying(10),
    wf character varying(10),
    cli character varying(10),
    "url" text
);

ALTER TABLE taxonomie.import_taxref ADD CONSTRAINT pk_import_taxref PRIMARY KEY (cd_nom);

-- ----------------------------------------------------------------------
-- Create cdnom_disparus table
DROP TABLE IF EXISTS taxonomie.cdnom_disparu;
CREATE TABLE taxonomie.cdnom_disparu (
    cd_nom	int,
    plus_recente_diffusion character varying(50),
    cd_nom_remplacement	int,
    cd_raison_suppression int,
    raison_suppression text
);

-- Added by Nicolas Imbert
CREATE INDEX IF NOT EXISTS i_tmp_cdnom_disparu_cd_nom ON taxonomie.cdnom_disparu (cd_nom);

-- ----------------------------------------------------------------------
-- Create import_taxref_rangs table
DROP TABLE IF EXISTS taxonomie.import_taxref_rangs;
CREATE TABLE taxonomie.import_taxref_rangs (
    "level" int NOT NULL,
    rang varchar(20) NOT NULL,
    detail_fr varchar(50) NOT NULL,
    detail_en varchar(50) NOT NULL
);

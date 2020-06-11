
ALTER TABLE taxonomie.import_taxref RENAME TO import_taxref_v9;

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
    cd_nom integer NOT NULL,
    cd_taxsup integer,
    cd_sup integer,
    cd_ref integer,
    rang character varying(10),
    lb_nom character varying(100),
    lb_auteur character varying(250),
    nom_complet character varying(255),
    nom_complet_html character varying(255),
    nom_valide character varying(255),
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



COPY taxonomie.import_taxref FROM  '/tmp/taxhub/TAXREFv11.txt'
WITH  CSV HEADER 
DELIMITER E'\t'  encoding 'UTF-8';

DROP TABLE IF EXISTS taxonomie.cdnom_disparu;
CREATE TABLE taxonomie.cdnom_disparu (
    CD_NOM	int,
    PLUS_RECENTE_DIFFUSION character varying(50),
    CD_NOM_REMPLACEMENT	int, 
    CD_RAISON_SUPPRESSION int, 
    RAISON_SUPPRESSION text
);

COPY taxonomie.cdnom_disparu FROM  '/tmp/taxhub/CDNOM_DISPARUS.csv'
WITH  CSV HEADER 
DELIMITER E'\t'  encoding 'UTF-8';

ALTER TABLE taxonomie.taxref_changes DROP CONSTRAINT pk_taxref_changes;

ALTER TABLE taxonomie.taxref_changes
  ADD CONSTRAINT pk_taxref_changes PRIMARY KEY(cd_nom, champ,num_version_init, num_version_final);


ALTER TABLE taxonomie.taxref_changes
   ALTER COLUMN valeur_init TYPE character varying(1500);

ALTER TABLE taxonomie.taxref_changes
   ALTER COLUMN valeur_final TYPE character varying(1500);

COPY taxonomie.taxref_changes FROM  '/tmp/taxhub/TAXREF_CHANGES.txt'
WITH  CSV HEADER 
DELIMITER E'\t'  encoding 'UTF-8';

/*
COPY taxonomie.taxref_changes FROM  '/tmp/taxhub/TAXREF_CHANGES_v10.txt'
WITH  CSV HEADER 
DELIMITER E'\t'  encoding 'UTF-8';
*/

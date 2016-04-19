--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: taxonomie; Type: SCHEMA; Schema: -; Owner: geonatuser
--

CREATE SCHEMA taxonomie;


ALTER SCHEMA taxonomie OWNER TO geonatuser;

SET search_path = taxonomie, pg_catalog;

--
-- Name: find_cdref(integer); Type: FUNCTION; Schema: taxonomie; Owner: geonatuser
--

CREATE FUNCTION find_cdref(id integer) RETURNS integer
    LANGUAGE plpgsql
    AS $$
--fonction permettant de renvoyer le cd_ref d'un taxon à partir de son cd_nom
--
--Gil DELUERMOZ septembre 2011

  DECLARE ref integer;
  BEGIN
	SELECT INTO ref cd_ref FROM taxonomie.taxref WHERE cd_nom = id;
	return ref;
  END;
$$;


ALTER FUNCTION taxonomie.find_cdref(id integer) OWNER TO geonatuser;

--
-- Name: bib_attributs_id_attribut_seq; Type: SEQUENCE; Schema: taxonomie; Owner: geonatuser
--

CREATE SEQUENCE bib_attributs_id_attribut_seq
    START WITH 1000000
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE taxonomie.bib_attributs_id_attribut_seq OWNER TO geonatuser;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: bib_attributs; Type: TABLE; Schema: taxonomie; Owner: geonatuser; Tablespace: 
--

CREATE TABLE bib_attributs (
    id_attribut integer DEFAULT nextval('bib_attributs_id_attribut_seq'::regclass) NOT NULL,
    nom_attribut character varying(255) NOT NULL,
    label_attribut character varying(50) NOT NULL,
    liste_valeur_attribut text NOT NULL,
    obligatoire boolean NOT NULL,
    desc_attribut text,
    type_attribut character varying(50),
    regne character varying(20),
    group2_inpn character varying(255)
);


ALTER TABLE taxonomie.bib_attributs OWNER TO geonatuser;

--
-- Name: bib_listes_id_liste_seq; Type: SEQUENCE; Schema: taxonomie; Owner: geonatuser
--

CREATE SEQUENCE bib_listes_id_liste_seq
    START WITH 1000000
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE taxonomie.bib_listes_id_liste_seq OWNER TO geonatuser;

--
-- Name: bib_listes; Type: TABLE; Schema: taxonomie; Owner: geonatuser; Tablespace: 
--

CREATE TABLE bib_listes (
    id_liste integer DEFAULT nextval('bib_listes_id_liste_seq'::regclass) NOT NULL,
    nom_liste character varying(255) NOT NULL,
    desc_liste text,
    picto character varying(50),
    regne character varying(20),
    group2_inpn character varying(255)
);


ALTER TABLE taxonomie.bib_listes OWNER TO geonatuser;

--
-- Name: COLUMN bib_listes.picto; Type: COMMENT; Schema: taxonomie; Owner: geonatuser
--

COMMENT ON COLUMN bib_listes.picto IS 'Indique le chemin vers l''image du picto représentant le groupe taxonomique dans les menus déroulants de taxons';


--
-- Name: bib_taxons; Type: TABLE; Schema: taxonomie; Owner: geonatuser; Tablespace: 
--

CREATE TABLE bib_taxons (
    id_taxon integer NOT NULL,
    cd_nom integer,
    nom_latin character varying(100),
    nom_francais character varying(255),
    auteur character varying(200)
);


ALTER TABLE taxonomie.bib_taxons OWNER TO geonatuser;

--
-- Name: bib_taxons_id_taxon_seq; Type: SEQUENCE; Schema: taxonomie; Owner: geonatuser
--

CREATE SEQUENCE bib_taxons_id_taxon_seq
    START WITH 2805
    INCREMENT BY 1
    MINVALUE 2805
    NO MAXVALUE
    CACHE 1;


ALTER TABLE taxonomie.bib_taxons_id_taxon_seq OWNER TO geonatuser;

--
-- Name: bib_taxref_habitats; Type: TABLE; Schema: taxonomie; Owner: geonatuser; Tablespace: 
--

CREATE TABLE bib_taxref_habitats (
    id_habitat integer NOT NULL,
    nom_habitat character varying(50) NOT NULL,
    desc_habitat text
);


ALTER TABLE taxonomie.bib_taxref_habitats OWNER TO geonatuser;

--
-- Name: bib_taxref_rangs; Type: TABLE; Schema: taxonomie; Owner: geonatuser; Tablespace: 
--

CREATE TABLE bib_taxref_rangs (
    id_rang character(4) NOT NULL,
    nom_rang character varying(20) NOT NULL
);


ALTER TABLE taxonomie.bib_taxref_rangs OWNER TO geonatuser;

--
-- Name: bib_taxref_statuts; Type: TABLE; Schema: taxonomie; Owner: geonatuser; Tablespace: 
--

CREATE TABLE bib_taxref_statuts (
    id_statut character(1) NOT NULL,
    nom_statut character varying(50) NOT NULL
);


ALTER TABLE taxonomie.bib_taxref_statuts OWNER TO geonatuser;

--
-- Name: cor_taxon_attribut; Type: TABLE; Schema: taxonomie; Owner: geonatuser; Tablespace: 
--

CREATE TABLE cor_taxon_attribut (
    id_taxon integer NOT NULL,
    id_attribut integer NOT NULL,
    valeur_attribut character varying(50) NOT NULL
);


ALTER TABLE taxonomie.cor_taxon_attribut OWNER TO geonatuser;

--
-- Name: cor_taxon_liste; Type: TABLE; Schema: taxonomie; Owner: geonatuser; Tablespace: 
--

CREATE TABLE cor_taxon_liste (
    id_liste integer NOT NULL,
    id_taxon integer NOT NULL
);


ALTER TABLE taxonomie.cor_taxon_liste OWNER TO geonatuser;

--
-- Name: import_taxref; Type: TABLE; Schema: taxonomie; Owner: geonatuser; Tablespace: 
--

CREATE TABLE import_taxref (
    regne character varying(20),
    phylum character varying(50),
    classe character varying(50),
    ordre character varying(50),
    famille character varying(50),
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
    taaf character varying(10),
    pf character varying(10),
    nc character varying(10),
    wf character varying(10),
    cli character varying(10),
    url text
);


ALTER TABLE taxonomie.import_taxref OWNER TO geonatuser;

--
-- Name: taxref; Type: TABLE; Schema: taxonomie; Owner: geonatuser; Tablespace: 
--

CREATE TABLE taxref (
    cd_nom integer NOT NULL,
    id_statut character(1),
    id_habitat integer,
    id_rang character varying(4),
    regne character varying(20),
    phylum character varying(50),
    classe character varying(50),
    ordre character varying(50),
    famille character varying(50),
    cd_taxsup integer,
    cd_sup integer,
    cd_ref integer,
    lb_nom character varying(100),
    lb_auteur character varying(150),
    nom_complet character varying(255),
    nom_complet_html character varying(255),
    nom_valide character varying(255),
    nom_vern character varying(255),
    nom_vern_eng character varying(255),
    group1_inpn character varying(255),
    group2_inpn character varying(255)
);


ALTER TABLE taxonomie.taxref OWNER TO geonatuser;

--
-- Name: taxref_changes; Type: TABLE; Schema: taxonomie; Owner: geonatuser; Tablespace: 
--

CREATE TABLE taxref_changes (
    cd_nom integer NOT NULL,
    num_version_init character varying(5),
    num_version_final character varying(5),
    champ character varying(50) NOT NULL,
    valeur_init character varying(255),
    valeur_final character varying(255),
    type_change character varying(25)
);


ALTER TABLE taxonomie.taxref_changes OWNER TO geonatuser;

--
-- Name: taxref_protection_articles; Type: TABLE; Schema: taxonomie; Owner: geonatuser; Tablespace: 
--

CREATE TABLE taxref_protection_articles (
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
    concerne_mon_territoire boolean
);


ALTER TABLE taxonomie.taxref_protection_articles OWNER TO geonatuser;

--
-- Name: taxref_protection_especes; Type: TABLE; Schema: taxonomie; Owner: geonatuser; Tablespace: 
--

CREATE TABLE taxref_protection_especes (
    cd_nom integer NOT NULL,
    cd_protection character varying(20) NOT NULL,
    nom_cite character varying(200),
    syn_cite character varying(200),
    nom_francais_cite character varying(100),
    precisions text,
    cd_nom_cite character varying(255) NOT NULL
);


ALTER TABLE taxonomie.taxref_protection_especes OWNER TO geonatuser;

--
-- Name: cor_taxon_attribut_pkey; Type: CONSTRAINT; Schema: taxonomie; Owner: geonatuser; Tablespace: 
--

ALTER TABLE ONLY cor_taxon_attribut
    ADD CONSTRAINT cor_taxon_attribut_pkey PRIMARY KEY (id_taxon, id_attribut);


--
-- Name: cor_taxon_liste_pkey; Type: CONSTRAINT; Schema: taxonomie; Owner: geonatuser; Tablespace: 
--

ALTER TABLE ONLY cor_taxon_liste
    ADD CONSTRAINT cor_taxon_liste_pkey PRIMARY KEY (id_taxon, id_liste);


--
-- Name: pk_bib_attributs; Type: CONSTRAINT; Schema: taxonomie; Owner: geonatuser; Tablespace: 
--

ALTER TABLE ONLY bib_attributs
    ADD CONSTRAINT pk_bib_attributs PRIMARY KEY (id_attribut);


--
-- Name: pk_bib_listes; Type: CONSTRAINT; Schema: taxonomie; Owner: geonatuser; Tablespace: 
--

ALTER TABLE ONLY bib_listes
    ADD CONSTRAINT pk_bib_listes PRIMARY KEY (id_liste);


--
-- Name: pk_bib_taxons; Type: CONSTRAINT; Schema: taxonomie; Owner: geonatuser; Tablespace: 
--

ALTER TABLE ONLY bib_taxons
    ADD CONSTRAINT pk_bib_taxons PRIMARY KEY (id_taxon);


--
-- Name: pk_bib_taxref_habitats; Type: CONSTRAINT; Schema: taxonomie; Owner: geonatuser; Tablespace: 
--

ALTER TABLE ONLY bib_taxref_habitats
    ADD CONSTRAINT pk_bib_taxref_habitats PRIMARY KEY (id_habitat);


--
-- Name: pk_bib_taxref_rangs; Type: CONSTRAINT; Schema: taxonomie; Owner: geonatuser; Tablespace: 
--

ALTER TABLE ONLY bib_taxref_rangs
    ADD CONSTRAINT pk_bib_taxref_rangs PRIMARY KEY (id_rang);


--
-- Name: pk_bib_taxref_statuts; Type: CONSTRAINT; Schema: taxonomie; Owner: geonatuser; Tablespace: 
--

ALTER TABLE ONLY bib_taxref_statuts
    ADD CONSTRAINT pk_bib_taxref_statuts PRIMARY KEY (id_statut);


--
-- Name: pk_import_taxref; Type: CONSTRAINT; Schema: taxonomie; Owner: geonatuser; Tablespace: 
--

ALTER TABLE ONLY import_taxref
    ADD CONSTRAINT pk_import_taxref PRIMARY KEY (cd_nom);


--
-- Name: pk_taxref; Type: CONSTRAINT; Schema: taxonomie; Owner: geonatuser; Tablespace: 
--

ALTER TABLE ONLY taxref
    ADD CONSTRAINT pk_taxref PRIMARY KEY (cd_nom);


--
-- Name: pk_taxref_changes; Type: CONSTRAINT; Schema: taxonomie; Owner: geonatuser; Tablespace: 
--

ALTER TABLE ONLY taxref_changes
    ADD CONSTRAINT pk_taxref_changes PRIMARY KEY (cd_nom, champ);


--
-- Name: taxref_protection_articles_pkey; Type: CONSTRAINT; Schema: taxonomie; Owner: geonatuser; Tablespace: 
--

ALTER TABLE ONLY taxref_protection_articles
    ADD CONSTRAINT taxref_protection_articles_pkey PRIMARY KEY (cd_protection);


--
-- Name: taxref_protection_especes_pkey; Type: CONSTRAINT; Schema: taxonomie; Owner: geonatuser; Tablespace: 
--

ALTER TABLE ONLY taxref_protection_especes
    ADD CONSTRAINT taxref_protection_especes_pkey PRIMARY KEY (cd_nom, cd_protection, cd_nom_cite);


--
-- Name: fki_cd_nom_taxref_protection_especes; Type: INDEX; Schema: taxonomie; Owner: geonatuser; Tablespace: 
--

CREATE INDEX fki_cd_nom_taxref_protection_especes ON taxref_protection_especes USING btree (cd_nom);


--
-- Name: fki_cor_taxon_attribut; Type: INDEX; Schema: taxonomie; Owner: geonatuser; Tablespace: 
--

CREATE INDEX fki_cor_taxon_attribut ON cor_taxon_attribut USING btree (valeur_attribut);


--
-- Name: i_fk_bib_taxons_taxr; Type: INDEX; Schema: taxonomie; Owner: geonatuser; Tablespace: 
--

CREATE INDEX i_fk_bib_taxons_taxr ON bib_taxons USING btree (cd_nom);


--
-- Name: i_fk_taxref_bib_taxref_habitat; Type: INDEX; Schema: taxonomie; Owner: geonatuser; Tablespace: 
--

CREATE INDEX i_fk_taxref_bib_taxref_habitat ON taxref USING btree (id_habitat);


--
-- Name: i_fk_taxref_bib_taxref_rangs; Type: INDEX; Schema: taxonomie; Owner: geonatuser; Tablespace: 
--

CREATE INDEX i_fk_taxref_bib_taxref_rangs ON taxref USING btree (id_rang);


--
-- Name: i_fk_taxref_bib_taxref_statuts; Type: INDEX; Schema: taxonomie; Owner: geonatuser; Tablespace: 
--

CREATE INDEX i_fk_taxref_bib_taxref_statuts ON taxref USING btree (id_statut);


--
-- Name: i_taxref_cd_nom; Type: INDEX; Schema: taxonomie; Owner: geonatuser; Tablespace: 
--

CREATE INDEX i_taxref_cd_nom ON taxref USING btree (cd_nom);


--
-- Name: i_taxref_cd_ref; Type: INDEX; Schema: taxonomie; Owner: geonatuser; Tablespace: 
--

CREATE INDEX i_taxref_cd_ref ON taxref USING btree (cd_ref);


--
-- Name: i_taxref_hierarchy; Type: INDEX; Schema: taxonomie; Owner: geonatuser; Tablespace: 
--

CREATE INDEX i_taxref_hierarchy ON taxref USING btree (regne, phylum, classe, ordre, famille);


--
-- Name: cor_taxon_attrib_bib_attrib_fkey; Type: FK CONSTRAINT; Schema: taxonomie; Owner: geonatuser
--

ALTER TABLE ONLY cor_taxon_attribut
    ADD CONSTRAINT cor_taxon_attrib_bib_attrib_fkey FOREIGN KEY (id_attribut) REFERENCES bib_attributs(id_attribut);


--
-- Name: cor_taxon_attrib_bib_taxons_fkey; Type: FK CONSTRAINT; Schema: taxonomie; Owner: geonatuser
--

ALTER TABLE ONLY cor_taxon_attribut
    ADD CONSTRAINT cor_taxon_attrib_bib_taxons_fkey FOREIGN KEY (id_taxon) REFERENCES bib_taxons(id_taxon);


--
-- Name: cor_taxon_listes_bib_listes_fkey; Type: FK CONSTRAINT; Schema: taxonomie; Owner: geonatuser
--

ALTER TABLE ONLY cor_taxon_liste
    ADD CONSTRAINT cor_taxon_listes_bib_listes_fkey FOREIGN KEY (id_liste) REFERENCES bib_listes(id_liste) ON UPDATE CASCADE;


--
-- Name: cor_taxon_listes_bib_taxons_fkey; Type: FK CONSTRAINT; Schema: taxonomie; Owner: geonatuser
--

ALTER TABLE ONLY cor_taxon_liste
    ADD CONSTRAINT cor_taxon_listes_bib_taxons_fkey FOREIGN KEY (id_taxon) REFERENCES bib_taxons(id_taxon);


--
-- Name: fk_bib_taxons_taxref; Type: FK CONSTRAINT; Schema: taxonomie; Owner: geonatuser
--

ALTER TABLE ONLY bib_taxons
    ADD CONSTRAINT fk_bib_taxons_taxref FOREIGN KEY (cd_nom) REFERENCES taxref(cd_nom);


--
-- Name: fk_taxref_bib_taxref_habitats; Type: FK CONSTRAINT; Schema: taxonomie; Owner: geonatuser
--

ALTER TABLE ONLY taxref
    ADD CONSTRAINT fk_taxref_bib_taxref_habitats FOREIGN KEY (id_habitat) REFERENCES bib_taxref_habitats(id_habitat) ON UPDATE CASCADE;


--
-- Name: fk_taxref_bib_taxref_rangs; Type: FK CONSTRAINT; Schema: taxonomie; Owner: geonatuser
--

ALTER TABLE ONLY taxref
    ADD CONSTRAINT fk_taxref_bib_taxref_rangs FOREIGN KEY (id_rang) REFERENCES bib_taxref_rangs(id_rang) ON UPDATE CASCADE;


--
-- Name: taxref_id_statut_fkey; Type: FK CONSTRAINT; Schema: taxonomie; Owner: geonatuser
--

ALTER TABLE ONLY taxref
    ADD CONSTRAINT taxref_id_statut_fkey FOREIGN KEY (id_statut) REFERENCES bib_taxref_statuts(id_statut) ON UPDATE CASCADE;


--
-- Name: taxref_protection_especes_cd_nom_fkey; Type: FK CONSTRAINT; Schema: taxonomie; Owner: geonatuser
--

ALTER TABLE ONLY taxref_protection_especes
    ADD CONSTRAINT taxref_protection_especes_cd_nom_fkey FOREIGN KEY (cd_nom) REFERENCES taxref(cd_nom) ON UPDATE CASCADE;


--
-- Name: taxref_protection_especes_cd_protection_fkey; Type: FK CONSTRAINT; Schema: taxonomie; Owner: geonatuser
--

ALTER TABLE ONLY taxref_protection_especes
    ADD CONSTRAINT taxref_protection_especes_cd_protection_fkey FOREIGN KEY (cd_protection) REFERENCES taxref_protection_articles(cd_protection);


--
-- Name: taxonomie; Type: ACL; Schema: -; Owner: geonatuser
--

REVOKE ALL ON SCHEMA taxonomie FROM PUBLIC;
REVOKE ALL ON SCHEMA taxonomie FROM geonatuser;
GRANT ALL ON SCHEMA taxonomie TO geonatuser;


--
-- Name: bib_attributs; Type: ACL; Schema: taxonomie; Owner: geonatuser
--

REVOKE ALL ON TABLE bib_attributs FROM PUBLIC;
REVOKE ALL ON TABLE bib_attributs FROM geonatuser;
GRANT ALL ON TABLE bib_attributs TO geonatuser;


--
-- Name: bib_listes; Type: ACL; Schema: taxonomie; Owner: geonatuser
--

REVOKE ALL ON TABLE bib_listes FROM PUBLIC;
REVOKE ALL ON TABLE bib_listes FROM geonatuser;
GRANT ALL ON TABLE bib_listes TO geonatuser;


--
-- Name: bib_taxons; Type: ACL; Schema: taxonomie; Owner: geonatuser
--

REVOKE ALL ON TABLE bib_taxons FROM PUBLIC;
REVOKE ALL ON TABLE bib_taxons FROM geonatuser;
GRANT ALL ON TABLE bib_taxons TO geonatuser;


--
-- Name: bib_taxref_habitats; Type: ACL; Schema: taxonomie; Owner: geonatuser
--

REVOKE ALL ON TABLE bib_taxref_habitats FROM PUBLIC;
REVOKE ALL ON TABLE bib_taxref_habitats FROM geonatuser;
GRANT ALL ON TABLE bib_taxref_habitats TO geonatuser;


--
-- Name: bib_taxref_rangs; Type: ACL; Schema: taxonomie; Owner: geonatuser
--

REVOKE ALL ON TABLE bib_taxref_rangs FROM PUBLIC;
REVOKE ALL ON TABLE bib_taxref_rangs FROM geonatuser;
GRANT ALL ON TABLE bib_taxref_rangs TO geonatuser;


--
-- Name: bib_taxref_statuts; Type: ACL; Schema: taxonomie; Owner: geonatuser
--

REVOKE ALL ON TABLE bib_taxref_statuts FROM PUBLIC;
REVOKE ALL ON TABLE bib_taxref_statuts FROM geonatuser;
GRANT ALL ON TABLE bib_taxref_statuts TO geonatuser;


--
-- Name: cor_taxon_attribut; Type: ACL; Schema: taxonomie; Owner: geonatuser
--

REVOKE ALL ON TABLE cor_taxon_attribut FROM PUBLIC;
REVOKE ALL ON TABLE cor_taxon_attribut FROM geonatuser;
GRANT ALL ON TABLE cor_taxon_attribut TO geonatuser;


--
-- Name: cor_taxon_liste; Type: ACL; Schema: taxonomie; Owner: geonatuser
--

REVOKE ALL ON TABLE cor_taxon_liste FROM PUBLIC;
REVOKE ALL ON TABLE cor_taxon_liste FROM geonatuser;
GRANT ALL ON TABLE cor_taxon_liste TO geonatuser;


--
-- Name: import_taxref; Type: ACL; Schema: taxonomie; Owner: geonatuser
--

REVOKE ALL ON TABLE import_taxref FROM PUBLIC;
REVOKE ALL ON TABLE import_taxref FROM geonatuser;
GRANT ALL ON TABLE import_taxref TO geonatuser;
GRANT ALL ON TABLE import_taxref TO postgres;


--
-- Name: taxref; Type: ACL; Schema: taxonomie; Owner: geonatuser
--

REVOKE ALL ON TABLE taxref FROM PUBLIC;
REVOKE ALL ON TABLE taxref FROM geonatuser;
GRANT ALL ON TABLE taxref TO geonatuser;


--
-- Name: taxref_changes; Type: ACL; Schema: taxonomie; Owner: geonatuser
--

REVOKE ALL ON TABLE taxref_changes FROM PUBLIC;
REVOKE ALL ON TABLE taxref_changes FROM geonatuser;
GRANT ALL ON TABLE taxref_changes TO geonatuser;


--
-- Name: taxref_protection_articles; Type: ACL; Schema: taxonomie; Owner: geonatuser
--

REVOKE ALL ON TABLE taxref_protection_articles FROM PUBLIC;
REVOKE ALL ON TABLE taxref_protection_articles FROM geonatuser;
GRANT ALL ON TABLE taxref_protection_articles TO geonatuser;


--
-- Name: taxref_protection_especes; Type: ACL; Schema: taxonomie; Owner: geonatuser
--

REVOKE ALL ON TABLE taxref_protection_especes FROM PUBLIC;
REVOKE ALL ON TABLE taxref_protection_especes FROM geonatuser;
GRANT ALL ON TABLE taxref_protection_especes TO geonatuser;


--
-- PostgreSQL database dump complete
--


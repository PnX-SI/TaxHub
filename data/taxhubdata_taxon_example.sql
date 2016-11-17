--
-- PostgreSQL database dump
--

-- Dumped from database version 9.3.14
-- Dumped by pg_dump version 9.3.14
-- Started on 2016-08-22 10:18:09 CEST

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = taxonomie, pg_catalog;


--
-- Data for Name: bib_noms; Type: TABLE DATA; Schema: taxonomie; Owner: -
--

INSERT INTO bib_noms (id_nom, cd_nom, cd_ref, nom_francais) VALUES (704, 67111, 67111, 'Ablette');
INSERT INTO bib_noms (id_nom, cd_nom, cd_ref, nom_francais) VALUES (64, 60612, 60612, 'Lynx boréal');
INSERT INTO bib_noms (id_nom, cd_nom, cd_ref, nom_francais) VALUES (23, 351, 351, 'Grenouille rousse');
INSERT INTO bib_noms (id_nom, cd_nom, cd_ref, nom_francais) VALUES (1950, 8326, 8326, 'Cicindela hybrida');
INSERT INTO bib_noms (id_nom, cd_nom, cd_ref, nom_francais) VALUES (2804, 11165, 11165, 'Coccinella septempunctata');
INSERT INTO bib_noms (id_nom, cd_nom, cd_ref, nom_francais) VALUES (816, 18437, 18437, 'Ecrevisse à pieds blancs');
INSERT INTO bib_noms (id_nom, cd_nom, cd_ref, nom_francais) VALUES (100001, 81065, 81065, 'Alchémille rampante');
INSERT INTO bib_noms (id_nom, cd_nom, cd_ref, nom_francais) VALUES (100002, 95186, 95186, 'Inule fétide');


--
-- 
-- Data for Name: cor_taxon_attribut; Type: TABLE DATA; Schema: taxonomie; Owner: -
--

INSERT INTO cor_taxon_attribut (cd_ref ,id_attribut, valeur_attribut) VALUES (67111, 1, 'non');
INSERT INTO cor_taxon_attribut (cd_ref ,id_attribut, valeur_attribut) VALUES (67111, 2, 'non');
INSERT INTO cor_taxon_attribut (cd_ref ,id_attribut, valeur_attribut) VALUES (67111, 3, 'oui');
INSERT INTO cor_taxon_attribut (cd_ref ,id_attribut, valeur_attribut) VALUES (60612, 1, 'oui');
INSERT INTO cor_taxon_attribut (cd_ref ,id_attribut, valeur_attribut) VALUES (60612, 2, 'oui');
INSERT INTO cor_taxon_attribut (cd_ref ,id_attribut, valeur_attribut) VALUES (60612, 3, 'oui');
INSERT INTO cor_taxon_attribut (cd_ref ,id_attribut, valeur_attribut) VALUES (351, 1, 'non');
INSERT INTO cor_taxon_attribut (cd_ref ,id_attribut, valeur_attribut) VALUES (351, 2, 'oui');
INSERT INTO cor_taxon_attribut (cd_ref ,id_attribut, valeur_attribut) VALUES (351, 3, 'oui');
INSERT INTO cor_taxon_attribut (cd_ref ,id_attribut, valeur_attribut) VALUES (8326, 1, 'non');
INSERT INTO cor_taxon_attribut (cd_ref ,id_attribut, valeur_attribut) VALUES (8326, 2, 'non');
INSERT INTO cor_taxon_attribut (cd_ref ,id_attribut, valeur_attribut) VALUES (8326, 3, 'oui');
INSERT INTO cor_taxon_attribut (cd_ref ,id_attribut, valeur_attribut) VALUES (11165, 1, 'non');
INSERT INTO cor_taxon_attribut (cd_ref ,id_attribut, valeur_attribut) VALUES (11165, 2, 'non');
INSERT INTO cor_taxon_attribut (cd_ref ,id_attribut, valeur_attribut) VALUES (11165, 3, 'oui');
INSERT INTO cor_taxon_attribut (cd_ref ,id_attribut, valeur_attribut) VALUES (18437, 1, 'non');
INSERT INTO cor_taxon_attribut (cd_ref ,id_attribut, valeur_attribut) VALUES (18437, 2, 'oui');
INSERT INTO cor_taxon_attribut (cd_ref ,id_attribut, valeur_attribut) VALUES (18437, 3, 'oui');
INSERT INTO cor_taxon_attribut (cd_ref ,id_attribut, valeur_attribut) VALUES (81065, 1, 'non');
INSERT INTO cor_taxon_attribut (cd_ref ,id_attribut, valeur_attribut) VALUES (81065, 2, 'non');
INSERT INTO cor_taxon_attribut (cd_ref ,id_attribut, valeur_attribut) VALUES (81065, 3, 'oui');
INSERT INTO cor_taxon_attribut (cd_ref ,id_attribut, valeur_attribut) VALUES (95186, 1, 'non');
INSERT INTO cor_taxon_attribut (cd_ref ,id_attribut, valeur_attribut) VALUES (95186, 2, 'non');
INSERT INTO cor_taxon_attribut (cd_ref ,id_attribut, valeur_attribut) VALUES (95186, 3, 'oui');


--
-- 
-- Data for Name: cor_nom_liste; Type: TABLE DATA; Schema: taxonomie; Owner: -
--

INSERT INTO cor_nom_liste (id_nom ,id_liste) VALUES (704, 1001);
INSERT INTO cor_nom_liste (id_nom ,id_liste) VALUES (64, 1001);
INSERT INTO cor_nom_liste (id_nom ,id_liste) VALUES (23, 1001);
INSERT INTO cor_nom_liste (id_nom ,id_liste) VALUES (1950, 1002);
INSERT INTO cor_nom_liste (id_nom ,id_liste) VALUES (2804, 1002);
INSERT INTO cor_nom_liste (id_nom ,id_liste) VALUES (816, 1002);
INSERT INTO cor_nom_liste (id_nom ,id_liste) VALUES (23, 1);
INSERT INTO cor_nom_liste (id_nom ,id_liste) VALUES (64, 11);
INSERT INTO cor_nom_liste (id_nom ,id_liste) VALUES (704, 13);
INSERT INTO cor_nom_liste (id_nom ,id_liste) VALUES (816, 5);
INSERT INTO cor_nom_liste (id_nom ,id_liste) VALUES (1950, 9);
INSERT INTO cor_nom_liste (id_nom ,id_liste) VALUES (2804,9);
INSERT INTO cor_nom_liste (id_nom ,id_liste) VALUES (100001,1003);
INSERT INTO cor_nom_liste (id_nom ,id_liste) VALUES (100002,1003);
INSERT INTO cor_nom_liste (id_nom ,id_liste) VALUES (100001,306);
INSERT INTO cor_nom_liste (id_nom ,id_liste) VALUES (100002,307);

--
-- PostgreSQL database dump
--

-- Dumped from database version 9.3.14
-- Dumped by pg_dump version 9.3.14
-- Started on 2016-08-22 10:18:09 CEST
-- Données insérées pour GeoNature-atlas

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = taxonomie, pg_catalog;

--
-- TOC entry 3457 (class 0 OID 194361)
-- Dependencies: 253
-- Data for Name: bib_themes; Type: TABLE DATA; Schema: taxonomie; Owner: dbadmin
--

INSERT INTO bib_themes (id_theme, nom_theme, desc_theme, ordre, id_droit) VALUES (2, 'Atlas', 'Informations relatives à GeoNature-atlas', 2, 3);

--
-- TOC entry 3463 (class 0 OID 0)
-- Dependencies: 252
-- Name: bib_themes_id_theme_seq; Type: SEQUENCE SET; Schema: taxonomie; Owner: dbadmin
--

SELECT pg_catalog.setval('bib_themes_id_theme_seq', 3, true);

--
--
-- Data for Name: bib_attributs; Type: TABLE DATA; Schema: taxonomie; Owner: -
--

INSERT INTO bib_attributs (id_attribut, nom_attribut, label_attribut, liste_valeur_attribut, obligatoire, desc_attribut, type_attribut, type_widget, regne, group2_inpn, id_theme, ordre) VALUES (100, 'atlas_description', 'Description', '{}', false, 'Donne une description du taxon pour l''atlas', 'text', 'textarea', NULL, NULL, 2, 100);
INSERT INTO bib_attributs (id_attribut, nom_attribut, label_attribut, liste_valeur_attribut, obligatoire, desc_attribut, type_attribut, type_widget, regne, group2_inpn, id_theme, ordre) VALUES (101, 'atlas_commentaire', 'Commentaire', '{}', false, 'Commentaire contextualisé sur le taxon pour GeoNature-Atlas', 'text', 'textarea', NULL, NULL, 2, 101);
INSERT INTO bib_attributs (id_attribut, nom_attribut, label_attribut, liste_valeur_attribut, obligatoire, desc_attribut, type_attribut, type_widget, regne, group2_inpn, id_theme, ordre) VALUES (102, 'atlas_milieu', 'Milieu', '{"values":["Forêt","Prairie","eau"]}', false, 'Habitat, milieu principal du taxon', 'text', 'multiselect', NULL, NULL, 2, 102);
INSERT INTO bib_attributs (id_attribut, nom_attribut, label_attribut, liste_valeur_attribut, obligatoire, desc_attribut, type_attribut, type_widget, regne, group2_inpn, id_theme, ordre) VALUES (103, 'atlas_chorologie', 'Chorologie', '{"values":["Méditéranéenne","Alpine","Océanique"]}', false, 'Distribution, répartition, région à grande échelle du taxon', 'text', 'select', NULL, NULL, 2, 103);

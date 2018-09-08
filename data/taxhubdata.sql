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
-- TOC entry 3457 (class 0 OID 194361)
-- Dependencies: 253
-- Data for Name: bib_themes; Type: TABLE DATA; Schema: taxonomie; Owner: dbadmin
--

INSERT INTO bib_themes (id_theme, nom_theme, desc_theme, ordre, id_droit) VALUES (3, 'Mon territoire', 'Informations relatives à mon territoire', 3, 4);

--
-- TOC entry 3463 (class 0 OID 0)
-- Dependencies: 252
-- Name: bib_themes_id_theme_seq; Type: SEQUENCE SET; Schema: taxonomie; Owner: dbadmin
--

SELECT pg_catalog.setval('bib_themes_id_theme_seq', 4, true);

--
--
-- Data for Name: bib_attributs; Type: TABLE DATA; Schema: taxonomie; Owner: -
--

INSERT INTO bib_attributs (id_attribut, nom_attribut, label_attribut, liste_valeur_attribut, obligatoire, desc_attribut, type_attribut, type_widget, regne, group2_inpn, id_theme, ordre) VALUES (4, 'migrateur', 'Migrateur', '{"values":["migrateur","migrateur partiel","sédentaire"]}', false, 'Défini le statut de migration pour le territoire', 'varchar(50)', 'select', 'Animalia', 'Oiseaux', 3, 200);

--
--
-- Data for Name: bib_listes; Type: TABLE DATA; Schema: taxonomie; Owner: -

INSERT INTO bib_listes (id_liste, nom_liste,desc_liste,picto) VALUES(500,'Saisie Occtax','Liste des noms dont la saisie est proposée dans le module Occtax','images/pictos/nopicto.gif');

--
-- TOC entry 3458 (class 0 OID 239030)
-- Dependencies: 260
-- Data for Name: bib_types_media; Type: TABLE DATA; Schema: taxonomie; Owner: dbadmin
--

INSERT INTO bib_types_media (id_type, nom_type_media, desc_type_media) VALUES (1, 'Photo_principale', 'Photo principale du taxon à utiliser pour les vignettes par exemple');
INSERT INTO bib_types_media (id_type, nom_type_media, desc_type_media) VALUES (2, 'Photo', 'Autres photos du taxon');
INSERT INTO bib_types_media (id_type, nom_type_media, desc_type_media) VALUES (3, 'Page web', 'URL d''une page web');
INSERT INTO bib_types_media (id_type, nom_type_media, desc_type_media) VALUES (4, 'PDF', 'Document de type PDF');
INSERT INTO bib_types_media (id_type, nom_type_media, desc_type_media) VALUES (5, 'Audio', 'Fichier audio MP3');
INSERT INTO bib_types_media (id_type, nom_type_media, desc_type_media) VALUES (6, 'Video (fichier)', 'Fichier video hébergé');
INSERT INTO bib_types_media (id_type, nom_type_media, desc_type_media) VALUES (7, 'Video Youtube', 'ID d''une video hébergée sur Youtube');
INSERT INTO bib_types_media (id_type, nom_type_media, desc_type_media) VALUES (8, 'Video Dailymotion', 'ID d''une video hébergée sur Dailymotion');
INSERT INTO bib_types_media (id_type, nom_type_media, desc_type_media) VALUES (9, 'Video Vimeo', 'ID d''une video hébergée sur Vimeo');

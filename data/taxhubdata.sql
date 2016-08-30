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
INSERT INTO bib_themes (id_theme, nom_theme, desc_theme, ordre, id_droit) VALUES (1, 'General', 'Information général concernant les taxons', 1, 4);
INSERT INTO bib_themes (id_theme, nom_theme, desc_theme, ordre, id_droit) VALUES (2, 'Atlas', NULL, 2, 3);

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
INSERT INTO bib_attributs (id_attribut ,nom_attribut, label_attribut, liste_valeur_attribut, obligatoire, desc_attribut, type_attribut, type_widget, id_theme, ordre, regne, group2_inpn) VALUES (2, 'protection_stricte', 'Protégé', '{"values":["oui", "non"]}',true,'Défini si le taxon bénéficie d''une protection juridique stricte pour le territoire', 'text', 'radio', 1, 2, null, null);
INSERT INTO bib_attributs (id_attribut, nom_attribut, label_attribut, liste_valeur_attribut, obligatoire, desc_attribut, type_attribut, type_widget, regne, group2_inpn, id_theme, ordre) VALUES (1, 'patrimonial', 'Patrimonial', '{"values":["oui", "non"]}', false, 'Défini si le taxon est patrimonial pour le territoire', 'text', 'radio', 'Animalia', NULL, 1, NULL);
INSERT INTO bib_attributs (id_attribut, nom_attribut, label_attribut, liste_valeur_attribut, obligatoire, desc_attribut, type_attribut, type_widget, regne, group2_inpn, id_theme, ordre) VALUES (3, 'migrateur', 'Migrateur', '{"values":["migrateur","migrateur partiel","sédentaire"]}', false, 'Défini le statut de migration pour le territoire', 'varchar(50)', 'select', 'Animalia', 'Oiseaux', 1, NULL);

INSERT INTO bib_attributs (id_attribut, nom_attribut, label_attribut, liste_valeur_attribut, obligatoire, desc_attribut, type_attribut, type_widget, regne, group2_inpn, id_theme, ordre) VALUES (100, 'atlas_description', 'Description', '{}', false, 'Donne une description du taxon pour l''atlas', 'text', 'textarea', NULL, NULL, 2, 100);
INSERT INTO bib_attributs (id_attribut, nom_attribut, label_attribut, liste_valeur_attribut, obligatoire, desc_attribut, type_attribut, type_widget, regne, group2_inpn, id_theme, ordre) VALUES (101, 'atlas_commentaire', 'Commentaire', '{}', false, 'Commentaire contextualisé sur le taxon pour GeoNature-atlas', 'text', 'textarea', NULL, NULL, 2, 101);
INSERT INTO bib_attributs (id_attribut, nom_attribut, label_attribut, liste_valeur_attribut, obligatoire, desc_attribut, type_attribut, type_widget, regne, group2_inpn, id_theme, ordre) VALUES (102, 'atlas_milieu', 'Milieu', '{"values":["Landes","Milieux humides","Alpages"]}', false, 'Habitat, milieu principal du taxon', 'text', 'select', NULL, NULL, 2, 102);
INSERT INTO bib_attributs (id_attribut, nom_attribut, label_attribut, liste_valeur_attribut, obligatoire, desc_attribut, type_attribut, type_widget, regne, group2_inpn, id_theme, ordre) VALUES (103, 'atlas_corologie', 'Chorologie', '{"values":["Méditéranéenne","Alpine","Océanique"]}', false, 'Distribution, répartition, région à grande échelle du taxon', 'text', 'multiselect', NULL, NULL, 2, 103);

--
-- 
-- Data for Name: bib_listes; Type: TABLE DATA; Schema: taxonomie; Owner: -
--

INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto,regne,group2_inpn) VALUES (1, 'Amphibiens',null, 'images/pictos/amphibien.gif','Animalia','Amphibiens');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto,regne,group2_inpn) VALUES (2, 'Vers',null, 'images/pictos/nopicto.gif','Animalia','Annélides');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto,regne,group2_inpn) VALUES (3, 'Entognathes',null, 'images/pictos/nopicto.gif','Animalia','Entognathes');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto,regne,group2_inpn) VALUES (4, 'Echinodermes',null, 'images/pictos/nopicto.gif','Animalia','<Autres>');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto,regne,group2_inpn) VALUES (5, 'Crustacés',null, 'images/pictos/ecrevisse.gif','Animalia','Crustacés');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto,regne,group2_inpn) VALUES (7, 'Pycnogonides',null, 'images/pictos/nopicto.gif','Animalia','Pycnogonides');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto,regne,group2_inpn) VALUES (8, 'Gastéropodes',null, 'images/pictos/nopicto.gif','Animalia','Gastéropodes');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto,regne,group2_inpn) VALUES (9, 'Insectes',null, 'images/pictos/insecte.gif','Animalia','Insectes');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto,regne,group2_inpn) VALUES (10, 'Bivalves',null, 'images/pictos/nopicto.gif','Animalia','Bivalves');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto,regne,group2_inpn) VALUES (11, 'Mammifères',null, 'images/pictos/mammifere.gif','Animalia','Mammifères');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto,regne,group2_inpn) VALUES (12, 'Oiseaux',null, 'images/pictos/oiseau.gif','Animalia','Oiseaux');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto,regne,group2_inpn) VALUES (13, 'Poissons',null, 'images/pictos/poisson.gif','Animalia','Poissons' );
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto,regne,group2_inpn) VALUES (14, 'Reptiles',null, 'images/pictos/reptile.gif','Animalia','Reptiles');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto,regne,group2_inpn) VALUES (15, 'Myriapodes',null, 'images/pictos/nopicto.gif','Animalia','Myriapodes');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto,regne,group2_inpn) VALUES (16, 'Arachnides',null, 'images/pictos/araignee.gif','Animalia','Arachnides');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto,regne,group2_inpn) VALUES (20, 'Rotifères',null, 'images/pictos/nopicto.gif','Animalia','<Autres>');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto,regne,group2_inpn) VALUES (21, 'Tardigrades',null, 'images/pictos/nopicto.gif','Animalia','<Autres>');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto,regne,group2_inpn) VALUES (101, 'Mollusques',null, 'images/pictos/mollusque.gif','Animalia','<Autres>');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto,regne,group2_inpn) VALUES (301, 'Bryophytes',null, 'images/pictos/mousse.gif','Plantae','Mousses');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto,regne,group2_inpn) VALUES (302, 'Lichens',null, 'images/pictos/nopicto.gif','Plantae','Lichens');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto,regne,group2_inpn) VALUES (303, 'Algues',null, 'images/pictos/nopicto.gif','Plantae','Algues');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto,regne,group2_inpn) VALUES (305, 'Ptéridophytes',null, 'images/pictos/nopicto.gif','Plantae','Angiospermes');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto,regne,group2_inpn) VALUES (306, 'Monocotylédones',null, 'images/pictos/nopicto.gif','Plantae','Angiospermes');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto,regne,group2_inpn) VALUES (307, 'Dycotylédones',null, 'images/pictos/nopicto.gif','Plantae','Angiospermes');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto) VALUES (666, 'Nuisibles',null, 'images/pictos/nopicto.gif');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto,regne) VALUES (1001, 'Faune vertébrée', 'Liste servant à l''affichage des taxons de la faune vertébré pouvant être saisis', 'images/pictos/nopicto.gif','Animalia');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto,regne) VALUES (1002, 'Faune invertébrée', 'Liste servant à l''affichage des taxons de la faune invertébré pouvant être saisis', 'images/pictos/nopicto.gif','Animalia');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto,regne) VALUES (1003, 'Flore', 'Liste servant à l''affichage des taxons de la flore pouvant être saisis', 'images/pictos/nopicto.gif','Plantae');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto,regne) VALUES (1004, 'Fonge','Liste servant à l''affichage des taxons de la fonge pouvant être saisis', 'images/pictos/champignon.gif','Fungi');

--
-- TOC entry 3458 (class 0 OID 239030)
-- Dependencies: 260
-- Data for Name: bib_types_media; Type: TABLE DATA; Schema: taxonomie; Owner: dbadmin
--

INSERT INTO bib_types_media (id_type, nom_type_media, desc_type_media) VALUES (1, 'Photo_principale', 'Photo principale du taxon à utiliser pour les vignettes par exemple');
INSERT INTO bib_types_media (id_type, nom_type_media, desc_type_media) VALUES (2, 'Photo', 'Autres photos du taxon');


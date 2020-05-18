-- Données insérées pour GeoNature V1

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = taxonomie, pg_catalog;

-- Insertion du thème permettant de regrouper les attributs nécessaires au fonctionnement de GeoNature V1
INSERT INTO bib_themes (nom_theme, desc_theme, ordre, id_droit) 
     VALUES ('GeoNature V1', 'Informations nécessaires au fonctionnement de GeoNature V1', 3, 4);
SELECT setval('taxonomie.bib_themes_id_theme_seq', (SELECT max(id_theme)+1 FROM taxonomie.bib_themes), true);

-- Insertion des 2 attributs nécessaires au fonctionnement de GeoNature V1
INSERT INTO bib_attributs (id_attribut, nom_attribut, label_attribut, liste_valeur_attribut, obligatoire, desc_attribut, type_attribut, type_widget, regne, group2_inpn, id_theme, ordre) 
     VALUES (1, 'patrimonial', 'Patrimonial', '{"values":["oui", "non"]}', false, 'Défini si le taxon est patrimonial pour le territoire', 'text', 'radio', NULL, NULL, (SELECT max(id_theme) FROM taxonomie.bib_themes), 2);
INSERT INTO bib_attributs (id_attribut ,nom_attribut, label_attribut, liste_valeur_attribut, obligatoire, desc_attribut, type_attribut, type_widget, regne, group2_inpn, id_theme, ordre) 
     VALUES (2, 'protection_stricte', 'Protégé', '{"values":["oui", "non"]}',true,'Défini si le taxon bénéficie d''une protection juridique stricte pour le territoire', 'text', 'radio', NULL, NULL, (SELECT max(id_theme) FROM taxonomie.bib_themes), 3);
SELECT setval('taxonomie.bib_attributs_id_attribut_seq', (SELECT max(id_attribut)+1 FROM taxonomie.bib_attributs), true);

-- Insertion des listes de noms nécessaires au fonctionnement de GeoNature V1
INSERT INTO bib_listes (id_liste,nom_liste,desc_liste,picto,regne,group2_inpn) VALUES (1, 'Amphibiens',null, 'images/pictos/amphibien.gif','Animalia','Amphibiens');
INSERT INTO bib_listes (id_liste,nom_liste,desc_liste,picto,regne,group2_inpn) VALUES (2, 'Vers',null, 'images/pictos/nopicto.gif','Animalia','Annélides');
INSERT INTO bib_listes (id_liste,nom_liste,desc_liste,picto,regne,group2_inpn) VALUES (3, 'Entognathes',null, 'images/pictos/nopicto.gif','Animalia','Entognathes');
INSERT INTO bib_listes (id_liste,nom_liste,desc_liste,picto,regne,group2_inpn) VALUES (4, 'Echinodermes',null, 'images/pictos/nopicto.gif','Animalia','<Autres>');
INSERT INTO bib_listes (id_liste,nom_liste,desc_liste,picto,regne,group2_inpn) VALUES (5, 'Crustacés',null, 'images/pictos/ecrevisse.gif','Animalia','Crustacés');
INSERT INTO bib_listes (id_liste,nom_liste,desc_liste,picto,regne,group2_inpn) VALUES (7, 'Pycnogonides',null, 'images/pictos/nopicto.gif','Animalia','Pycnogonides');
INSERT INTO bib_listes (id_liste,nom_liste,desc_liste,picto,regne,group2_inpn) VALUES (8, 'Gastéropodes',null, 'images/pictos/nopicto.gif','Animalia','Gastéropodes');
INSERT INTO bib_listes (id_liste,nom_liste,desc_liste,picto,regne,group2_inpn) VALUES (9, 'Insectes',null, 'images/pictos/insecte.gif','Animalia','Insectes');
INSERT INTO bib_listes (id_liste,nom_liste,desc_liste,picto,regne,group2_inpn) VALUES (10, 'Bivalves',null, 'images/pictos/nopicto.gif','Animalia','Bivalves');
INSERT INTO bib_listes (id_liste,nom_liste,desc_liste,picto,regne,group2_inpn) VALUES (11, 'Mammifères',null, 'images/pictos/mammifere.gif','Animalia','Mammifères');
INSERT INTO bib_listes (id_liste,nom_liste,desc_liste,picto,regne,group2_inpn) VALUES (12, 'Oiseaux',null, 'images/pictos/oiseau.gif','Animalia','Oiseaux');
INSERT INTO bib_listes (id_liste,nom_liste,desc_liste,picto,regne,group2_inpn) VALUES (13, 'Poissons',null, 'images/pictos/poisson.gif','Animalia','Poissons' );
INSERT INTO bib_listes (id_liste,nom_liste,desc_liste,picto,regne,group2_inpn) VALUES (14, 'Reptiles',null, 'images/pictos/reptile.gif','Animalia','Reptiles');
INSERT INTO bib_listes (id_liste,nom_liste,desc_liste,picto,regne,group2_inpn) VALUES (15, 'Myriapodes',null, 'images/pictos/nopicto.gif','Animalia','Myriapodes');
INSERT INTO bib_listes (id_liste,nom_liste,desc_liste,picto,regne,group2_inpn) VALUES (16, 'Arachnides',null, 'images/pictos/araignee.gif','Animalia','Arachnides');
INSERT INTO bib_listes (id_liste,nom_liste,desc_liste,picto,regne,group2_inpn) VALUES (20, 'Rotifères',null, 'images/pictos/nopicto.gif','Animalia','<Autres>');
INSERT INTO bib_listes (id_liste,nom_liste,desc_liste,picto,regne,group2_inpn) VALUES (21, 'Tardigrades',null, 'images/pictos/nopicto.gif','Animalia','<Autres>');
INSERT INTO bib_listes (id_liste,nom_liste,desc_liste,picto,regne,group2_inpn) VALUES (101, 'Mollusques',null, 'images/pictos/mollusque.gif','Animalia','<Autres>');
INSERT INTO bib_listes (id_liste,nom_liste,desc_liste,picto,regne,group2_inpn) VALUES (301, 'Bryophytes',null, 'images/pictos/mousse.gif','Plantae','Mousses');
INSERT INTO bib_listes (id_liste,nom_liste,desc_liste,picto,regne,group2_inpn) VALUES (302, 'Lichens',null, 'images/pictos/nopicto.gif','Plantae','Lichens');
INSERT INTO bib_listes (id_liste,nom_liste,desc_liste,picto,regne,group2_inpn) VALUES (303, 'Algues',null, 'images/pictos/nopicto.gif','Plantae','Algues');
INSERT INTO bib_listes (id_liste,nom_liste,desc_liste,picto,regne,group2_inpn) VALUES (305, 'Ptéridophytes',null, 'images/pictos/nopicto.gif','Plantae','Fougères');
INSERT INTO bib_listes (id_liste,nom_liste,desc_liste,picto,regne,group2_inpn) VALUES (306, 'Monocotylédones',null, 'images/pictos/nopicto.gif','Plantae','Angiospermes');
INSERT INTO bib_listes (id_liste,nom_liste,desc_liste,picto,regne,group2_inpn) VALUES (307, 'Dycotylédones',null, 'images/pictos/nopicto.gif','Plantae','Angiospermes');
INSERT INTO bib_listes (id_liste,nom_liste,desc_liste,picto,regne,group2_inpn) VALUES (308, 'Gymnospermes',null, 'images/pictos/nopicto.gif','Plantae','Gymnospermes');
INSERT INTO bib_listes (id_liste,nom_liste,desc_liste,picto,regne) VALUES (1001, 'Faune vertébrée', 'Liste servant à l''affichage des taxons de la faune vertébré pouvant être saisis', 'images/pictos/nopicto.gif','Animalia');
INSERT INTO bib_listes (id_liste,nom_liste,desc_liste,picto,regne) VALUES (1002, 'Faune invertébrée', 'Liste servant à l''affichage des taxons de la faune invertébré pouvant être saisis', 'images/pictos/nopicto.gif','Animalia');
INSERT INTO bib_listes (id_liste,nom_liste,desc_liste,picto,regne) VALUES (1003, 'Flore', 'Liste servant à l''affichage des taxons de la flore pouvant être saisis', 'images/pictos/nopicto.gif','Plantae');
INSERT INTO bib_listes (id_liste,nom_liste,desc_liste,picto,regne) VALUES (1004, 'Fonge','Liste servant à l''affichage des taxons de la fonge pouvant être saisis', 'images/pictos/champignon.gif','Fungi');

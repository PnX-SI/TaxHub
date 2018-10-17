-- Données insérées pour GeoNature-atlas

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = taxonomie, pg_catalog;

-- Insertion du thème regroupant les attributs utilisés par GeoNature-atlas
INSERT INTO bib_themes (nom_theme, desc_theme, ordre, id_droit) 
VALUES ('Atlas', 'Informations relatives à GeoNature-atlas', 2, 3);

-- Insertion des attributs utilisés par GeoNature-atlas
INSERT INTO bib_attributs (id_attribut, nom_attribut, label_attribut, liste_valeur_attribut, obligatoire, desc_attribut, type_attribut, type_widget, regne, group2_inpn, id_theme, ordre) VALUES (100, 'atlas_description', 'Description', '{}', false, 'Donne une description du taxon pour l''atlas', 'text', 'textarea', NULL, NULL, (SELECT max(id_theme) FROM taxonomie.bib_themes), 1);
INSERT INTO bib_attributs (id_attribut, nom_attribut, label_attribut, liste_valeur_attribut, obligatoire, desc_attribut, type_attribut, type_widget, regne, group2_inpn, id_theme, ordre) VALUES (101, 'atlas_commentaire', 'Commentaire', '{}', false, 'Commentaire contextualisé sur le taxon pour GeoNature-Atlas', 'text', 'textarea', NULL, NULL, (SELECT max(id_theme) FROM taxonomie.bib_themes), 2);
INSERT INTO bib_attributs (id_attribut, nom_attribut, label_attribut, liste_valeur_attribut, obligatoire, desc_attribut, type_attribut, type_widget, regne, group2_inpn, id_theme, ordre) VALUES (102, 'atlas_milieu', 'Milieu', '{"values":["Forêt","Prairie","eau"]}', false, 'Habitat, milieu principal du taxon', 'text', 'multiselect', NULL, NULL, (SELECT max(id_theme) FROM taxonomie.bib_themes), 3);
INSERT INTO bib_attributs (id_attribut, nom_attribut, label_attribut, liste_valeur_attribut, obligatoire, desc_attribut, type_attribut, type_widget, regne, group2_inpn, id_theme, ordre) VALUES (103, 'atlas_chorologie', 'Chorologie', '{"values":["Méditéranéenne","Alpine","Océanique"]}', false, 'Distribution, répartition, région à grande échelle du taxon', 'text', 'select', NULL, NULL, (SELECT max(id_theme) FROM taxonomie.bib_themes), 4);
SELECT setval('taxonomie.bib_attributs_id_attribut_seq', (SELECT max(id_attribut)+1 FROM taxonomie.bib_attributs), true);

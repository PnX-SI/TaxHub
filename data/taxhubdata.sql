SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = taxonomie, pg_catalog;

-- Insertion d'un thème d'exemple permettant de gérer les attributs et informations taxonomiques spécifiques à un territoire
INSERT INTO bib_themes (id_theme, nom_theme, desc_theme, ordre, id_droit) 
    VALUES (1, 'Mon territoire', 'Informations relatives à mon territoire', 1, 4);
SELECT setval('taxonomie.bib_themes_id_theme_seq', (SELECT max(id_theme)+1 FROM taxonomie.bib_themes), true);

-- Insertion d'une liste permettant de définir les noms pouvant être saisis dans le module Occtax
INSERT INTO bib_listes (id_liste, nom_liste,desc_liste,picto) 
    VALUES (100,'Saisie Occtax','Liste des noms dont la saisie est proposée dans le module Occtax','images/pictos/nopicto.gif');

-- Insertion des types de média associables aux taxons
INSERT INTO bib_types_media (id_type, nom_type_media, desc_type_media) VALUES (1, 'Photo_principale', 'Photo principale du taxon à utiliser pour les vignettes par exemple');
INSERT INTO bib_types_media (id_type, nom_type_media, desc_type_media) VALUES (2, 'Photo', 'Autres photos du taxon');
INSERT INTO bib_types_media (id_type, nom_type_media, desc_type_media) VALUES (3, 'Page web', 'URL d''une page web');
INSERT INTO bib_types_media (id_type, nom_type_media, desc_type_media) VALUES (4, 'PDF', 'Document de type PDF');
INSERT INTO bib_types_media (id_type, nom_type_media, desc_type_media) VALUES (5, 'Audio', 'Fichier audio MP3');
INSERT INTO bib_types_media (id_type, nom_type_media, desc_type_media) VALUES (6, 'Video (fichier)', 'Fichier video hébergé');
INSERT INTO bib_types_media (id_type, nom_type_media, desc_type_media) VALUES (7, 'Video Youtube', 'ID d''une video hébergée sur Youtube');
INSERT INTO bib_types_media (id_type, nom_type_media, desc_type_media) VALUES (8, 'Video Dailymotion', 'ID d''une video hébergée sur Dailymotion');
INSERT INTO bib_types_media (id_type, nom_type_media, desc_type_media) VALUES (9, 'Video Vimeo', 'ID d''une video hébergée sur Vimeo');

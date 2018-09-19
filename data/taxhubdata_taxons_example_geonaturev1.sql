SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = taxonomie, pg_catalog;

-- Ajout des 8 taxons exemple aux listes nécéessaires à GeoNature V1
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
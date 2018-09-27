SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = taxonomie, pg_catalog;

-- Ajout des 8 taxons exemple aux listes nécéessaires à GeoNature V1
INSERT INTO cor_nom_liste (id_nom ,id_liste) VALUES ((SELECT id_nom FROM bib_noms WHERE nom_francais = 'Ablette'), 1001);
INSERT INTO cor_nom_liste (id_nom ,id_liste) VALUES ((SELECT id_nom FROM bib_noms WHERE nom_francais = 'Lynx boréal'), 1001);
INSERT INTO cor_nom_liste (id_nom ,id_liste) VALUES ((SELECT id_nom FROM bib_noms WHERE nom_francais = 'Grenouille rousse'), 1001);
INSERT INTO cor_nom_liste (id_nom ,id_liste) VALUES ((SELECT id_nom FROM bib_noms WHERE nom_francais = 'Cicindela hybrida'), 1002);
INSERT INTO cor_nom_liste (id_nom ,id_liste) VALUES ((SELECT id_nom FROM bib_noms WHERE nom_francais = 'Coccinella septempunctata', 1002);
INSERT INTO cor_nom_liste (id_nom ,id_liste) VALUES ((SELECT id_nom FROM bib_noms WHERE nom_francais = 'Ecrevisse à pieds blancs'), 1002);
INSERT INTO cor_nom_liste (id_nom ,id_liste) VALUES ((SELECT id_nom FROM bib_noms WHERE nom_francais = 'Lynx boréal'), 1);
INSERT INTO cor_nom_liste (id_nom ,id_liste) VALUES ((SELECT id_nom FROM bib_noms WHERE nom_francais = 'Grenouille rousse'), 11);
INSERT INTO cor_nom_liste (id_nom ,id_liste) VALUES ((SELECT id_nom FROM bib_noms WHERE nom_francais = 'Ablette'), 13);
INSERT INTO cor_nom_liste (id_nom ,id_liste) VALUES ((SELECT id_nom FROM bib_noms WHERE nom_francais = 'Ecrevisse à pieds blancs'), 5);
INSERT INTO cor_nom_liste (id_nom ,id_liste) VALUES ((SELECT id_nom FROM bib_noms WHERE nom_francais = 'Cicindela hybrida'), 9);
INSERT INTO cor_nom_liste (id_nom ,id_liste) VALUES ((SELECT id_nom FROM bib_noms WHERE nom_francais = 'Coccinella septempunctata'),9);
INSERT INTO cor_nom_liste (id_nom ,id_liste) VALUES ((SELECT id_nom FROM bib_noms WHERE nom_francais = 'Alchémille rampante'),1003);
INSERT INTO cor_nom_liste (id_nom ,id_liste) VALUES ((SELECT id_nom FROM bib_noms WHERE nom_francais = 'Inule fétide'),1003);
INSERT INTO cor_nom_liste (id_nom ,id_liste) VALUES ((SELECT id_nom FROM bib_noms WHERE nom_francais = 'Alchémille rampante'),306);
INSERT INTO cor_nom_liste (id_nom ,id_liste) VALUES ((SELECT id_nom FROM bib_noms WHERE nom_francais = 'Inule fétide'),307);
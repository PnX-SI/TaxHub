SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = taxonomie, pg_catalog;

-- Insertion de 8 noms d'exemple dans bib_noms (les taxons de mon territoire)
INSERT INTO bib_noms (id_nom, cd_nom, cd_ref, nom_francais) VALUES (704, 67111, 67111, 'Ablette');
INSERT INTO bib_noms (id_nom, cd_nom, cd_ref, nom_francais) VALUES (64, 60612, 60612, 'Lynx boréal');
INSERT INTO bib_noms (id_nom, cd_nom, cd_ref, nom_francais) VALUES (23, 351, 351, 'Grenouille rousse');
INSERT INTO bib_noms (id_nom, cd_nom, cd_ref, nom_francais) VALUES (1950, 8326, 8326, 'Cicindela hybrida');
INSERT INTO bib_noms (id_nom, cd_nom, cd_ref, nom_francais) VALUES (2804, 11165, 11165, 'Coccinella septempunctata');
INSERT INTO bib_noms (id_nom, cd_nom, cd_ref, nom_francais) VALUES (816, 18437, 18437, 'Ecrevisse à pieds blancs');
INSERT INTO bib_noms (id_nom, cd_nom, cd_ref, nom_francais) VALUES (100001, 81065, 81065, 'Alchémille rampante');
INSERT INTO bib_noms (id_nom, cd_nom, cd_ref, nom_francais) VALUES (100002, 95186, 95186, 'Inule fétide');

-- Ajout de ces 8 noms à la liste "Saisie Occtax" pour pouvoir les saisir dans ce module de GeoNature
INSERT INTO cor_nom_liste (id_nom, id_liste) VALUES (704, 100);
INSERT INTO cor_nom_liste (id_nom, id_liste) VALUES (64, 100);
INSERT INTO cor_nom_liste (id_nom, id_liste) VALUES (23, 100);
INSERT INTO cor_nom_liste (id_nom, id_liste) VALUES (1950, 100);
INSERT INTO cor_nom_liste (id_nom, id_liste) VALUES (2804, 100);
INSERT INTO cor_nom_liste (id_nom, id_liste) VALUES (816, 100);
INSERT INTO cor_nom_liste (id_nom, id_liste) VALUES (100001, 100);
INSERT INTO cor_nom_liste (id_nom, id_liste) VALUES (100002, 100);
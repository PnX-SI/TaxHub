-- Insertion d'exemple de taxons dans TaxHub en version 1.8.1
-- A partir de la version 1.9.0, les évolutions de la BDD sont gérées dans des migrations Alembic

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = taxonomie, pg_catalog, public;

-- Insertion de 8 noms d'exemple dans bib_noms (les taxons de mon territoire)
-- ainsi que dans la liste des taxons saisissables dans occtax
INSERT INTO bib_noms (cd_nom, cd_ref, nom_francais) VALUES (67111, 67111, 'Ablette');
INSERT INTO cor_nom_liste (id_nom, id_liste) VALUES ((SELECT max(id_nom) FROM taxonomie.bib_noms), 100);
INSERT INTO bib_noms (cd_nom, cd_ref, nom_francais) VALUES (60612, 60612, 'Lynx boréal');
INSERT INTO cor_nom_liste (id_nom, id_liste) VALUES ((SELECT max(id_nom) FROM taxonomie.bib_noms), 100);
INSERT INTO bib_noms (cd_nom, cd_ref, nom_francais) VALUES (351, 351, 'Grenouille rousse');
INSERT INTO cor_nom_liste (id_nom, id_liste) VALUES ((SELECT max(id_nom) FROM taxonomie.bib_noms), 100);
INSERT INTO bib_noms (cd_nom, cd_ref, nom_francais) VALUES (8326, 8326, 'Cicindèle hybride');
INSERT INTO cor_nom_liste (id_nom, id_liste) VALUES ((SELECT max(id_nom) FROM taxonomie.bib_noms), 100);
INSERT INTO bib_noms (cd_nom, cd_ref, nom_francais) VALUES (11165, 11165, 'Coccinelle à 7 points');
INSERT INTO cor_nom_liste (id_nom, id_liste) VALUES ((SELECT max(id_nom) FROM taxonomie.bib_noms), 100);
INSERT INTO bib_noms (cd_nom, cd_ref, nom_francais) VALUES (18437, 18437, 'Ecrevisse à pieds blancs');
INSERT INTO cor_nom_liste (id_nom, id_liste) VALUES ((SELECT max(id_nom) FROM taxonomie.bib_noms), 100);
INSERT INTO bib_noms (cd_nom, cd_ref, nom_francais) VALUES (81065, 81065, 'Alchémille rampante');
INSERT INTO cor_nom_liste (id_nom, id_liste) VALUES ((SELECT max(id_nom) FROM taxonomie.bib_noms), 100);
INSERT INTO bib_noms (cd_nom, cd_ref, nom_francais) VALUES (95186, 95186, 'Inule fétide');
INSERT INTO cor_nom_liste (id_nom, id_liste) VALUES ((SELECT max(id_nom) FROM taxonomie.bib_noms), 100);
INSERT INTO bib_noms (cd_nom, cd_ref, nom_francais, comments) VALUES (713776, 209902, '-', 'un synonyme');

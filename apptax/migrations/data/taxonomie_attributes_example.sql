-- Insertion optionnelle d'un exemple d'attribut en version 1.8.1
-- A partir de la version 1.9.0, les évolutions de la BDD sont gérées dans des migrations Alembic

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = taxonomie, pg_catalog, public;

-- Insertion d'un attribut spécifique d'exemple (uniquement proposé pour les taxons du groupe Oiseaux)
INSERT INTO bib_attributs (nom_attribut, label_attribut, liste_valeur_attribut, obligatoire, desc_attribut, type_attribut, type_widget, regne, group2_inpn, id_theme, ordre) 
    VALUES ('migrateur', 'Migrateur', '{"values":["migrateur","migrateur partiel","sédentaire"]}', false, 'Défini le statut de migration pour le territoire', 'varchar(50)', 'select', 'Animalia', 'Oiseaux', (SELECT id_theme FROM taxonomie.bib_themes WHERE nom_theme = 'Mon territoire'), 1);

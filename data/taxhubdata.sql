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

-- Creation de la table de tous les noms de Taxref mis en forme pour la recherche de taxons
CREATE TABLE taxonomie.vm_taxref_list_forautocomplete AS
SELECT t.cd_nom,
  t.cd_ref,
  t.search_name,
  t.nom_valide,
  t.lb_nom,
  t.regne,
  t.group2_inpn
FROM (
  -- PARTIE NOM SCIENTIFIQUE : ici on prend TOUS les synonymes.
  SELECT t_1.cd_nom,
        t_1.cd_ref,
        concat(t_1.lb_nom, ' =  <i> ', t_1.nom_valide, '</i>', ' - [', t_1.id_rang, ' - ', t_1.cd_nom , ']') AS search_name,
        t_1.nom_valide,
        t_1.lb_nom,
        t_1.regne,
        t_1.group2_inpn
  FROM taxonomie.taxref t_1
  UNION
  -- PARTIE NOM FRANCAIS : ici on prend une seule fois (DISTINCT) dans Taxref tous les taxons de références 
  -- On ne prend pas les taxons qui n'ont pas de nom vern dans taxref,
  -- donc si un taxon n'a pas de nom vern dans Taxref, il n'est accessible que par son nom scientifique.
  SELECT DISTINCT 
        t_1.cd_nom,
        t_1.cd_ref,
        concat(split_part(t_1.nom_vern, ',', 1), ' =  <i> ', t_1.nom_valide, '</i>', ' - [', t_1.id_rang, ' - ', t_1.cd_ref , ']' ) AS search_name,
        t_1.nom_valide,
        t_1.lb_nom,
        t_1.regne,
        t_1.group2_inpn
  FROM taxonomie.taxref t_1
  WHERE t_1.nom_vern IS NOT null and t_1.cd_nom = t_1.cd_ref
) t;
-- Ici on filtre pour ne conserver que les taxons présents dans les listes (cor_nom_liste)
-- La jointure est double : sur le cd_nom + le cd_ref (pour les noms qui n'auraient pas leur taxon référence dans bib_noms)

-- Creation des index de la table vm_taxref_list_forautocomplete
CREATE INDEX i_vm_taxref_list_forautocomplete_cd_nom
  ON vm_taxref_list_forautocomplete (cd_nom ASC NULLS LAST);
CREATE INDEX i_vm_taxref_list_forautocomplete_search_name
  ON vm_taxref_list_forautocomplete (search_name ASC NULLS LAST);
CREATE INDEX i_tri_vm_taxref_list_forautocomplete_search_name
  ON vm_taxref_list_forautocomplete
  USING gist
  (search_name  gist_trgm_ops);

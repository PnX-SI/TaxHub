-- Insertion de 8 noms d'exemple dans bib_noms (les taxons de mon territoire)
-- ainsi que dans la liste des taxons saisissables dans occtax
INSERT INTO taxonomie.bib_noms (cd_nom, cd_ref, nom_francais) VALUES (67111, 67111, 'Ablette');
INSERT INTO taxonomie.cor_nom_liste (id_nom, id_liste) VALUES ((SELECT max(id_nom) FROM taxonomie.bib_noms), 100);
INSERT INTO taxonomie.bib_noms (cd_nom, cd_ref, nom_francais) VALUES (60612, 60612, 'Lynx boréal');
INSERT INTO taxonomie.cor_nom_liste (id_nom, id_liste) VALUES ((SELECT max(id_nom) FROM taxonomie.bib_noms), 100);
INSERT INTO taxonomie.bib_noms (cd_nom, cd_ref, nom_francais) VALUES (351, 351, 'Grenouille rousse');
INSERT INTO taxonomie.cor_nom_liste (id_nom, id_liste) VALUES ((SELECT max(id_nom) FROM taxonomie.bib_noms), 100);
INSERT INTO taxonomie.bib_noms (cd_nom, cd_ref, nom_francais) VALUES (8326, 8326, 'Cicindèle hybride');
INSERT INTO taxonomie.cor_nom_liste (id_nom, id_liste) VALUES ((SELECT max(id_nom) FROM taxonomie.bib_noms), 100);
INSERT INTO taxonomie.bib_noms (cd_nom, cd_ref, nom_francais) VALUES (11165, 11165, 'Coccinelle à 7 points');
INSERT INTO taxonomie.cor_nom_liste (id_nom, id_liste) VALUES ((SELECT max(id_nom) FROM taxonomie.bib_noms), 100);
INSERT INTO taxonomie.bib_noms (cd_nom, cd_ref, nom_francais) VALUES (18437, 18437, 'Ecrevisse à pieds blancs');
INSERT INTO taxonomie.cor_nom_liste (id_nom, id_liste) VALUES ((SELECT max(id_nom) FROM taxonomie.bib_noms), 100);
INSERT INTO taxonomie.bib_noms (cd_nom, cd_ref, nom_francais) VALUES (81065, 81065, 'Alchémille rampante');
INSERT INTO taxonomie.cor_nom_liste (id_nom, id_liste) VALUES ((SELECT max(id_nom) FROM taxonomie.bib_noms), 100);
INSERT INTO taxonomie.bib_noms (cd_nom, cd_ref, nom_francais) VALUES (95186, 95186, 'Inule fétide');
INSERT INTO taxonomie.cor_nom_liste (id_nom, id_liste) VALUES ((SELECT max(id_nom) FROM taxonomie.bib_noms), 100);
INSERT INTO taxonomie.bib_noms (cd_nom, cd_ref, nom_francais, comments) VALUES (713776, 209902, '-', 'un synonyme');


-- -- Insertion d'un attribut spécifique d'exemple (uniquement proposé pour les taxons du groupe Oiseaux)
INSERT INTO taxonomie.bib_attributs (nom_attribut, label_attribut, liste_valeur_attribut, obligatoire, desc_attribut, type_attribut, type_widget, regne, group2_inpn, id_theme, ordre)
    VALUES ('migrateur', 'Migrateur', '{"values":["migrateur","migrateur partiel","sédentaire"]}', false, 'Défini le statut de migration pour le territoire', 'varchar(50)', 'select', 'Animalia', 'Oiseaux', (SELECT id_theme FROM taxonomie.bib_themes WHERE nom_theme = 'Mon territoire'), 1);

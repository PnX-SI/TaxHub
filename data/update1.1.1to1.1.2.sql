--Création d'une nouvelle liste pour la saisie possible dans GeoNature
--A vous de mettre dans cette liste (cor_nom_liste) les taxons correspondant
--Eventuellement en utilisant l'attribut correspondant
INSERT INTO taxonomie.bib_listes (id_liste, nom_liste, desc_liste, picto)
VALUES(500,'Saisie possible','Liste des noms dont la saisie est autorisée','images/pictos/nopicto.gif');

--Ajout de la liste gymnospermes oubliés
--A vous de mettre dans cette liste (cor_nom_liste) les taxons correspondant
--Vous pouvez pour cela utiliser le champs "group2_inpn" de la table "taxonomie.taxref"
INSERT INTO taxonomie.bib_listes (id_liste ,nom_liste,desc_liste,picto,regne,group2_inpn) 
VALUES (308, 'Gymnospermes',null, 'images/pictos/nopicto.gif','Plantae','Gymnospermes');

--correction
UPDATE taxonomie.bib_listes SET group2_inpn = 'Fougères' WHERE id_liste = 305;
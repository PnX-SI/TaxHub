ALTER TABLE taxonomie.bib_listes
  ADD CONSTRAINT unique_bib_listes_nom_liste UNIQUE (nom_liste);

ALTER TABLE taxonomie.t_medias ADD COLUMN source varchar(25);
ALTER TABLE taxonomie.t_medias ADD COLUMN licence varchar(100);
ALTER TABLE taxonomie.t_medias ALTER COLUMN auteur TYPE character varying(1000);

ALTER TABLE taxonomie.bib_listes
  ADD CONSTRAINT unique_bib_listes_nom_liste UNIQUE (nom_liste);

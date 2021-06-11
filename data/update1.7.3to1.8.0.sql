-- Ajout d'une colonne code_liste
--      et création d'un séquence pour la colonne id_liste
ALTER TABLE taxonomie.bib_listes
  ADD COLUMN code_liste character varying(50);

-- Calcul d'une valeur initiale pour le nouveau champs "code_liste" en utilisant la valeur de "id_liste"
UPDATE taxonomie.bib_listes SET code_liste = id_liste::varchar;

ALTER TABLE taxonomie.bib_listes ALTER COLUMN code_liste SET NOT NULL;

ALTER TABLE taxonomie.bib_listes
  ADD CONSTRAINT unique_bib_listes_code_liste UNIQUE (code_liste);

CREATE SEQUENCE taxonomie.bib_listes_id_liste_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE taxonomie.bib_listes_id_liste_seq OWNED BY taxonomie.bib_listes.id_liste;

SELECT setval('taxonomie.bib_listes_id_liste_seq', (SELECT max(id_liste) FROM taxonomie.bib_listes), true);

ALTER TABLE taxonomie.bib_listes ALTER COLUMN id_liste SET DEFAULT nextval('taxonomie.bib_listes_id_liste_seq');

-- Ajout index sur colonne cd_sup pour les recherches de taxons fils
CREATE INDEX i_taxref_cd_sup
  ON taxonomie.taxref
  USING btree
  (cd_sup);

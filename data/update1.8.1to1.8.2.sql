ALTER TABLE taxonomie.bib_listes ALTER COLUMN id_liste DROP DEFAULT;
DROP SEQUENCE  IF EXISTS taxonomie.bib_listes_id_liste_seq;


CREATE SEQUENCE taxonomie.bib_listes_id_liste_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE taxonomie.bib_listes_id_liste_seq OWNED BY taxonomie.bib_listes.id_liste;

SELECT setval('taxonomie.bib_listes_id_liste_seq', (SELECT max(id_liste) FROM taxonomie.bib_listes), true);

ALTER TABLE taxonomie.bib_listes ALTER COLUMN id_liste SET DEFAULT nextval('taxonomie.bib_listes_id_liste_seq');

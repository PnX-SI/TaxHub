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

-- Modification d'un trigger sur les medias
DROP TRIGGER tri_unique_type1 ON taxonomie.t_medias;
CREATE TRIGGER tri_unique_type1
  AFTER INSERT OR UPDATE
  ON taxonomie.t_medias
  FOR EACH ROW
  EXECUTE PROCEDURE taxonomie.unique_type1();


-- Cas ou la mise à jour taxref n'est pas réalisée en amont
CREATE TABLE  IF NOT EXISTS taxonomie.bdc_statut_type (
    cd_type_statut varchar(50) PRIMARY KEY,
    lb_type_statut varchar(250),
    regroupement_type varchar(250),
    thematique varchar(50),
    type_value varchar(50)
);
CREATE TABLE taxonomie.bdc_statut_text (
	id_text serial NOT NULL PRIMARY KEY,
	cd_st_text  varchar(50),
	cd_type_statut varchar(50) NOT NULL,
	cd_sig varchar(50),
	cd_doc int4,
	niveau_admin varchar(250),
	cd_iso3166_1 varchar(50),
	cd_iso3166_2 varchar(50),
	lb_adm_tr varchar(250),
	full_citation text,
	doc_url TEXT,
	ENABLE boolean DEFAULT(true)
);

ALTER TABLE taxonomie.bdc_statut_text
	ADD CONSTRAINT bdc_statut_text_fkey FOREIGN KEY (cd_type_statut)
REFERENCES taxonomie.bdc_statut_type(cd_type_statut) ON DELETE CASCADE ON UPDATE CASCADE;

CREATE TABLE taxonomie.bdc_statut_values (
	id_value serial NOT NULL PRIMARY KEY,
	code_statut varchar(50) NOT NULL,
	label_statut varchar(250)
);

CREATE TABLE taxonomie.bdc_statut_cor_text_values (
	id_value_text serial NOT NULL PRIMARY KEY,
	id_value int4 NOT NULL,
	id_text int4 NOT NULL
);

ALTER TABLE taxonomie.bdc_statut_cor_text_values
	ADD CONSTRAINT tbdc_statut_cor_text_values_id_value_fkey FOREIGN KEY (id_value)
REFERENCES taxonomie.bdc_statut_values(id_value) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE taxonomie.bdc_statut_cor_text_values
	ADD CONSTRAINT tbdc_statut_cor_text_values_id_text_fkey FOREIGN KEY (id_text)
REFERENCES taxonomie.bdc_statut_text(id_text) ON DELETE CASCADE ON UPDATE CASCADE;


CREATE TABLE taxonomie.bdc_statut_taxons (
	id int4 NOT NULL PRIMARY KEY,
	id_value_text int4 NOT NULL,
	cd_nom int4 NOT NULL,
	cd_ref int4 NOT NULL, -- TO KEEP?
	rq_statut varchar(1000)
);

ALTER TABLE taxonomie.bdc_statut_taxons
	ADD CONSTRAINT bdc_statut_taxons_id_value_text_fkey FOREIGN KEY (id_value_text)
REFERENCES taxonomie.bdc_statut_cor_text_values(id_value_text) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE taxonomie.bdc_statut_taxons
	ADD CONSTRAINT bdc_statut_taxons_cd_nom_fkey FOREIGN KEY (cd_nom)
REFERENCES taxonomie.taxref(cd_nom) ON DELETE CASCADE ON UPDATE CASCADE;

COMMENT ON TABLE taxonomie.bdc_statut_text IS 'Table contenant les textes et leur zone d''application';
COMMENT ON TABLE taxonomie.bdc_statut_type IS 'Table des grands type de statuts';
COMMENT ON TABLE taxonomie.bdc_statut_values IS 'Table contenant la liste des valeurs possible pour les textes';
COMMENT ON TABLE taxonomie.bdc_statut_taxons IS 'Table d''association entre les textes et les taxons';
COMMENT ON TABLE taxonomie.bdc_statut_cor_text_values IS 'Table d''association entre les textes, les taxons et la valeur';

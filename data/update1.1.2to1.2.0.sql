-- Nettoyage de la table d'import temporaire de taxref.
TRUNCATE TABLE taxonomie.import_taxref;

-- Convertir l'id_liste de bib_listes de serial vers integer.
ALTER TABLE taxonomie.bib_listes ALTER COLUMN id_liste DROP DEFAULT;
DROP SEQUENCE taxonomie.bib_listes_id_liste_seq;

--Rendre le picto de bib_listes obligatoire avec une valeur par défaut.
ALTER TABLE taxonomie.bib_listes ALTER COLUMN picto SET NOT NULL;
ALTER TABLE taxonomie.bib_listes ALTER COLUMN picto SET DEFAULT 'images/pictos/nopicto.gif';

--Sortir les infos spécifiques des tables de Taxref
CREATE TABLE taxonomie.taxref_protection_articles_structure
(
  cd_protection character varying(50) NOT NULL,
  alias_statut character varying(10),
  concerne_structure boolean,
  CONSTRAINT taxref_protection_articles_structure_pkey PRIMARY KEY (cd_protection),
  CONSTRAINT taxref_protection_articles_structure_cd_protect_fkey FOREIGN KEY (cd_protection)
      REFERENCES taxonomie.taxref_protection_articles (cd_protection) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
);

CREATE OR REPLACE FUNCTION taxonomie.trg_fct_refresh_attributesviews_per_kingdom()
  RETURNS trigger AS
$BODY$
DECLARE
   sregne text;
BEGIN
	if NEW.regne IS NULL THEN
		FOR sregne IN
			SELECT DISTINCT regne
			FROM taxonomie.taxref t
			JOIN taxonomie.bib_noms n
			ON t.cd_nom = n.cd_nom
      WHERE t.regne IS NOT NULL
		LOOP
			PERFORM taxonomie.fct_build_bibtaxon_attributs_view(sregne);
		END LOOP;
	ELSE
		PERFORM taxonomie.fct_build_bibtaxon_attributs_view(NEW.regne);
	END IF;
   RETURN NEW;
END
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

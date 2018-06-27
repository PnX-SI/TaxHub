SET search_path = taxonomie, pg_catalog;

ALTER TABLE taxonomie.bib_noms ADD COLUMN comments character varying(1000);

----------------------------------------------------------------------------------
--- MODIF liée à au passage du champ bib_nom.nom_francais en char(1000) -------
----------------------------------------------------------------------------------

-- suppression des vues qui sont liées à bib_noms
DO
$$
DECLARE
   sregne text;
BEGIN
	FOR sregne IN
		SELECT DISTINCT regne
		FROM taxonomie.taxref t
		JOIN taxonomie.bib_noms n
		ON t.cd_nom = n.cd_nom
		WHERE t.regne IS NOT NULL
	LOOP
		PERFORM 'DROP VIEW IF exists taxonomie.v_bibtaxon_attributs_%',sregne;
	END LOOP;
END
$$;

DROP VIEW IF EXISTS taxonomie.v_taxref_all_listes;


-- drop related trigger
DROP TRIGGER trg_refresh_nomfrancais_mv_taxref_list_forautocomplete ON taxonomie.bib_noms;

-- alter bib_noms
ALTER TABLE taxonomie.bib_noms ALTER COLUMN nom_francais TYPE character varying(1000);

-- relancer la fonction qui cree les vues

DO
$$
DECLARE
   sregne text;
BEGIN
	FOR sregne IN
		SELECT DISTINCT regne
		FROM taxonomie.taxref t
		JOIN taxonomie.bib_noms n
		ON t.cd_nom = n.cd_nom
		WHERE t.regne IS NOT NULL
	LOOP
			PERFORM taxonomie.fct_build_bibtaxon_attributs_view(sregne);
	END LOOP;
END
$$;

-- recree la vue v_taxref_all_lites

CREATE OR REPLACE VIEW v_taxref_all_listes AS
 WITH bib_nom_lst AS (
         SELECT cor_nom_liste.id_nom,
            bib_noms.cd_nom,
            bib_noms.nom_francais,
            cor_nom_liste.id_liste
           FROM taxonomie.cor_nom_liste
             JOIN taxonomie.bib_noms USING (id_nom)
        )
 SELECT t.regne,
    t.phylum,
    t.classe,
    t.ordre,
    t.famille,
    t.group1_inpn,
    t.group2_inpn,
    t.cd_nom,
    t.cd_ref,
    t.nom_complet,
    t.nom_valide,
    d.nom_francais AS nom_vern,
    t.lb_nom,
    d.id_liste
   FROM taxonomie.taxref t
     JOIN bib_nom_lst d ON t.cd_nom = d.cd_nom;


-- recree le trigger supprimé

CREATE TRIGGER trg_refresh_nomfrancais_mv_taxref_list_forautocomplete AFTER UPDATE OF nom_francais
ON bib_noms FOR EACH ROW
EXECUTE PROCEDURE trg_fct_refresh_nomfrancais_mv_taxref_list_forautocomplete();


----------------------------------------------------------------------------------
--- MODIF liée à l'ajout du champ cd_ref dans vm_taxref_list_forautocomplete-------
----------------------------------------------------------------------------------

DROP TABLE taxonomie.vm_taxref_list_forautocomplete;
DROP FUNCTION taxonomie.trg_fct_refresh_mv_taxref_list_forautocomplete() CASCADE;
DROP TRIGGER trg_refresh_mv_taxref_list_forautocomplete ON taxonomie.cor_nom_liste;

-- recrée la table vm_taxref_list_forautocomplete avec le cd_ref
CREATE TABLE vm_taxref_list_forautocomplete AS
SELECT t.cd_nom,
  t.cd_ref,
  t.search_name,
  t.nom_valide,
  t.lb_nom,
  t.regne,
  t.group2_inpn,
  l.id_liste
FROM (
  SELECT t_1.cd_nom,
        t_1.cd_ref,
        concat(t_1.lb_nom, ' =  <i> ', t_1.nom_valide, '</i>' ) AS search_name,
        t_1.nom_valide,
        t_1.lb_nom,
        t_1.regne,
        t_1.group2_inpn
  FROM taxonomie.taxref t_1
  UNION
  SELECT t_1.cd_nom,
        t_1.cd_ref,
        concat(n.nom_francais, ' =  <i> ', t_1.nom_valide, '</i>' ) AS search_name,
        t_1.nom_valide,
        t_1.lb_nom,
        t_1.regne,
        t_1.group2_inpn
  FROM taxonomie.taxref t_1
  JOIN taxonomie.bib_noms n
  ON t_1.cd_nom = n.cd_nom
  WHERE n.nom_francais IS NOT NULL AND t_1.cd_nom = t_1.cd_ref
) t
JOIN v_taxref_all_listes l ON t.cd_nom = l.cd_nom;
COMMENT ON TABLE vm_taxref_list_forautocomplete
     IS 'Table construite à partir d''une requete sur la base et mise à jour via le trigger trg_refresh_mv_taxref_list_forautocomplete de la table cor_nom_liste';

CREATE INDEX i_vm_taxref_list_forautocomplete_cd_nom
  ON vm_taxref_list_forautocomplete (cd_nom ASC NULLS LAST);
CREATE INDEX i_vm_taxref_list_forautocomplete_search_name
  ON vm_taxref_list_forautocomplete (search_name ASC NULLS LAST);


-- recree le trigger modifié

CREATE OR REPLACE FUNCTION trg_fct_refresh_mv_taxref_list_forautocomplete()
  RETURNS trigger AS
$BODY$
DECLARE
	new_cd_nom int;
	new_nom_vern varchar(1000);
BEGIN
	IF TG_OP in ('DELETE', 'TRUNCATE', 'UPDATE') THEN
	    DELETE FROM taxonomie.vm_taxref_list_forautocomplete WHERE cd_nom IN (
		SELECT cd_nom FROM taxonomie.bib_noms WHERE id_nom =  OLD.id_nom
	    );
	END IF;
	IF TG_OP in ('INSERT', 'UPDATE') THEN
		SELECT cd_nom, nom_francais INTO new_cd_nom, new_nom_vern FROM taxonomie.bib_noms WHERE id_nom = NEW.id_nom;

		INSERT INTO taxonomie.vm_taxref_list_forautocomplete
		SELECT t.cd_nom,
            t.cd_ref,
		    concat(t.lb_nom, ' = ', t.nom_valide) AS search_name,
		    t.nom_valide,
		    t.lb_nom,
		    t.regne,
		    t.group2_inpn,
		    NEW.id_liste
		FROM taxonomie.taxref t  WHERE cd_nom = new_cd_nom;


		IF NOT new_nom_vern IS NULL THEN
			INSERT INTO taxonomie.vm_taxref_list_forautocomplete
			SELECT t.cd_nom,
                t.cd_ref,
			    concat(new_nom_vern, ' = ', t.nom_valide) AS search_name,
			    t.nom_valide,
			    t.lb_nom,
			    t.regne,
			    t.group2_inpn,
          NEW.id_liste
			FROM taxonomie.taxref t
			WHERE cd_nom = new_cd_nom AND t.cd_nom = t.cd_ref;
		END IF;
	END IF;
  RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;


CREATE TRIGGER trg_refresh_mv_taxref_list_forautocomplete
  AFTER INSERT OR UPDATE OR DELETE
  ON cor_nom_liste
  FOR EACH ROW
  EXECUTE PROCEDURE trg_fct_refresh_mv_taxref_list_forautocomplete();

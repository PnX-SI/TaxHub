SET search_path = taxonomie, pg_catalog;



----------------------------------------------------------------------------------
--- MODIF liée à au passage à taxref v11
----------------------------------------------------------------------------------


DROP VIEW taxonomie.v_taxref_hierarchie_bibtaxons;

DO $$ 
    BEGIN
        BEGIN
            ALTER TABLE taxonomie.taxref ADD sous_famille character varying(50);
        EXCEPTION
            WHEN duplicate_column THEN RAISE NOTICE 'column sous_famille already exists in taxref.';
        END;
    END;
$$;

DO $$ 
    BEGIN
        BEGIN
            ALTER TABLE taxonomie.taxref ADD tribu character varying(50);
        EXCEPTION
            WHEN duplicate_column THEN RAISE NOTICE 'column tribu already exists in taxref.';
        END;
    END;
$$;

DO $$ 
    BEGIN
        BEGIN
            ALTER TABLE taxonomie.taxref ADD url character varying(50);
        EXCEPTION
            WHEN duplicate_column THEN RAISE NOTICE 'column url already exists in taxref.';
        END;
    END;
$$;

ALTER TABLE taxonomie.taxref ALTER COLUMN  nom_vern TYPE character varying(1000) USING nom_vern::character varying(1000);
ALTER TABLE taxonomie.taxref ALTER COLUMN  lb_auteur TYPE character varying(250) USING lb_auteur::character varying(250);


CREATE OR REPLACE VIEW taxonomie.v_taxref_hierarchie_bibtaxons AS 
 WITH mestaxons AS (
         SELECT tx_1.cd_nom,
            tx_1.id_habitat,
            tx_1.id_rang,
            tx_1.regne,
            tx_1.phylum,
            tx_1.classe,
            tx_1.ordre,
            tx_1.famille,
            tx_1.cd_taxsup,
            tx_1.cd_sup,
            tx_1.cd_ref,
            tx_1.lb_nom,
            tx_1.lb_auteur,
            tx_1.nom_complet,
            tx_1.nom_complet_html,
            tx_1.nom_valide,
            tx_1.nom_vern,
            tx_1.nom_vern_eng,
            tx_1.group1_inpn,
            tx_1.group2_inpn
           FROM taxonomie.taxref tx_1
             JOIN taxonomie.bib_noms t ON t.cd_nom = tx_1.cd_nom
        )
 SELECT DISTINCT tx.regne,
    tx.phylum,
    tx.classe,
    tx.ordre,
    tx.famille,
    tx.cd_nom,
    tx.cd_ref,
    tx.lb_nom,
    btrim(tx.id_rang::text) AS id_rang,
    f.nb_tx_fm,
    o.nb_tx_or,
    c.nb_tx_cl,
    p.nb_tx_ph,
    r.nb_tx_kd
   FROM taxonomie.taxref tx
     JOIN ( SELECT DISTINCT tx_1.regne,
            tx_1.phylum,
            tx_1.classe,
            tx_1.ordre,
            tx_1.famille
           FROM mestaxons tx_1) a ON a.regne::text = tx.regne::text AND tx.id_rang::text = 'KD'::text OR a.phylum::text = tx.phylum::text AND tx.id_rang::text = 'PH'::text OR a.classe::text = tx.classe::text AND tx.id_rang::text = 'CL'::text OR a.ordre::text = tx.ordre::text AND tx.id_rang::text = 'OR'::text OR a.famille::text = tx.famille::text AND tx.id_rang::text = 'FM'::text
     LEFT JOIN ( SELECT mestaxons.famille,
            count(*) AS nb_tx_fm
           FROM mestaxons
          WHERE mestaxons.id_rang::text <> 'FM'::text
          GROUP BY mestaxons.famille) f ON f.famille::text = tx.famille::text
     LEFT JOIN ( SELECT mestaxons.ordre,
            count(*) AS nb_tx_or
           FROM mestaxons
          WHERE mestaxons.id_rang::text <> 'OR'::text
          GROUP BY mestaxons.ordre) o ON o.ordre::text = tx.ordre::text
     LEFT JOIN ( SELECT mestaxons.classe,
            count(*) AS nb_tx_cl
           FROM mestaxons
          WHERE mestaxons.id_rang::text <> 'CL'::text
          GROUP BY mestaxons.classe) c ON c.classe::text = tx.classe::text
     LEFT JOIN ( SELECT mestaxons.phylum,
            count(*) AS nb_tx_ph
           FROM mestaxons
          WHERE mestaxons.id_rang::text <> 'PH'::text
          GROUP BY mestaxons.phylum) p ON p.phylum::text = tx.phylum::text
     LEFT JOIN ( SELECT mestaxons.regne,
            count(*) AS nb_tx_kd
           FROM mestaxons
          WHERE mestaxons.id_rang::text <> 'KD'::text
          GROUP BY mestaxons.regne) r ON r.regne::text = tx.regne::text
  WHERE (tx.id_rang::text = ANY (ARRAY['KD'::character varying::text, 'PH'::character varying::text, 'CL'::character varying::text, 'OR'::character varying::text, 'FM'::character varying::text])) AND tx.cd_nom = tx.cd_ref;


ALTER TABLE taxonomie.bib_noms ADD COLUMN comments character varying(1000);

----------------------------------------------------------------------------------
--- MODIF liée à au passage du champ bib_nom.nom_francais en char(1000) -------
----------------------------------------------------------------------------------

-- suppression des vues qui sont liées à bib_noms
-- ? Le perform ne supprime pas les vues ? A creuser.
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

DROP VIEW IF exists taxonomie.v_bibtaxon_attributs_animalia;
DROP VIEW IF exists taxonomie.v_bibtaxon_attributs_fungi;
DROP VIEW IF exists taxonomie.v_bibtaxon_attributs_protozoa;
DROP VIEW IF exists taxonomie.v_bibtaxon_attributs_plantae;
DROP VIEW IF exists taxonomie.v_bibtaxon_attributs_bacteria;
DROP VIEW IF exists taxonomie.v_bibtaxon_attributs_chromista;


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
DROP TRIGGER IF EXISTS trg_refresh_mv_taxref_list_forautocomplete ON taxonomie.cor_nom_liste;

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

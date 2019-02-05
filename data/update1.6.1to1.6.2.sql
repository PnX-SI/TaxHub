SET search_path = taxonomie, pg_catalog, public;


--Création d'index uniques sur les vues matérialisées 
--afin de permettre le refresh
CREATE UNIQUE INDEX i_unique_ordre
  ON taxonomie.vm_ordre
  USING btree
  (ordre);
CREATE UNIQUE INDEX i_unique_phylum
  ON taxonomie.vm_phylum
  USING btree
  (phylum);
CREATE UNIQUE INDEX i_unique_regne
  ON taxonomie.vm_regne
  USING btree
  (regne);
CREATE UNIQUE INDEX i_unique_famille
  ON taxonomie.vm_famille
  USING btree
  (famille);
CREATE UNIQUE INDEX i_unique_classe
  ON taxonomie.vm_classe
  USING btree
  (classe);
CREATE UNIQUE INDEX i_unique_group1_inpn
  ON taxonomie.vm_group1_inpn
  USING btree
  (group1_inpn);
CREATE UNIQUE INDEX i_unique_group2_inpn
  ON taxonomie.vm_group2_inpn
  USING btree
  (group2_inpn);


SELECT concat(aut.search_name,  ' - [', t.id_rang, ' - ', t.cd_nom , ']' )
FROM taxonomie.vm_taxref_list_forautocomplete aut
JOIN taxonomie.taxref t ON aut.cd_nom = t.cd_nom;

  -- Modification de la table vm_taxref_list_forautocomplete
CREATE OR REPLACE FUNCTION taxonomie.trg_fct_refresh_mv_taxref_list_forautocomplete()
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
		    concat(t.lb_nom, ' =  <i> ', t.nom_valide, '</i>', ' - [', t.id_rang, ' - ', t.cd_nom , ']') AS search_name,
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
                concat(new_nom_vern, ' =  <i> ', t.nom_valide, '</i>', ' - [', t.id_rang, ' - ', t.cd_nom , ']') AS search_name,
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


  CREATE OR REPLACE FUNCTION taxonomie.trg_fct_refresh_nomfrancais_mv_taxref_list_forautocomplete()
  RETURNS trigger AS
$BODY$
DECLARE
BEGIN
    UPDATE taxonomie.vm_taxref_list_forautocomplete v
    SET search_name = concat(NEW.nom_francais, ' =  <i> ', t.nom_valide, '</i>', ' - [', t.id_rang, ' - ', t.cd_nom , ']')
    FROM taxonomie.taxref t
		WHERE v.cd_nom = NEW.cd_nom AND t.cd_nom = NEW.cd_nom;
    RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;


DO
$$
BEGIN
     CREATE INDEX i_tri_vm_taxref_list_forautocomplete_search_name
            ON taxonomie.vm_taxref_list_forautocomplete
            USING gist
            (search_name  gist_trgm_ops);
EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Tentative d''un index existant';
END
$$;


-------------------------------------------------------------------------------------
--GESTION DES NOMS ORPHELINS (SYNONYMES) SANS LEUR TAXON DE REFERENCE DANS BIB_NOMS--
-------------------------------------------------------------------------------------
CREATE INDEX i_bib_noms_cd_ref ON taxonomie.bib_noms USING btree (cd_ref);

DROP TABLE taxonomie.vm_taxref_list_forautocomplete;
CREATE TABLE taxonomie.vm_taxref_list_forautocomplete AS
SELECT t.cd_nom,
  t.cd_ref,
  t.search_name,
  t.nom_valide,
  t.lb_nom,
  t.regne,
  t.group2_inpn,
  cnl.id_liste
FROM (
  -- PARTIE NOM SCIENTIFIQUE : ici on prend TOUS les synonymes.
  SELECT t_1.cd_nom,
        t_1.cd_ref,
        concat(t_1.lb_nom, ' =  <i> ', t_1.nom_valide, '</i>', ' - [', t_1.id_rang, ' - ', t_1.cd_nom , ']') AS search_name,
        t_1.nom_valide,
        t_1.lb_nom,
        t_1.regne,
        t_1.group2_inpn
  FROM taxonomie.taxref t_1
  UNION
  -- PARTIE NOM FRANCAIS : ici on prend une seule fois (DISTINCT) dans taxref tous les taxons de références présents dans bib_noms (t_1.cd_nom = n.cd_ref)
  -- même si un taxon n'a qu'un synonyme et pas son taxon de référence dans bib_noms.
  -- On ne prend pas les taxons qui n'ont pas de nom français dans bib_noms,
  -- donc si un taxon n'a pas de nom français dans bib_noms, il n'est accessible que par son nom scientifique.
  SELECT DISTINCT
        t_1.cd_nom,
        t_1.cd_ref,
        concat(n.nom_francais, ' =  <i> ', t_1.nom_valide, '</i>', ' - [', t_1.id_rang, ' - ', t_1.cd_ref , ']' ) AS search_name,
        t_1.nom_valide,
        t_1.lb_nom,
        t_1.regne,
        t_1.group2_inpn
  FROM taxonomie.taxref t_1
  JOIN taxonomie.bib_noms n ON t_1.cd_nom = n.cd_ref AND n.nom_francais IS NOT null
) t
-- ici on filtre pour ne conserver que les taxons présents dans les listes (cor_nom_liste)
-- la jointure est double : sur le cd_nom + le cd_ref (pour les noms qui n'auraient pas leur taxon référence dans bib_noms)
JOIN taxonomie.bib_noms n ON n.cd_nom = t.cd_nom OR n.cd_ref = t.cd_ref
JOIN taxonomie.cor_nom_liste cnl ON cnl.id_nom = n.id_nom;
COMMENT ON TABLE taxonomie.vm_taxref_list_forautocomplete
     IS 'Table construite à partir d''une requete sur la base et mise à jour via le trigger trg_refresh_mv_taxref_list_forautocomplete de la table cor_nom_liste';


CREATE OR REPLACE FUNCTION taxonomie.trg_fct_refresh_mv_taxref_list_forautocomplete()
  RETURNS trigger AS
$BODY$
DECLARE
	new_cd_nom int;
    new_cd_ref int;
	new_nom_vern varchar(1000);
	count_cdref int;
BEGIN
	IF TG_OP in ('DELETE', 'TRUNCATE', 'UPDATE') THEN
	    DELETE FROM taxonomie.vm_taxref_list_forautocomplete WHERE cd_nom IN (
		SELECT cd_nom FROM taxonomie.bib_noms WHERE id_nom =  OLD.id_nom
	    ) AND id_liste = OLD.id_liste;
	END IF;
	IF TG_OP in ('INSERT', 'UPDATE') THEN
		SELECT cd_nom, nom_francais, cd_ref INTO new_cd_nom, new_nom_vern, new_cd_ref FROM taxonomie.bib_noms WHERE id_nom = NEW.id_nom;
    SELECT count(*) INTO count_cdref FROM taxonomie.vm_taxref_list_forautocomplete WHERE cd_ref = new_cd_ref AND id_liste = NEW.id_liste;

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


		IF NOT new_nom_vern IS NULL AND count_cdref = 0 THEN
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



DROP TRIGGER tri_unique_type1 ON taxonomie.t_medias;

CREATE TRIGGER tri_unique_type1
  AFTER INSERT OR UPDATE
  ON taxonomie.t_medias
  FOR EACH ROW
  EXECUTE PROCEDURE taxonomie.unique_type1();

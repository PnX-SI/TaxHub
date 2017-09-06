
SET search_path = taxonomie, pg_catalog;

CREATE INDEX i_fk_taxref_group1_inpn ON taxref USING btree (group1_inpn);

CREATE INDEX i_fk_taxref_group2_inpn ON taxref USING btree (group2_inpn);

CREATE INDEX i_fk_taxref_nom_vern ON taxref USING btree (nom_vern);


CREATE OR REPLACE FUNCTION taxonomie.unique_type1()
RETURNS trigger AS
$BODY$
DECLARE
  nbimgprincipale integer;
  mymedia record;
BEGIN
  IF new.id_type = 1 THEN
    SELECT count(*) INTO nbimgprincipale FROM taxonomie.t_medias WHERE cd_ref = new.cd_ref AND id_type = 1 AND NOT id_media = NEW.id_media;
    IF nbimgprincipale > 0 THEN
      FOR mymedia  IN SELECT * FROM taxonomie.t_medias WHERE cd_ref = new.cd_ref AND id_type = 1 LOOP
        UPDATE taxonomie.t_medias SET id_type = 2 WHERE id_media = mymedia.id_media;
        RAISE NOTICE USING MESSAGE =
          'La photo principale a été mise à jour pour le cd_ref ' || new.cd_ref ||
          '. La photo avec l''id_media ' || mymedia.id_media  || ' n''est plus la photo principale.';
      END LOOP;
    END IF;
  END IF;
  RETURN NEW;
END;
$BODY$
LANGUAGE plpgsql VOLATILE
COST 100;

CREATE TRIGGER tri_unique_type1
  BEFORE INSERT OR UPDATE
  ON t_medias
  FOR EACH ROW
  EXECUTE PROCEDURE unique_type1();



  --DROP MATERIALIZED VIEW IF EXISTS vm_taxref_list_forautocomplete;
  CREATE MATERIALIZED VIEW vm_taxref_list_forautocomplete AS
  SELECT t.*, l.id_liste
  FROM (
  SELECT t.cd_nom,
      concat(t.lb_nom, ' = ', t.nom_complet_html) AS search_name,
      t.nom_valide,
      t.lb_nom,
      t.regne,
      t.group2_inpn
     FROM  taxonomie.taxref t
  UNION
   SELECT t.cd_nom,
      concat(t.nom_vern, ' = ', t.nom_complet_html) AS search_name,
      t.nom_valide,
      t.lb_nom,
      t.regne,
      t.group2_inpn
     FROM taxonomie.taxref t
    WHERE t.nom_vern IS NOT NULL
    ) t
    JOIN taxonomie.v_taxref_all_listes l
   ON t.cd_nom = l.cd_nom
    WITH DATA;


CREATE OR REPLACE FUNCTION taxonomie.trg_fct_refresh_taxonlist_views_per_list()
  RETURNS trigger AS
$BODY$
DECLARE
BEGIN
   REFRESH MATERIALIZED VIEW taxonomie.vm_taxref_list_forautocomplete;
   RETURN NEW;
END
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

CREATE TRIGGER trg_refresh_taxonlist_views_per_list
AFTER INSERT OR UPDATE OR DELETE ON taxonomie.cor_nom_liste
FOR EACH STATEMENT EXECUTE PROCEDURE taxonomie.trg_fct_refresh_taxonlist_views_per_list();

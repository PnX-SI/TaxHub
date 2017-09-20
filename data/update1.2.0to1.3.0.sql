
SET search_path = taxonomie, pg_catalog;

CREATE INDEX i_fk_taxref_group1_inpn ON taxref USING btree (group1_inpn);

CREATE INDEX i_fk_taxref_group2_inpn ON taxref USING btree (group2_inpn);

CREATE INDEX i_fk_taxref_nom_vern ON taxref USING btree (nom_vern);



-------------
--FUNCTIONS--
-------------
CREATE OR REPLACE FUNCTION check_is_inbibnoms(mycdnom integer)
  RETURNS boolean AS
$BODY$
--fonction permettant de vérifier si un texte proposé correspond à un group2_inpn dans la table taxref
  BEGIN
    IF mycdnom IN(SELECT cd_nom FROM taxonomie.bib_noms) THEN
      RETURN true;
    ELSE
      RETURN false;
    END IF;
  END;
$BODY$
  LANGUAGE plpgsql IMMUTABLE
  COST 100;


CREATE OR REPLACE FUNCTION check_is_group2inpn(mygroup text)
  RETURNS boolean AS
$BODY$
--fonction permettant de vérifier si un texte proposé correspond à un group2_inpn dans la table taxref
  BEGIN
    IF mygroup IN(SELECT group2_inpn FROM taxonomie.vm_group2_inpn) OR mygroup IS NULL THEN
      RETURN true;
    ELSE
      RETURN false;
    END IF;
  END;
$BODY$
  LANGUAGE plpgsql IMMUTABLE
  COST 100;


CREATE OR REPLACE FUNCTION check_is_regne(myregne text)
  RETURNS boolean AS
$BODY$
--fonction permettant de vérifier si un texte proposé correspond à un regne dans la table taxref
  BEGIN
    IF myregne IN(SELECT regne FROM taxonomie.vm_regne) OR myregne IS NULL THEN
      return true;
    ELSE
      RETURN false;
    END IF;
  END;
$BODY$
  LANGUAGE plpgsql IMMUTABLE
  COST 100;

CREATE OR REPLACE FUNCTION find_regne(mycdnom integer)
  RETURNS text AS
$BODY$
--fonction permettant de renvoyer le regne d'un taxon à partir de son cd_nom
  DECLARE theregne character varying(255);
  BEGIN
    SELECT INTO theregne regne FROM taxonomie.taxref WHERE cd_nom = mycdnom;
    return theregne;
  END;
$BODY$
  LANGUAGE plpgsql IMMUTABLE
  COST 100;

CREATE OR REPLACE FUNCTION find_group2inpn(mycdnom integer)
  RETURNS text AS
$BODY$
--fonction permettant de renvoyer le group2_inpn d'un taxon à partir de son cd_nom
  DECLARE group2 character varying(255);
  BEGIN
    SELECT INTO group2 group2_inpn FROM taxonomie.taxref WHERE cd_nom = mycdnom;
    return group2;
  END;
$BODY$
  LANGUAGE plpgsql IMMUTABLE
  COST 100;

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

DROP VIEW IF EXISTS v_taxref_all_listes;
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

DROP MATERIALIZED VIEW IF EXISTS vm_taxref_list_forautocomplete;

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


----------------------
--MATERIALIZED VIEWS--
----------------------
--Vue materialisée permettant d'améliorer fortement les performances des contraintes check sur les champs filtres 'regne' et 'group2_inpn'
CREATE MATERIALIZED VIEW vm_regne AS (SELECT DISTINCT regne FROM taxref);
CREATE MATERIALIZED VIEW vm_phylum AS (SELECT DISTINCT phylum FROM taxref);
CREATE MATERIALIZED VIEW vm_classe AS (SELECT DISTINCT classe FROM taxref);
CREATE MATERIALIZED VIEW vm_ordre AS (SELECT DISTINCT ordre FROM taxref);
CREATE MATERIALIZED VIEW vm_famille AS (SELECT DISTINCT famille FROM taxref);
CREATE MATERIALIZED VIEW vm_group1_inpn AS (SELECT DISTINCT group1_inpn FROM taxref);
CREATE MATERIALIZED VIEW vm_group2_inpn AS (SELECT DISTINCT group2_inpn FROM taxref);

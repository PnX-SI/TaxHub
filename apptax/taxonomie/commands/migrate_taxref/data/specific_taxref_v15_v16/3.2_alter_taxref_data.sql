
---- #################################################################################
---- #################################################################################
----		IMPORT DE TAXREF
---- #################################################################################
---- #################################################################################

------------------------------------------------
------------------------------------------------
--Alter existing constraints
------------------------------------------------
------------------------------------------------
ALTER TABLE taxonomie.t_medias DROP CONSTRAINT IF EXISTS check_cd_ref_is_ref;
ALTER TABLE taxonomie.cor_taxon_attribut DROP CONSTRAINT IF EXISTS check_is_cd_ref;
ALTER TABLE taxonomie.cor_nom_liste DROP CONSTRAINT cor_nom_listes_taxref_fkey;

------------------------------------------------
------------------------------------------------
-- 	UPDATE TAXREF
------------------------------------------------
------------------------------------------------

-- UPDATE EXISTING CD_NOM
UPDATE taxonomie.taxref t
   SET id_habitat = it.habitat::int, id_rang = it.rang, regne = it.regne, phylum = it.phylum,
       classe = it.classe, ordre = it.ordre, famille = it.famille, cd_taxsup = it.cd_taxsup,
       cd_sup = it.cd_sup, cd_ref = it.cd_ref,
       lb_nom = it.lb_nom, lb_auteur = it.lb_auteur, nom_complet = it.nom_complet,
       nom_complet_html = it.nom_complet_html, nom_valide = it.nom_valide,
       nom_vern = it.nom_vern, nom_vern_eng = it.nom_vern_eng, group1_inpn = it.group1_inpn,
       group2_inpn = it.group2_inpn, sous_famille = it.sous_famille,
       tribu = it.tribu, url = it.url, group3_inpn = it.group3_inpn
FROM taxonomie.import_taxref it
WHERE it.cd_nom  = t.cd_nom;

-- ADD NEW CD_NOM
INSERT INTO taxonomie.taxref(
            cd_nom, id_habitat, id_rang, regne, phylum, classe,
            ordre, famille, cd_taxsup, cd_sup, cd_ref, lb_nom, lb_auteur,
            nom_complet, nom_complet_html, nom_valide, nom_vern, nom_vern_eng,
            group1_inpn, group2_inpn, sous_famille, tribu, url, group3_inpn)
SELECT it.cd_nom,it.habitat::int, it.rang, it.regne, it.phylum, it.classe,
    it.ordre, it.famille, it.cd_taxsup, it.cd_sup, it.cd_ref, it.lb_nom, it.lb_auteur,
    it.nom_complet, it.nom_complet_html, it.nom_valide, it.nom_vern, it.nom_vern_eng,
    it.group1_inpn, it.group2_inpn, it.sous_famille, it.tribu, it.url, it.group3_inpn
FROM taxonomie.import_taxref it
LEFT OUTER JOIN taxonomie.taxref t
ON it.cd_nom = t.cd_nom
WHERE t.cd_nom IS NULL;

-- Regional Status

DO $$ BEGIN   
   IF :taxref_region = 'gf' THEN UPDATE taxonomie.taxref t SET id_statut = NULLIF(it.gf, '') FROM taxonomie.import_taxref it WHERE it.cd_nom  = t.cd_nom;
   ELSIF :taxref_region = 'mar' THEN UPDATE taxonomie.taxref t SET id_statut = NULLIF(it.mar, '') FROM taxonomie.import_taxref it WHERE it.cd_nom  = t.cd_nom;
   ELSIF :taxref_region = 'gua' THEN UPDATE taxonomie.taxref t SET id_statut = NULLIF(it.gua, '') FROM taxonomie.import_taxref it WHERE it.cd_nom  = t.cd_nom;
   ELSIF :taxref_region = 'sm' THEN UPDATE taxonomie.taxref t SET id_statut = NULLIF(it.sm, '') FROM taxonomie.import_taxref it WHERE it.cd_nom  = t.cd_nom;
   ELSIF :taxref_region = 'sb' THEN UPDATE taxonomie.taxref t SET id_statut = NULLIF(it.sb, '') FROM taxonomie.import_taxref it WHERE it.cd_nom  = t.cd_nom;
   ELSIF :taxref_region = 'spm' THEN UPDATE taxonomie.taxref t SET id_statut = NULLIF(it.spm, '') FROM taxonomie.import_taxref it WHERE it.cd_nom  = t.cd_nom;
   ELSIF :taxref_region = 'may' THEN UPDATE taxonomie.taxref t SET id_statut = NULLIF(it.may, '') FROM taxonomie.import_taxref it WHERE it.cd_nom  = t.cd_nom;
   ELSIF :taxref_region = 'epa' THEN UPDATE taxonomie.taxref t SET id_statut = NULLIF(it.epa, '') FROM taxonomie.import_taxref it WHERE it.cd_nom  = t.cd_nom;
   ELSIF :taxref_region = 'reu' THEN UPDATE taxonomie.taxref t SET id_statut = NULLIF(it.reu, '') FROM taxonomie.import_taxref it WHERE it.cd_nom  = t.cd_nom;
   ELSIF :taxref_region = 'sa' THEN UPDATE taxonomie.taxref t SET id_statut = NULLIF(it.sa, '') FROM taxonomie.import_taxref it WHERE it.cd_nom  = t.cd_nom;
   ELSIF :taxref_region = 'ta' THEN UPDATE taxonomie.taxref t SET id_statut = NULLIF(it.ta, '') FROM taxonomie.import_taxref it WHERE it.cd_nom  = t.cd_nom;
   ELSIF :taxref_region = 'taaf' THEN UPDATE taxonomie.taxref t SET id_statut = NULLIF(it.taaf, '') FROM taxonomie.import_taxref it WHERE it.cd_nom  = t.cd_nom;
   ELSIF :taxref_region = 'pf' THEN UPDATE taxonomie.taxref t SET id_statut = NULLIF(it.pf, '') FROM taxonomie.import_taxref it WHERE it.cd_nom  = t.cd_nom;
   ELSIF :taxref_region = 'nc' THEN UPDATE taxonomie.taxref t SET id_statut = NULLIF(it.nc, '') FROM taxonomie.import_taxref it WHERE it.cd_nom  = t.cd_nom;
   ELSIF :taxref_region = 'wf' THEN UPDATE taxonomie.taxref t SET id_statut = NULLIF(it.wf, '') FROM taxonomie.import_taxref it WHERE it.cd_nom  = t.cd_nom;
   ELSIF :taxref_region = 'cli' THEN UPDATE taxonomie.taxref t SET id_statut = NULLIF(it.cli, '') FROM taxonomie.import_taxref it WHERE it.cd_nom  = t.cd_nom;
   ELSE  UPDATE taxonomie.taxref t SET id_statut = NULLIF(it.fr,  '') FROM taxonomie.import_taxref it WHERE it.cd_nom  = t.cd_nom;
END IF;
END $$;

-- DELETE MISSING CD_NOM if not keep_cdnom is specify
DO $$ BEGIN
    IF  :keep_cd_nom = FALSE THEN
        DELETE FROM taxonomie.taxref
        WHERE cd_nom IN (
          SELECT cd_nom
         FROM taxonomie.cdnom_disparu
        );

    END IF;
END $$;

---- #################################################################################
---- #################################################################################
----	 REPERCUSSION des changements de taxref dans taxhub (attributs, médias)
---- #################################################################################
---- #################################################################################

--- Sauvegarde des données au cas ou
DROP TABLE IF EXISTS tmp_taxref_changes.t_medias;
CREATE TABLE tmp_taxref_changes.t_medias AS
SELECT * FROM taxonomie.t_medias;

DROP TABLE IF EXISTS tmp_taxref_changes.cor_taxon_attribut;
CREATE TABLE tmp_taxref_changes.cor_taxon_attribut AS
SELECT * FROM taxonomie.cor_taxon_attribut;

DROP TABLE IF EXISTS tmp_taxref_changes.cor_nom_liste;
CREATE TABLE tmp_taxref_changes.cor_nom_liste AS
SELECT * FROM taxonomie.cor_nom_liste;


---- #################################################################################
--- cor_nom_liste
---- #################################################################################
-- Remplacement des anciens cd_nom par leurs remplaçants dans cor_nom_liste
WITH d AS (
    SELECT cnl.id_liste , cnl.cd_nom, cd.cd_nom_remplacement
    FROM taxonomie.cor_nom_liste AS cnl
    JOIN taxonomie.cdnom_disparu AS cd
    ON cnl.cd_nom = cd.cd_nom
    LEFT OUTER JOIN taxonomie.cor_nom_liste AS repl
    ON repl.cd_nom = cd.cd_nom_remplacement  AND cnl.id_liste = repl.id_liste
    WHERE repl.cd_nom IS NULL AND NOT  cd.cd_nom_remplacement  IS NULL
)
UPDATE taxonomie.cor_nom_liste l SET cd_nom  = cd_nom_remplacement
FROM d
WHERE d.cd_nom = l.cd_nom  AND d.id_liste = l.id_liste;

-- supression dans les cas ou il n'y a pas de taxons de remplacements
-- Même si le paramètre keep_cd_nom est spécifié
--    de façon à ne pas autoriser la saisie de nouvelles données avec des cd_nom qui n'existent plus
DELETE FROM taxonomie.cor_nom_liste l
USING taxonomie.cdnom_disparu AS cd
WHERE  l.cd_nom = cd.cd_nom AND  cd.cd_nom_remplacement IS NULL;


---- #################################################################################
----		MODIFICATIONS DES ATTRIBUTS ET DES MEDIAS
---- #################################################################################

--- Action : Update cd_ref no changes for attributes and medium
ALTER TABLE taxonomie.t_medias DISABLE TRIGGER USER;
UPDATE taxonomie.t_medias SET cd_ref = f_cd_ref
FROM tmp_taxref_changes.comp_grap
WHERE cas = 'update cd_ref' AND cd_ref = i_cd_ref;
ALTER TABLE taxonomie.t_medias ENABLE TRIGGER USER;

UPDATE taxonomie.cor_taxon_attribut SET cd_ref = f_cd_ref
FROM tmp_taxref_changes.comp_grap
WHERE cas = 'update cd_ref' AND cd_ref = i_cd_ref;

-- Action merge
UPDATE taxonomie.t_medias SET cd_ref = f_cd_ref
FROM tmp_taxref_changes.comp_grap
WHERE  cas = 'merge' AND cd_ref = i_cd_ref;

-- Suppression des potentiels doublons puis modification
WITH grp_del AS (
    SELECT f_cd_ref, id_attribut, count(*), array_agg(DISTINCT i_cd_ref) cd_refs, array_agg( DISTINCT valeur_attribut) AS valeur_attribut
    FROM taxonomie.cor_taxon_attribut ia
    JOIN tmp_taxref_changes.comp_grap cg
    ON
    	cd_ref = i_cd_ref
    GROUP BY f_cd_ref, id_attribut
    HAVING count(*) > 1
) , del AS (
    SELECT id_attribut as at, unnest(cd_refs[2:]) as i_cd_ref
    FROM grp_del
    WHERE array_length(valeur_attribut, 1) = 1
)
DELETE FROM taxonomie.cor_taxon_attribut
USING del
WHERE cd_ref = i_cd_ref  AND id_attribut = at;

UPDATE taxonomie.cor_taxon_attribut SET cd_ref = f_cd_ref
FROM tmp_taxref_changes.comp_grap
WHERE cas = 'merge' AND cd_ref = i_cd_ref;

------------------------------------------------
------------------------------------------------
-- REBUILD CONSTAINTS
------------------------------------------------
------------------------------------------------

UPDATE taxonomie.t_medias m  SET cd_ref = t.cd_ref
FROM taxonomie.taxref t
WHERE m.cd_ref = t.cd_nom AND  NOT t.cd_nom = t.cd_ref;


UPDATE taxonomie.cor_taxon_attribut m SET cd_ref =  t.cd_ref
FROM taxonomie.taxref t
WHERE m.cd_ref = t.cd_nom
  AND NOT t.cd_ref = t.cd_nom;



ALTER TABLE taxonomie.t_medias
  DROP CONSTRAINT IF EXISTS check_is_cd_ref,
  ADD CONSTRAINT check_is_cd_ref CHECK (cd_ref = taxonomie.find_cdref(cd_ref));

ALTER TABLE taxonomie.cor_taxon_attribut
  DROP CONSTRAINT IF EXISTS check_is_cd_ref,
  ADD CONSTRAINT check_is_cd_ref CHECK (cd_ref = taxonomie.find_cdref(cd_ref));

ALTER TABLE taxonomie.cor_nom_liste ADD CONSTRAINT cor_nom_listes_taxref_fkey FOREIGN KEY (cd_nom)
REFERENCES taxonomie.taxref(cd_nom) ON UPDATE CASCADE ON DELETE NO ACTION;
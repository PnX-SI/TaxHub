
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

ALTER TABLE taxonomie.bib_noms DROP CONSTRAINT fk_bib_nom_taxref;
ALTER TABLE taxonomie.taxref_protection_especes DROP CONSTRAINT taxref_protection_especes_cd_nom_fkey;

ALTER TABLE taxonomie.t_medias DROP CONSTRAINT check_cd_ref_is_ref;
ALTER TABLE taxonomie.bib_noms DROP CONSTRAINT check_is_valid_cd_ref;
ALTER TABLE taxonomie.cor_taxon_attribut DROP CONSTRAINT check_is_cd_ref;


------------------------------------------------
------------------------------------------------
-- 	UPDATE TAXREF
------------------------------------------------
------------------------------------------------
-- UPDATE EXISTING CD_NOM

UPDATE taxonomie.taxref t
   SET id_statut = fr, id_habitat = it.habitat::int, id_rang = it.rang, regne = it.regne, phylum = it.phylum, 
       classe = it.classe, ordre = it.ordre, famille = it.famille, cd_taxsup = it.cd_taxsup,
       cd_sup = it.cd_sup, cd_ref = it.cd_ref, 
       lb_nom = it.lb_nom, lb_auteur = it.lb_auteur, nom_complet = it.nom_complet,
       nom_complet_html = it.nom_complet_html, nom_valide = it.nom_valide, 
       nom_vern = it.nom_vern, nom_vern_eng = it.nom_vern_eng, group1_inpn = it.group1_inpn,
       group2_inpn = it.group2_inpn, sous_famille = it.sous_famille, 
       tribu = it.tribu, url = it.url
FROM taxonomie.import_taxref it
WHERE it.cd_nom  = t.cd_nom;


-- ADD NEW CD_NOM
INSERT INTO taxonomie.taxref(
            cd_nom, id_statut, id_habitat, id_rang, regne, phylum, classe, 
            ordre, famille, cd_taxsup, cd_sup, cd_ref, lb_nom, lb_auteur, 
            nom_complet, nom_complet_html, nom_valide, nom_vern, nom_vern_eng, 
            group1_inpn, group2_inpn, sous_famille, tribu, url)
SELECT it.cd_nom, it.fr, it.habitat::int, it.rang, it.regne, it.phylum, it.classe,
    it.ordre, it.famille, it.cd_taxsup, it.cd_sup, it.cd_ref, it.lb_nom, it.lb_auteur,
    it.nom_complet, it.nom_complet_html, it.nom_valide, it.nom_vern, it.nom_vern_eng,
    it.group1_inpn, it.group2_inpn, it.sous_famille, it.tribu, it.url
FROM taxonomie.import_taxref it
LEFT OUTER JOIN taxonomie.taxref t
ON it.cd_nom = t.cd_nom
WHERE t.cd_nom IS NULL;

-- DELETE MISSING CD_NOM
DELETE FROM taxonomie.taxref 
WHERE cd_nom IN (
	SELECT t.cd_nom
	FROM taxonomie.taxref t
	LEFT OUTER JOIN taxonomie.import_taxref it
	ON it.cd_nom = t.cd_nom
	WHERE it.cd_nom IS NULL
);



------------------------------------------------
------------------------------------------------
-- 	Delete bib_nom AND insert new ref
------------------------------------------------
------------------------------------------------

ALTER TABLE taxonomie.bib_noms DISABLE TRIGGER trg_refresh_nomfrancais_mv_taxref_list_forautocomplete;

UPDATE taxonomie.bib_noms n SET cd_ref = t.cd_ref
FROM taxonomie.taxref t
WHERE n.cd_nom = t.cd_nom;

DELETE FROM taxonomie.bib_noms WHERE cd_nom IN (
	SELECT n.cd_nom 
	FROM taxonomie.bib_noms n
	LEFT OUTER JOIN taxonomie.taxref t
	ON n.cd_nom = t.cd_nom
	WHERE t.cd_nom IS NULL
);

ALTER TABLE taxonomie.bib_noms DROP deleted; 
ALTER TABLE taxonomie.bib_noms DROP commentaire_disparition;



INSERT INTO taxonomie.bib_noms (cd_nom, cd_ref, nom_francais)
SELECT DISTINCT t.cd_nom, t.cd_ref, split_part(nom_vern, ',', 1)
FROM tmp_taxref_changes.comp_grap cg
LEFT OUTER JOIN taxonomie.bib_noms n
ON n.cd_nom = f_cd_ref
JOIN taxonomie.taxref t
ON f_cd_ref = t.cd_nom
WHERE n.cd_nom IS NULL;

ALTER TABLE taxonomie.bib_noms ENABLE TRIGGER trg_refresh_nomfrancais_mv_taxref_list_forautocomplete;




---- #################################################################################
---- #################################################################################
----		MODIFICATIONS DES ATTRIBUTS ET DES MEDIAS
---- #################################################################################
---- #################################################################################

--- Sauvegarde des données au cas ou 
CREATE TABLE tmp_taxref_changes.t_medias AS
SELECT * FROM taxonomie.t_medias;

CREATE TABLE tmp_taxref_changes.cor_taxon_attribut AS
SELECT * FROM taxonomie.cor_taxon_attribut;


--- Action : Update cd_ref no changes for attributes and medium


ALTER TABLE taxonomie.t_medias DISABLE TRIGGER ALL;
UPDATE taxonomie.t_medias SET cd_ref = f_cd_ref
FROM tmp_taxref_changes.comp_grap
WHERE cas = 'update cd_ref' aND cd_ref = i_cd_ref;
ALTER TABLE taxonomie.t_medias ENABLE TRIGGER ALL;

UPDATE taxonomie.cor_taxon_attribut SET cd_ref = f_cd_ref
FROM tmp_taxref_changes.comp_grap 
WHERE cas = 'update cd_ref' aND cd_ref = i_cd_ref;

--- Action : Keep attributes and medium

ALTER TABLE taxonomie.t_medias DISABLE TRIGGER ALL;
UPDATE taxonomie.t_medias SET cd_ref = f_cd_ref
FROM tmp_taxref_changes.comp_grap
WHERE action = 'Keep attributes and medium' aND cd_ref = i_cd_ref AND not i_cd_ref = f_cd_ref;
ALTER TABLE taxonomie.t_medias ENABLE TRIGGER ALL;

UPDATE taxonomie.cor_taxon_attribut SET cd_ref = f_cd_ref
FROM tmp_taxref_changes.comp_grap 
WHERE action = 'Keep attributes and medium' aND cd_ref = i_cd_ref AND not i_cd_ref = f_cd_ref;

--- Action : Loose attributes and medium
 --- => Nothing to do
/*
SELECT * 
FROM tmp_taxref_changes.comp_grap 
WHERE action ilike 'loo%'
*/

--- Action : duplicate
INSERT INTO taxonomie.cor_taxon_attribut(
            id_attribut, valeur_attribut, cd_ref)
SELECT a.id_attribut, a.valeur_attribut, f_cd_ref
FROM tmp_taxref_changes.comp_grap cg
JOIN  taxonomie.cor_taxon_attribut a
ON cg.i_cd_ref = a.cd_ref
WHERE action ilike '%Duplicate attibutes%';



ALTER TABLE taxonomie.t_medias DISABLE TRIGGER ALL;

INSERT INTO taxonomie.t_medias(cd_ref, titre, url, chemin, auteur, desc_media, date_media, is_public, supprime, id_type, source, licence)
SELECT f_cd_ref, titre, url, chemin, auteur, desc_media, date_media, is_public, supprime, id_type, source, licence
FROM tmp_taxref_changes.comp_grap cg
JOIN  taxonomie.t_medias a
ON cg.i_cd_ref = a.cd_ref
WHERE action ilike '%Duplicate medium%';

ALTER TABLE taxonomie.t_medias ENABLE TRIGGER ALL;

--- Action : Merge attributes if exists

ALTER TABLE taxonomie.t_medias DISABLE TRIGGER ALL;
UPDATE taxonomie.t_medias SET cd_ref = f_cd_ref
FROM tmp_taxref_changes.comp_grap
WHERE action ilike '%Merge attributes%'  aND cd_ref = i_cd_ref;
ALTER TABLE taxonomie.t_medias ENABLE TRIGGER ALL;

UPDATE taxonomie.cor_taxon_attribut SET cd_ref = f_cd_ref
FROM tmp_taxref_changes.comp_grap 
WHERE action ilike '%Merge attributes%' aND cd_ref = i_cd_ref;

------------------------------------------------
------------------------------------------------
-- REBUILD CONSTAINTS
------------------------------------------------
------------------------------------------------

ALTER TABLE taxonomie.bib_noms
  ADD CONSTRAINT fk_bib_nom_taxref FOREIGN KEY (cd_nom)
      REFERENCES taxonomie.taxref (cd_nom) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE taxonomie.t_medias
  ADD CONSTRAINT check_is_cd_ref CHECK (cd_ref = taxonomie.find_cdref(cd_ref));
  
ALTER TABLE taxonomie.bib_noms
  ADD CONSTRAINT check_is_cd_ref CHECK (cd_ref = taxonomie.find_cdref(cd_ref));

ALTER TABLE taxonomie.cor_taxon_attribut
  ADD CONSTRAINT check_is_cd_ref CHECK (cd_ref = taxonomie.find_cdref(cd_ref));

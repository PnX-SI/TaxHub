
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
ALTER TABLE taxonomie.bib_noms DROP CONSTRAINT IF EXISTS fk_bib_nom_taxref;

ALTER TABLE taxonomie.t_medias DROP CONSTRAINT IF EXISTS check_cd_ref_is_ref;
ALTER TABLE taxonomie.bib_noms DROP CONSTRAINT IF EXISTS check_is_valid_cd_ref;
ALTER TABLE taxonomie.cor_taxon_attribut DROP CONSTRAINT IF EXISTS check_is_cd_ref;

------------------------------------------------
------------------------------------------------
-- 	UPDATE TAXREF
------------------------------------------------
------------------------------------------------

-- CORRECTION
UPDATE taxonomie.import_taxref SET fr = NULL WHERE fr='';

-- UPDATE EXISTING CD_NOM
UPDATE taxonomie.taxref t
   SET id_statut = fr, id_habitat = it.habitat::int, id_rang = it.rang, regne = it.regne, phylum = it.phylum,
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
            cd_nom, id_statut, id_habitat, id_rang, regne, phylum, classe,
            ordre, famille, cd_taxsup, cd_sup, cd_ref, lb_nom, lb_auteur,
            nom_complet, nom_complet_html, nom_valide, nom_vern, nom_vern_eng,
            group1_inpn, group2_inpn, sous_famille, tribu, url, group3_inpn)
SELECT it.cd_nom, it.fr, it.habitat::int, it.rang, it.regne, it.phylum, it.classe,
    it.ordre, it.famille, it.cd_taxsup, it.cd_sup, it.cd_ref, it.lb_nom, it.lb_auteur,
    it.nom_complet, it.nom_complet_html, it.nom_valide, it.nom_vern, it.nom_vern_eng,
    it.group1_inpn, it.group2_inpn, it.sous_famille, it.tribu, it.url, it.group3_inpn
FROM taxonomie.import_taxref it
LEFT OUTER JOIN taxonomie.taxref t
ON it.cd_nom = t.cd_nom
WHERE t.cd_nom IS NULL;

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

------------------
--- cor_nom_liste
------------------
-- Remplacement des anciens cd_nom par leurs remplaçants dans cor_nom_liste
ALTER TABLE taxonomie.cor_nom_liste DROP CONSTRAINT cor_nom_liste_pkey;
ALTER TABLE  taxonomie.cor_nom_liste ADD tmp_id serial;

UPDATE taxonomie.cor_nom_liste l SET id_nom = repl_nom
FROM (
  SELECT  l.id_liste, l.id_nom, n.cd_nom_remplacement, n.cd_nom, repl.id_nom as repl_nom
  FROM taxonomie.cor_nom_liste l
  JOIN (
        SELECT n.id_nom, d.*
        FROM taxonomie.bib_noms n
        JOIN taxonomie.cdnom_disparu d
        ON n.cd_nom = d.cd_nom
    ) n
    ON n.id_nom = l.id_nom
    JOIN taxonomie.bib_noms repl
    ON repl.cd_nom = n.cd_nom_remplacement
  LEFT OUTER JOIN taxonomie.cor_nom_liste li
  ON li.id_liste = l.id_liste AND repl.id_nom = li.id_nom
  WHERE li.id_liste IS NULL
) a
WHERE a.id_liste = l.id_liste AND a.id_nom = l.id_nom;


--- Suppression des doublons
DELETE FROM taxonomie.cor_nom_liste
WHERE tmp_id IN (
	SELECT tmp_id FROM taxonomie.cor_nom_liste l
	JOIN  (
		SELECT  id_liste, id_nom, max(tmp_id)
		FROM taxonomie.cor_nom_liste
		GROUP BY id_liste, id_nom
		HAVING count(*) >1
	)a
	ON l.id_liste = a.id_liste AND l.id_nom = a.id_nom
		AND NOT tmp_id = max
);

-- supression dans les cas ou il n'y a pas de taxons de remplacements
DELETE FROM taxonomie.cor_nom_liste
WHERE id_nom IN (
  SELECT id_nom
  FROM taxonomie.bib_noms bn
  LEFT OUTER JOIN taxonomie.import_taxref it
  ON bn.cd_nom = it.cd_nom
  WHERE it.cd_nom IS NULL
);

-- Restauration de la clé primaire de cor_nom_liste
ALTER TABLE taxonomie.cor_nom_liste
  ADD CONSTRAINT cor_nom_liste_pkey PRIMARY KEY(id_nom, id_liste);

-- Suppression de la colonne temporaire cor_nom_liste
ALTER TABLE  taxonomie.cor_nom_liste DROP COLUMN tmp_id ;

-- Modification de la clé étrangère
ALTER TABLE taxonomie.cor_nom_liste DROP CONSTRAINT cor_nom_listes_bib_noms_fkey;
ALTER TABLE taxonomie.cor_nom_liste
  ADD CONSTRAINT cor_nom_listes_bib_noms_fkey FOREIGN KEY (id_nom)
  REFERENCES taxonomie.bib_noms(id_nom)
  ON UPDATE CASCADE
  ON DELETE  CASCADE;


------------------
--- bib_noms

------------------

-- Suppression des cd_nom disparus
DELETE FROM taxonomie.bib_noms WHERE cd_nom IN (
	SELECT t.cd_nom
	FROM taxonomie.taxref t
	LEFT OUTER JOIN taxonomie.import_taxref it
	ON it.cd_nom = t.cd_nom
  LEFT OUTER JOIN taxonomie.tmp_bib_noms_copy tbnc
  ON tbnc.cd_nom = t.cd_nom
  WHERE it.cd_nom IS NULL AND tbnc.deleted IS DISTINCT FROM FALSE
);



-- Ajout des noms de référence pour les cd_nom ayant changé de cd_ref
INSERT INTO taxonomie.bib_noms (cd_nom, cd_ref, nom_francais)
SELECT DISTINCT t.cd_nom, t.cd_ref, split_part(nom_vern, ',', 1)
FROM tmp_taxref_changes.comp_grap cg
LEFT OUTER JOIN taxonomie.bib_noms n
ON n.cd_nom = f_cd_ref
JOIN taxonomie.taxref t
ON f_cd_ref = t.cd_nom
WHERE n.cd_nom IS NULL;

------------- Cas avec cd_nom de remplacement
-- Ajout du cd_nom de remplacement quand il n'existait pas dans bib_noms
UPDATE taxonomie.bib_noms b
SET cd_nom = a.cd_nom_remplacement
FROM (
    SELECT
      n.cd_nom,
      n.cd_nom_remplacement
    FROM
      taxonomie.tmp_bib_noms_copy n
    LEFT OUTER JOIN taxonomie.bib_noms b ON n.cd_nom_remplacement = b.cd_nom
    WHERE
      NOT n.cd_nom_remplacement IS NULL
      AND b.cd_nom IS NULL
  ) a
WHERE b.cd_nom = a.cd_nom;

-- Suppression des cd_noms obsolètes
DELETE FROM taxonomie.bib_noms b
WHERE
  id_nom IN (
    SELECT b.id_nom
    FROM taxonomie.tmp_bib_noms_copy n
    JOIN taxonomie.bib_noms b ON n.cd_nom = b.cd_nom
    WHERE deleted = TRUE
  );

--Mise à jour des cd_ref
UPDATE taxonomie.bib_noms n SET cd_ref = t.cd_ref
FROM taxonomie.taxref t
WHERE n.cd_nom = t.cd_nom;


---- #################################################################################
---- #################################################################################
----		MODIFICATIONS DES ATTRIBUTS ET DES MEDIAS
---- #################################################################################
---- #################################################################################


--- Sauvegarde des données au cas ou
DROP TABLE IF EXISTS tmp_taxref_changes.t_medias;
CREATE TABLE tmp_taxref_changes.t_medias AS
SELECT * FROM taxonomie.t_medias;

DROP TABLE IF EXISTS tmp_taxref_changes.cor_taxon_attribut;
CREATE TABLE tmp_taxref_changes.cor_taxon_attribut AS
SELECT * FROM taxonomie.cor_taxon_attribut;


--- Action : Update cd_ref no changes for attributes and medium
ALTER TABLE taxonomie.t_medias DISABLE TRIGGER USER;
UPDATE taxonomie.t_medias SET cd_ref = f_cd_ref
FROM tmp_taxref_changes.comp_grap
WHERE cas = 'update cd_ref' AND cd_ref = i_cd_ref;
ALTER TABLE taxonomie.t_medias ENABLE TRIGGER USER;

UPDATE taxonomie.cor_taxon_attribut SET cd_ref = f_cd_ref
FROM tmp_taxref_changes.comp_grap
WHERE cas = 'update cd_ref' AND cd_ref = i_cd_ref;

--- Action : Keep attributes and medium
ALTER TABLE taxonomie.t_medias DISABLE TRIGGER USER;
UPDATE taxonomie.t_medias SET cd_ref = f_cd_ref
FROM tmp_taxref_changes.comp_grap
WHERE action = 'Keep attributes and medium' aND cd_ref = i_cd_ref AND not i_cd_ref = f_cd_ref;
ALTER TABLE taxonomie.t_medias ENABLE TRIGGER USER;

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
WHERE action ilike '%Duplicate attibutes%'
ON CONFLICT DO NOTHING;



ALTER TABLE taxonomie.t_medias DISABLE TRIGGER USER;

INSERT INTO taxonomie.t_medias(cd_ref, titre, url, chemin, auteur, desc_media, date_media, is_public, supprime, id_type, source, licence)
SELECT f_cd_ref, titre, url, chemin, auteur, desc_media, date_media, is_public, supprime, id_type, source, licence
FROM tmp_taxref_changes.comp_grap cg
JOIN  taxonomie.t_medias a
ON cg.i_cd_ref = a.cd_ref
WHERE action ilike '%Duplicate medium%';

ALTER TABLE taxonomie.t_medias ENABLE TRIGGER USER;

--- Action : Merge attributes if exists

ALTER TABLE taxonomie.t_medias DISABLE TRIGGER USER;
UPDATE taxonomie.t_medias SET cd_ref = f_cd_ref
FROM tmp_taxref_changes.comp_grap
WHERE action ilike '%Merge attributes%'  AND cd_ref = i_cd_ref;
ALTER TABLE taxonomie.t_medias ENABLE TRIGGER USER;


-- Suppression des potentiels doublons puis modification
WITH grp_del AS (
    SELECT f_cd_ref, id_attribut, count(*), array_agg( DISTINCT i_cd_ref) cd_refs, array_agg( DISTINCT valeur_attribut) AS valeur_attribut
    FROM taxonomie.cor_taxon_attribut ia
    JOIN tmp_taxref_changes.comp_grap cg
    ON  -- action ilike '%Merge attributes%' AND
    	cd_ref = i_cd_ref
    GROUP BY f_cd_ref, id_attribut
    HAVING count(*) > 1
) , del AS (
    SELECT id_attribut as at, unnest(cd_refs[2:])
    FROM grp_del
    WHERE array_length(valeur_attribut, 1) = 1
)
DELETE FROM taxonomie.cor_taxon_attribut
USING del
WHERE cd_ref = unnest  AND id_attribut = at;

UPDATE taxonomie.cor_taxon_attribut SET cd_ref = f_cd_ref
FROM tmp_taxref_changes.comp_grap
WHERE action ilike '%Merge attributes%' AND cd_ref = i_cd_ref;

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

ALTER TABLE taxonomie.bib_noms
  ADD CONSTRAINT fk_bib_nom_taxref FOREIGN KEY (cd_nom)
      REFERENCES taxonomie.taxref (cd_nom) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION;


ALTER TABLE taxonomie.t_medias
  DROP CONSTRAINT IF EXISTS check_is_cd_ref,
  ADD CONSTRAINT check_is_cd_ref CHECK (cd_ref = taxonomie.find_cdref(cd_ref));

ALTER TABLE taxonomie.cor_taxon_attribut
  DROP CONSTRAINT IF EXISTS check_is_cd_ref,
  ADD CONSTRAINT check_is_cd_ref CHECK (cd_ref = taxonomie.find_cdref(cd_ref));




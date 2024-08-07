
-- ----------------------------------------------------------------------
-- TAXREF IMPORT

-- ----------------------------------------------------------------------
-- Alter existing constraints
ALTER TABLE taxonomie.bib_noms DROP CONSTRAINT IF EXISTS fk_bib_nom_taxref ;
ALTER TABLE taxonomie.t_medias DROP CONSTRAINT IF EXISTS check_cd_ref_is_ref ;
ALTER TABLE taxonomie.bib_noms DROP CONSTRAINT IF EXISTS check_is_valid_cd_ref ;
ALTER TABLE taxonomie.cor_taxon_attribut DROP CONSTRAINT IF EXISTS check_is_cd_ref ;

-- ----------------------------------------------------------------------
-- UPDATE TAXREF

-- Fix TaxRef
UPDATE taxonomie.import_taxref SET
    fr = NULL
WHERE fr = '' ;

-- Update existing cd_nom
UPDATE taxonomie.taxref AS t SET
    id_statut = fr,
    id_habitat = it.habitat::int,
    id_rang = it.rang,
    regne = it.regne,
    phylum = it.phylum,
    classe = it.classe,
    ordre = it.ordre,
    famille = it.famille,
    cd_taxsup = it.cd_taxsup,
    cd_sup = it.cd_sup,
    cd_ref = it.cd_ref,
    lb_nom = it.lb_nom,
    lb_auteur = it.lb_auteur,
    nom_complet = it.nom_complet,
    nom_complet_html = it.nom_complet_html,
    nom_valide = it.nom_valide,
    nom_vern = it.nom_vern,
    nom_vern_eng = it.nom_vern_eng,
    group1_inpn = it.group1_inpn,
    group2_inpn = it.group2_inpn,
    sous_famille = it.sous_famille,
    tribu = it.tribu, url = it.url,
    group3_inpn = it.group3_inpn
FROM taxonomie.import_taxref AS it
WHERE it.cd_nom = t.cd_nom ;

-- Add new cd_nom
INSERT INTO taxonomie.taxref(
    cd_nom,
    id_statut,
    id_habitat,
    id_rang,
    regne,
    phylum,
    classe,
    ordre,
    famille,
    cd_taxsup,
    cd_sup,
    cd_ref,
    lb_nom,
    lb_auteur,
    nom_complet,
    nom_complet_html,
    nom_valide,
    nom_vern,
    nom_vern_eng,
    group1_inpn,
    group2_inpn,
    sous_famille,
    tribu,
    "url",
    group3_inpn
)
    SELECT
        it.cd_nom,
        it.fr,
        it.habitat::int,
        it.rang,
        it.regne,
        it.phylum,
        it.classe,
        it.ordre,
        it.famille,
        it.cd_taxsup,
        it.cd_sup,
        it.cd_ref,
        it.lb_nom,
        it.lb_auteur,
        it.nom_complet,
        it.nom_complet_html,
        it.nom_valide,
        it.nom_vern,
        it.nom_vern_eng,
        it.group1_inpn,
        it.group2_inpn,
        it.sous_famille,
        it.tribu,
        it.url,
        it.group3_inpn
    FROM taxonomie.import_taxref AS it
        LEFT JOIN taxonomie.taxref AS t
            ON it.cd_nom = t.cd_nom
    WHERE t.cd_nom IS NULL ;

-- Delete missing cd_nom if keep_cdnom is not specify
DO $$ BEGIN
    IF  :keep_cd_nom = FALSE THEN

        DELETE FROM taxonomie.taxref
        WHERE cd_nom IN (
            SELECT cd_nom
            FROM taxonomie.cdnom_disparu
        ) ;

    END IF ;
END $$ ;

-- ######################################################################
-- Impact of Taxref changes bib_noms and cor_nom_liste

-- ----------------------------------------------------------------------
-- cor_nom_liste :

-- Removing temporary the primary key of cor_list_name
ALTER TABLE taxonomie.cor_nom_liste DROP CONSTRAINT cor_nom_liste_pkey ;


-- Add a temporary column in cor_nom_liste
ALTER TABLE taxonomie.cor_nom_liste ADD tmp_id serial ;


-- Replacement of old cd_nom by their replacements
UPDATE taxonomie.cor_nom_liste AS l SET
    id_nom = repl_nom
FROM (
        SELECT
            l.id_liste,
            l.id_nom,
            n.cd_nom_remplacement,
            n.cd_nom,
            repl.id_nom AS repl_nom
        FROM taxonomie.cor_nom_liste AS l
            JOIN (
                  SELECT
                    n.id_nom,
                    d.*
                  FROM taxonomie.bib_noms AS n
                      JOIN taxonomie.cdnom_disparu AS d
                          ON n.cd_nom = d.cd_nom
            ) AS n
                ON n.id_nom = l.id_nom
            JOIN taxonomie.bib_noms AS repl
                ON repl.cd_nom = n.cd_nom_remplacement
            LEFT OUTER JOIN taxonomie.cor_nom_liste AS li
                ON (li.id_liste = l.id_liste AND repl.id_nom = li.id_nom)
        WHERE li.id_liste IS NULL
    ) AS a
WHERE a.id_liste = l.id_liste
    AND a.id_nom = l.id_nom ;


--- Delete duplicates from cor_nom_liste
DELETE FROM taxonomie.cor_nom_liste
WHERE tmp_id IN (
    SELECT tmp_id
    FROM taxonomie.cor_nom_liste AS l
        JOIN (
            SELECT
                id_liste,
                id_nom,
                max(tmp_id)
            FROM taxonomie.cor_nom_liste
            GROUP BY id_liste, id_nom
            HAVING count(*) > 1
        ) AS a
            ON (l.id_liste = a.id_liste AND l.id_nom = a.id_nom AND tmp_id != max)
) ;


-- Delete from cor_nom_liste where there are not replacement taxa
DELETE FROM taxonomie.cor_nom_liste
WHERE id_nom IN (
    SELECT bn.id_nom
    FROM taxonomie.bib_noms AS bn
        LEFT OUTER JOIN taxonomie.import_taxref AS it
            ON bn.cd_nom = it.cd_nom
    WHERE it.cd_nom IS NULL
) ;


-- Restoring the primary key of cor_list_name
ALTER TABLE taxonomie.cor_nom_liste
    ADD CONSTRAINT cor_nom_liste_pkey PRIMARY KEY(id_nom, id_liste) ;


-- Deleting the temporary column in cor_nom_liste
ALTER TABLE taxonomie.cor_nom_liste DROP COLUMN tmp_id ;


-- Changing cor_nom_liste the foreign key
ALTER TABLE taxonomie.cor_nom_liste DROP CONSTRAINT cor_nom_listes_bib_noms_fkey;
ALTER TABLE taxonomie.cor_nom_liste
    ADD CONSTRAINT cor_nom_listes_bib_noms_fkey FOREIGN KEY (id_nom)
    REFERENCES taxonomie.bib_noms(id_nom)
    ON UPDATE CASCADE
    ON DELETE CASCADE ;


-- ----------------------------------------------------------------------
-- bib_noms

-- Remove vanished cd_nom from bib_noms
DELETE FROM taxonomie.bib_noms
WHERE cd_nom IN (
    SELECT t.cd_nom
    FROM taxonomie.taxref t
        LEFT OUTER JOIN taxonomie.import_taxref AS it
            ON it.cd_nom = t.cd_nom
        LEFT OUTER JOIN taxonomie.tmp_bib_noms_copy AS tbnc
            ON tbnc.cd_nom = t.cd_nom
    WHERE it.cd_nom IS NULL
        AND tbnc.deleted IS DISTINCT FROM FALSE
) ;


-- Add reference names in bib_noms for cd_nom having changed from cd_ref
INSERT INTO taxonomie.bib_noms (cd_nom, cd_ref, nom_francais)
    SELECT DISTINCT
        t.cd_nom,
        t.cd_ref,
        split_part(nom_vern, ',', 1)
    FROM tmp_taxref_changes.comp_grap AS cg
        LEFT OUTER JOIN taxonomie.bib_noms AS n
            ON n.cd_nom = cg.f_cd_ref
        JOIN taxonomie.taxref AS t
            ON cg.f_cd_ref = t.cd_nom
    WHERE n.cd_nom IS NULL ;


-- Set replacement cd_nom when it did not exist in bib_noms
UPDATE taxonomie.bib_noms AS b SET
    cd_nom = a.cd_nom_remplacement
FROM (
    SELECT
        n.cd_nom,
        n.cd_nom_remplacement
    FROM taxonomie.tmp_bib_noms_copy AS n
        LEFT OUTER JOIN taxonomie.bib_noms AS b
            ON n.cd_nom_remplacement = b.cd_nom
    WHERE n.cd_nom_remplacement IS NOT NULL
        AND b.cd_nom IS NULL
  ) AS a
WHERE b.cd_nom = a.cd_nom ;

-- Remove obsolete cd_nom in bib_noms
DELETE FROM taxonomie.bib_noms
WHERE id_nom IN (
    SELECT b.id_nom
    FROM taxonomie.tmp_bib_noms_copy AS n
        JOIN taxonomie.bib_noms AS b
            ON n.cd_nom = b.cd_nom
    WHERE deleted = TRUE
) ;

-- TODO: why not used import_taxref !?
-- Update cd_ref in bib_noms
UPDATE taxonomie.bib_noms AS n SET
    cd_ref = t.cd_ref
FROM taxonomie.taxref AS t
WHERE n.cd_nom = t.cd_nom ;


-- ######################################################################
-- Impact of Taxref changes in Taxhub attributes and media


-- Backup t_medias and cor_taxon_attribut tables
DROP TABLE IF EXISTS tmp_taxref_changes.t_medias ;

CREATE TABLE tmp_taxref_changes.t_medias AS
    SELECT * FROM taxonomie.t_medias ;

DROP TABLE IF EXISTS tmp_taxref_changes.cor_taxon_attribut ;

CREATE TABLE tmp_taxref_changes.cor_taxon_attribut AS
    SELECT * FROM taxonomie.cor_taxon_attribut ;


-- Action: update cd_ref no changes for attributes and media
ALTER TABLE taxonomie.t_medias DISABLE TRIGGER USER ;

UPDATE taxonomie.t_medias SET
    cd_ref = f_cd_ref
FROM tmp_taxref_changes.comp_grap
WHERE cas = 'update cd_ref'
    AND cd_ref = i_cd_ref ;

ALTER TABLE taxonomie.t_medias ENABLE TRIGGER USER;

UPDATE taxonomie.cor_taxon_attribut SET
    cd_ref = f_cd_ref
FROM tmp_taxref_changes.comp_grap
WHERE cas = 'update cd_ref'
    AND cd_ref = i_cd_ref ;


--- Action: keep attributes and media
ALTER TABLE taxonomie.t_medias DISABLE TRIGGER USER;

UPDATE taxonomie.t_medias SET
    cd_ref = f_cd_ref
FROM tmp_taxref_changes.comp_grap
WHERE action = 'Keep attributes and medium'
    AND cd_ref = i_cd_ref
    AND i_cd_ref != f_cd_ref;

ALTER TABLE taxonomie.t_medias ENABLE TRIGGER USER;

UPDATE taxonomie.cor_taxon_attribut SET
    cd_ref = f_cd_ref
FROM tmp_taxref_changes.comp_grap
WHERE action = 'Keep attributes and medium'
    AND cd_ref = i_cd_ref
    AND i_cd_ref != f_cd_ref ;


-- Action: Loose attributes and medium
-- => Nothing to do
/*
SELECT *
FROM tmp_taxref_changes.comp_grap
WHERE action ILIKE 'loo%' ;
*/


-- Action: duplicate
INSERT INTO taxonomie.cor_taxon_attribut (id_attribut, valeur_attribut, cd_ref)
    SELECT a.id_attribut, a.valeur_attribut, f_cd_ref
    FROM tmp_taxref_changes.comp_grap AS cg
        JOIN taxonomie.cor_taxon_attribut AS a
            ON cg.i_cd_ref = a.cd_ref
    WHERE action ILIKE '%Duplicate attibutes%'
ON CONFLICT DO NOTHING ;


ALTER TABLE taxonomie.t_medias DISABLE TRIGGER USER ;

INSERT INTO taxonomie.t_medias(
    cd_ref,
    titre,
    "url",
    chemin,
    auteur,
    desc_media,
    date_media,
    is_public,
    supprime,
    id_type,
    source,
    licence
)
SELECT
    f_cd_ref,
    titre,
    "url",
    chemin,
    auteur,
    desc_media,
    date_media,
    is_public,
    supprime,
    id_type,
    source,
    licence
FROM tmp_taxref_changes.comp_grap AS cg
    JOIN taxonomie.t_medias AS a
        ON cg.i_cd_ref = a.cd_ref
WHERE action ILIKE '%Duplicate medium%' ;

ALTER TABLE taxonomie.t_medias ENABLE TRIGGER USER ;


--- Action : merge attributes if exists
ALTER TABLE taxonomie.t_medias DISABLE TRIGGER USER ;

UPDATE taxonomie.t_medias SET
    cd_ref = f_cd_ref
FROM tmp_taxref_changes.comp_grap
WHERE action ILIKE '%Merge attributes%'
    AND cd_ref = i_cd_ref
    AND i_cd_ref = ANY(f_array_agg) ;

ALTER TABLE taxonomie.t_medias ENABLE TRIGGER USER ;


-- Delete duplicates if exists and update attributs
WITH grp_del AS (
    SELECT
        f_cd_ref,
        id_attribut,
        count(*),
        array_agg(DISTINCT i_cd_ref) AS cd_refs,
        array_agg(DISTINCT valeur_attribut) AS valeur_attribut
    FROM taxonomie.cor_taxon_attribut AS ia
        JOIN tmp_taxref_changes.comp_grap AS cg
            ON cd_ref = i_cd_ref
    GROUP BY f_cd_ref, id_attribut
    HAVING count(*) > 1
),
del AS (
    SELECT
        id_attribut AS "at",
        unnest(cd_refs[2:])
    FROM grp_del
    WHERE array_length(valeur_attribut, 1) = 1
)
DELETE FROM taxonomie.cor_taxon_attribut
USING del
WHERE cd_ref = unnest
    AND id_attribut = "at" ;

UPDATE taxonomie.cor_taxon_attribut SET
    cd_ref = f_cd_ref
FROM tmp_taxref_changes.comp_grap
WHERE action ILIKE '%Merge attributes%'
    AND cd_ref = i_cd_ref
    AND i_cd_ref = ANY(f_array_agg) ;


-- ######################################################################
-- Rebuild constraints

UPDATE taxonomie.t_medias AS m SET
    cd_ref = t.cd_ref
FROM taxonomie.taxref AS t
WHERE m.cd_ref = t.cd_nom
    AND t.cd_nom != t.cd_ref ;

UPDATE taxonomie.cor_taxon_attribut AS m SET
    cd_ref = t.cd_ref
FROM taxonomie.taxref AS t
WHERE m.cd_ref = t.cd_nom
    AND t.cd_ref != t.cd_nom;

ALTER TABLE taxonomie.bib_noms
    ADD CONSTRAINT fk_bib_nom_taxref FOREIGN KEY (cd_nom)
    REFERENCES taxonomie.taxref (cd_nom) MATCH SIMPLE
    ON UPDATE NO ACTION ON DELETE NO ACTION ;

ALTER TABLE taxonomie.t_medias
    DROP CONSTRAINT IF EXISTS check_is_cd_ref,
    ADD CONSTRAINT check_is_cd_ref CHECK (cd_ref = taxonomie.find_cdref(cd_ref)) ;

ALTER TABLE taxonomie.cor_taxon_attribut
    DROP CONSTRAINT IF EXISTS check_is_cd_ref,
    ADD CONSTRAINT check_is_cd_ref CHECK (cd_ref = taxonomie.find_cdref(cd_ref)) ;



CREATE SCHEMA IF NOT EXISTS tmp_taxref_changes;

DROP TABLE IF EXISTS tmp_taxref_changes.comp_grap ;

-- Détection des changements taxonomiques cd_ref initial vs cd_ref final
-- Pour tous des cd_ref référencés dans la table t_medias ou cor_taxon_attribut
CREATE TABLE tmp_taxref_changes.comp_grap AS
WITH used_cd_ref AS (
    SELECT cd_ref FROM taxonomie.t_medias
    UNION
    SELECT cd_ref FROM taxonomie.cor_taxon_attribut
) , grappe_init AS (
    SELECT t.cd_ref
    FROM  taxonomie.taxref t
    JOIN used_cd_ref u
    ON u.cd_ref = t.cd_ref
    GROUP BY t.cd_ref
),
attribs AS (
    SELECT DISTINCT a.cd_ref, array_agg(id_attribut) as att_list, count(DISTINCT id_attribut) as att_nb
    FROM taxonomie.cor_taxon_attribut a
    WHERE NOT valeur_attribut ='{}' AND NOT valeur_attribut =''
    GROUP BY  a.cd_ref
),
media AS (
    SELECT DISTINCT cd_ref, count(id_media) as media_nb
    FROM taxonomie.t_medias
    GROUP BY cd_ref
)
SELECT i.cd_ref as i_cd_ref,
        f.cd_ref as f_cd_ref,
        att_list, att_nb, media_nb
FROM grappe_init i
LEFT OUTER JOIN  taxonomie.import_taxref f ON i.cd_ref = f.cd_nom
LEFT OUTER JOIN  attribs a ON i.cd_ref = a.cd_ref
LEFT OUTER JOIN  media m ON i.cd_ref = m.cd_ref;


ALTER TABLE tmp_taxref_changes.comp_grap ADD cas varchar(50);
ALTER TABLE tmp_taxref_changes.comp_grap ADD action varchar(500);

-- 'no changes' =  Cas ou il n'y a aucun changement
--  cd_ref initial correspond au cd_ref final
UPDATE tmp_taxref_changes.comp_grap SET cas = 'no changes'
WHERE i_cd_ref = f_cd_ref;

-- 'update cd_ref' = Cas ou le cd_ref est modifié
--  cd_ref initial différent du cd_ref final
UPDATE tmp_taxref_changes.comp_grap SET cas = 'update cd_ref'
WHERE NOT i_cd_ref = f_cd_ref;

-- 'merge' = Cas de fusion de cd_ref
-- quand 2 cd_ref initiaux ont le même cd_ref final
UPDATE tmp_taxref_changes.comp_grap SET cas = 'merge'
WHERE   f_cd_ref IN (
    SELECT f_cd_ref
    FROM  tmp_taxref_changes.comp_grap
    GROUP BY f_cd_ref
    HAVING count(*)>1
);

-- Détection des conflits
-- Cas de merge de cd_ref avec des attributs
-- Conflit si 2 cd_ref ont le même attribut avec des valeurs différentes
WITH c AS (
    SELECT f_cd_ref , array_agg(i_cd_ref) AS li_cd_ref
    FROM  tmp_taxref_changes.comp_grap
    WHERE cas  = 'merge' AND att_nb > 0
    GROUP BY f_cd_ref
    HAVING count(*) >1
), atts AS (
    SELECT DISTINCT *
    FROM taxonomie.cor_taxon_attribut a
    JOIN c ON a.cd_ref = ANY(c.li_cd_ref)
) , conflict_atts AS (
    SELECT
        f_cd_ref,
        atts.id_attribut,
        count(DISTINCT valeur_attribut),
        string_agg(DISTINCT CONCAT(nom_attribut::varchar, ': ' , valeur_attribut), ', ') AS atts
    FROM atts
    JOIN taxonomie.bib_attributs a
    ON a.id_attribut = atts.id_attribut
    GROUP BY f_cd_ref, atts.id_attribut
    HAVING count(DISTINCT valeur_attribut) >1
)
UPDATE tmp_taxref_changes.comp_grap c SET action = 'Conflicts with attributes : ' || atts
FROM conflict_atts a
WHERE a.f_cd_ref = c.f_cd_ref AND  cas = 'merge';

UPDATE tmp_taxref_changes.comp_grap SET action = 'no changes'
WHERE cas = 'no changes';


UPDATE tmp_taxref_changes.comp_grap SET action = 'update cd_ref'
WHERE cas = 'update cd_ref' ;

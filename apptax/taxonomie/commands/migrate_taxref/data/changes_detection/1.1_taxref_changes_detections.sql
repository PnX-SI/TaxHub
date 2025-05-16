

CREATE SCHEMA IF NOT EXISTS tmp_taxref_changes;

DROP TABLE IF EXISTS tmp_taxref_changes.comp_grap ;

-- Détection des changements taxonomiques cd_ref initial vs cd_ref final
-- Pour tous des cd_ref référencés dans la table t_medias ou cor_taxon_attribut
CREATE TABLE tmp_taxref_changes.comp_grap AS
WITH used_cd_ref AS (
    SELECT cd_ref FROM taxonomie.t_medias
    UNION
    SELECT cd_ref FROM taxonomie.cor_taxon_attribut
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
FROM used_cd_ref i
LEFT OUTER JOIN  taxonomie.import_taxref f ON i.cd_ref = f.cd_nom
LEFT OUTER JOIN  attribs a ON i.cd_ref = a.cd_ref
LEFT OUTER JOIN  media m ON i.cd_ref = m.cd_ref;


ALTER TABLE tmp_taxref_changes.comp_grap ADD cas varchar(50);
ALTER TABLE tmp_taxref_changes.comp_grap ADD action text;

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


-- Analyse des splits
DROP TABLE IF EXISTS tmp_taxref_changes.split_analyze ;

CREATE TABLE tmp_taxref_changes.split_analyze AS
WITH
grappe_init AS (
    SELECT b.cd_ref , array_agg(DISTINCT cnl.cd_nom ORDER BY cnl.cd_nom) as array_agg, count(DISTINCT cnl.cd_nom)
    FROM  taxonomie.taxref b
    JOIN taxonomie.cor_nom_liste cnl
    ON cnl.cd_nom = b.cd_nom
    GROUP BY b.cd_ref
),
grappe_final AS (
    SELECT new_ref.cd_ref , array_agg(DISTINCT cnl.cd_nom ORDER BY cnl.cd_nom) as array_agg, count(DISTINCT cnl.cd_nom)
    FROM taxonomie.import_taxref new_ref
    JOIN taxonomie.cor_nom_liste cnl
    ON cnl.cd_nom = new_ref.cd_nom
    GROUP BY new_ref.cd_ref
),
init_cdnom as (
	select distinct t1.cd_ref, t2.cd_nom, t1.array_agg, t1.count
	from taxonomie.cor_nom_liste t2
	JOIN taxonomie.taxref t ON t.cd_nom = t2.cd_nom
	JOIN grappe_init t1 ON t1.cd_ref = t.cd_ref
	order by 1,2),
final_cdnom as (
	select distinct t3.cd_ref, t2.cd_nom, t1.array_agg, t1.count
	from grappe_final t1, taxonomie.cor_nom_liste t2, taxonomie.import_taxref t3
	where t1.cd_ref = t3.cd_ref
	and t2.cd_nom = t3.cd_nom
	order by 1,2)
SELECT DISTINCT i.cd_ref as i_cd_ref, i.array_agg as i_array_agg, i.count as i_count,
        f.cd_ref as f_cd_ref, f.array_agg as f_array_agg, f.count as f_count
FROM init_cdnom i
LEFT OUTER JOIN  final_cdnom f ON i.cd_nom = f.cd_nom
WHERE NOT i.array_agg = f.array_agg;



ALTER TABLE tmp_taxref_changes.split_analyze ADD cas varchar(50);

UPDATE tmp_taxref_changes.split_analyze SET cas = 'split'
WHERE i_array_agg  @> f_array_agg AND NOT i_array_agg  = f_array_agg;

UPDATE tmp_taxref_changes.split_analyze SET cas = 'merge'
WHERE f_array_agg  @> i_array_agg AND NOT i_array_agg  = f_array_agg AND cas IS NULL;


UPDATE tmp_taxref_changes.split_analyze SET cas = 'split and merge'
WHERE NOT i_array_agg  @> f_array_agg --grappe initial non incluse totalement dans la grappe finale
    AND i_array_agg && f_array_agg -- grappe finale contient au moins un élément de la grappe initiale
    AND NOT i_array_agg  = f_array_agg AND cas IS NULL;

UPDATE tmp_taxref_changes.split_analyze SET cas = CONCAT(cas || ' - ', 'update cd_ref')
WHERE i_cd_ref = f_cd_ref;

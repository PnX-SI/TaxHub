
---- Type de changements

UPDATE tmp_taxref_changes.comp_grap SET grappe_change = NULL;
UPDATE tmp_taxref_changes.comp_grap SET grappe_change = 'no change'
WHERE sort(i_array_agg) = sort(f_array_agg) AND i_cd_ref = f_cd_ref;


UPDATE tmp_taxref_changes.comp_grap SET grappe_change = 'cas1'
WHERE sort(i_array_agg) = sort(f_array_agg) AND NOT i_cd_ref = f_cd_ref;


--Cas 2 i_array_agg = f_array_agg - cd_nom(s)
UPDATE tmp_taxref_changes.comp_grap SET grappe_change =  COALESCE(grappe_change|| ', ', '') || 'cas2'
WHERE sort(i_array_agg)  @> sort(f_array_agg) AND NOT sort(i_array_agg)  = sort(f_array_agg)  ;


--Cas 3 Quand 2 grappes initiales en forme une troisième
UPDATE tmp_taxref_changes.comp_grap SET grappe_change =  COALESCE(grappe_change|| ', ', '') ||  'cas3: 2 grappes'
WHERE i_cd_ref IN (
	SELECT a.i_cd_ref --a.i_array_agg | b.i_array_agg , *
	FROM tmp_taxref_changes.comp_grap a, tmp_taxref_changes.comp_grap b
	WHERE NOT a.i_cd_ref = b.i_cd_ref
		AND  sort(a.f_array_agg) = sort(b.f_array_agg)
		AND sort(a.i_array_agg | b.i_array_agg) = sort(a.f_array_agg)
);


UPDATE tmp_taxref_changes.comp_grap c SET grappe_change = COALESCE(grappe_change|| ', ', '') || 'cas3: f_cd_ref'
WHERE i_cd_ref IN (
	SELECT  i_cd_ref
	FROM tmp_taxref_changes.comp_grap
	WHERE f_cd_ref IN (SELECT f_cd_ref FROM tmp_taxref_changes.comp_grap GROUP BY f_cd_ref HAVING count(*) >1 )
);



UPDATE tmp_taxref_changes.comp_grap c SET cas = 'update cd_ref'
WHERE grappe_change ilike '%cas1%';

UPDATE tmp_taxref_changes.comp_grap c SET cas = 'merge'
WHERE grappe_change ilike '%cas3: 2 gr%';
UPDATE tmp_taxref_changes.comp_grap c SET cas = 'merge'
WHERE grappe_change ilike '%cas3%' AND i_count = 1 And f_count >1 ;

UPDATE tmp_taxref_changes.comp_grap c SET cas = 'split'
WHERE grappe_change = 'cas2';

UPDATE tmp_taxref_changes.comp_grap c SET cas = 'split and merge'
WHERE grappe_change ilike '%cas3%' and cas IS NULL;



---- ######### Actions qui vont être réalisées lors de la mise à jour de taxref

UPDATE  tmp_taxref_changes.comp_grap c SET action = NULL;

UPDATE  tmp_taxref_changes.comp_grap c SET action = 'no changes'
WHERE grappe_change = 'no change';

UPDATE  tmp_taxref_changes.comp_grap c SET action = 'Update cd_ref no changes for attributes and medium'
WHERE cas = 'update cd_ref';

-- Split

UPDATE tmp_taxref_changes.comp_grap c SET action = 'Keep attributes and medium'
WHERE  cas = 'split' AND i_cd_ref = f_cd_ref;

UPDATE tmp_taxref_changes.comp_grap c SET action = 'Loose attributes and medium now attach to ' || COALESCE(cd_ref_attr::varchar, 'No one')
FROM (
	SELECT l.*, k.i_cd_ref as cd_ref_attr
	FROM (
		SELECT *
		FROM tmp_taxref_changes.comp_grap
		WHERE  cas = 'split' AND NOT i_cd_ref = f_cd_ref
	) l
	LEFT OUTER JOIN (
		SELECT *
		FROM tmp_taxref_changes.comp_grap
		WHERE  cas = 'split' AND  i_cd_ref = f_cd_ref
	) k
	ON k.i_cd_ref = l.i_cd_ref
) a
WHERE a.i_cd_ref = c.i_cd_ref AND a.f_cd_ref = c.f_cd_ref;


-- Merge detection des conflits pour les attributs
WITH atts AS (
	SELECT DISTINCT *
	FROM taxonomie.cor_taxon_attribut a
	JOIN tmp_taxref_changes.comp_grap c
	ON a.cd_ref = c.i_cd_ref
	WHERE NOT valeur_attribut ='{}' AND NOT valeur_attribut =''
		AND cas = 'merge'
) , conflict_atts AS (
	SELECT f_cd_ref, id_attribut, count(DISTINCT valeur_attribut)
	FROM atts
	GROUP BY f_cd_ref, id_attribut
	HAVING count(DISTINCT valeur_attribut) >1
) , conflict_atts_text AS (
	SELECT f_cd_ref, string_agg(nom_attribut::varchar, ', ') as atts
	FROM conflict_atts c
	JOIN taxonomie.bib_attributs a
	ON a.id_attribut = c.id_attribut
	GROUP BY f_cd_ref
)
UPDATE tmp_taxref_changes.comp_grap c SET action = 'Conflicts with attributes : ' || atts
FROM conflict_atts_text a
WHERE a.f_cd_ref = c.f_cd_ref AND  cas = 'merge';

UPDATE tmp_taxref_changes.comp_grap c SET action = 'Merge attributes if exists'
WHERE cas = 'merge' AND action IS NULL;

-- Split and merge

UPDATE tmp_taxref_changes.comp_grap c SET action = 'Keep attributes and medium'
WHERE  cas = 'split and merge' AND i_cd_ref = f_cd_ref;

UPDATE tmp_taxref_changes.comp_grap c SET action = 'Loose attributes and medium now attach to ' || COALESCE(cd_ref_attr::varchar, 'No one')
FROM (
	SELECT l.*, k.i_cd_ref as cd_ref_attr
	FROM (
		SELECT *
		FROM tmp_taxref_changes.comp_grap
		WHERE  cas = 'split and merge' AND NOT i_cd_ref = f_cd_ref
	) l
	LEFT OUTER JOIN (
		SELECT *
		FROM tmp_taxref_changes.comp_grap
		WHERE  cas = 'split and merge' AND  i_cd_ref = f_cd_ref
	) k
	ON k.i_cd_ref = l.i_cd_ref
) a
WHERE a.i_cd_ref = c.i_cd_ref AND a.f_cd_ref = c.f_cd_ref;

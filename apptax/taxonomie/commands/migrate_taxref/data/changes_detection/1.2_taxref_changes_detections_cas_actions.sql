-- ----------------------------------------------------------------------
-- Add impacts of taxonomic changes in comp_grap table


-- ----------------------------------------------------------------------
-- Reset cd_nom cluster change
UPDATE tmp_taxref_changes.comp_grap SET grappe_change = NULL;


-- ----------------------------------------------------------------------
-- Set no change
UPDATE tmp_taxref_changes.comp_grap SET
    grappe_change = 'no change'
WHERE i_array_agg = f_array_agg
    AND i_cd_ref = f_cd_ref;


-- ----------------------------------------------------------------------
-- Set "case 1" : same cd_nom clusters but different cd_ref
UPDATE tmp_taxref_changes.comp_grap SET
    grappe_change = 'cas1'
WHERE i_array_agg = f_array_agg
    AND i_cd_ref != f_cd_ref ;


-- ----------------------------------------------------------------------
-- Set "case 2" : the new cd_nom cluster not contains all initial cd_nom
-- Formula : i_array_agg = f_array_agg - cd_nom(s)
UPDATE tmp_taxref_changes.comp_grap SET
    grappe_change = COALESCE(grappe_change || ', ', '') || 'cas2'
WHERE i_array_agg @> f_array_agg
    AND i_array_agg != f_array_agg ;


-- ----------------------------------------------------------------------
-- Set "case 3" : when 2 initial clusters form a third
WITH comp AS (
    SELECT
        a.i_cd_ref,
        a.f_array_agg,
        a.i_array_agg AS a_i_array_agg,
        b.i_array_agg AS b_i_array_agg,
        row_number() OVER (ORDER BY a.i_cd_ref ) AS tmp_id
    FROM tmp_taxref_changes.comp_grap AS a, tmp_taxref_changes.comp_grap AS b
    WHERE a.i_cd_ref != b.i_cd_ref
        AND a.f_array_agg = b.f_array_agg
),
unnest_grap AS (
    SELECT unnest(a_i_array_agg) AS cd, tmp_id
    FROM comp
    UNION
    SELECT unnest(b_i_array_agg) AS cd, tmp_id
    FROM comp
),
agg_grap AS (
    SELECT
        array_agg(cd ORDER BY cd) AS cd_agg,
        tmp_id
    FROM unnest_grap
    GROUP BY tmp_id
)
UPDATE tmp_taxref_changes.comp_grap SET
    grappe_change = COALESCE(grappe_change || ', ', '') ||  'cas3: 2 grappes'
WHERE i_cd_ref IN (
    SELECT i_cd_ref
    FROM agg_grap
        JOIN comp
            ON comp.tmp_id = agg_grap.tmp_id
    WHERE cd_agg = f_array_agg
);

UPDATE tmp_taxref_changes.comp_grap AS c SET
    grappe_change = COALESCE(grappe_change || ', ', '') || 'cas3: f_cd_ref'
WHERE i_cd_ref IN (
    SELECT i_cd_ref
    FROM tmp_taxref_changes.comp_grap
    WHERE f_cd_ref IN (
        SELECT f_cd_ref
        FROM tmp_taxref_changes.comp_grap
        GROUP BY f_cd_ref
        HAVING count(*) > 1
    )
);

UPDATE tmp_taxref_changes.comp_grap AS c SET
    cas = 'update cd_ref'
WHERE grappe_change ILIKE '%cas1%' ;


-- ----------------------------------------------------------------------
-- Case with 2 clusters of cd_nom which merge
UPDATE tmp_taxref_changes.comp_grap AS c SET
    cas = 'merge'
WHERE grappe_change ILIKE '%cas3: 2 gr%' ;


-- ----------------------------------------------------------------------
-- Case of merges with more than 2 clusters of cd_noms
WITH d AS (
    SELECT
        c.f_cd_ref,
        array_agg(DISTINCT i_array_agg) AS i_array_agg,
        array_agg(DISTINCT f_array_agg) AS f_array_agg
    FROM (
            SELECT
                f_cd_ref,
                UNNEST(i_array_agg) AS i_array_agg
            FROM tmp_taxref_changes.comp_grap
            WHERE grappe_change ILIKE '%cas3%'
                AND cas IS NULL
            ORDER BY f_cd_ref, UNNEST(i_array_agg)
        ) AS c
        JOIN (
            SELECT
                f_cd_ref,
                UNNEST(f_array_agg) AS f_array_agg
            FROM tmp_taxref_changes.comp_grap
            WHERE grappe_change ILIKE '%cas3%'
                AND cas IS NULL
            ORDER BY f_cd_ref, UNNEST(f_array_agg)
        ) AS f
            ON c.f_cd_ref = f.f_cd_ref
    GROUP BY c.f_cd_ref
)
UPDATE tmp_taxref_changes.comp_grap AS c SET
    cas = 'merge'
FROM d
WHERE d.f_cd_ref = c.f_cd_ref ;

UPDATE tmp_taxref_changes.comp_grap SET
    cas = 'split'
WHERE grappe_change = 'cas2' ;

UPDATE tmp_taxref_changes.comp_grap SET
    cas = 'split and merge'
WHERE grappe_change ILIKE '%cas3%'
    AND cas IS NULL ;

-- ----------------------------------------------------------------------
-- Medium & attributs: reset fields action, grappe_change and cas for analyse
UPDATE tmp_taxref_changes.comp_grap SET
    action = NULL ;

UPDATE tmp_taxref_changes.comp_grap SET
    action = 'no changes'
WHERE grappe_change = 'no change' ;

UPDATE tmp_taxref_changes.comp_grap SET
    action = 'Update cd_ref no changes for attributes and medium'
WHERE cas = 'update cd_ref' ;


-- ----------------------------------------------------------------------
-- Medium & attributs: case "split"
UPDATE tmp_taxref_changes.comp_grap SET
    action = 'Keep attributes and medium'
WHERE cas = 'split'
    AND i_cd_ref = f_cd_ref ;

UPDATE tmp_taxref_changes.comp_grap AS c SET
    action = 'Loose attributes and medium now attach to ' || COALESCE(cd_ref_attr::varchar, 'No one')
FROM (
    SELECT
        l.*,
        k.i_cd_ref AS cd_ref_attr
    FROM (
        SELECT *
        FROM tmp_taxref_changes.comp_grap
        WHERE cas = 'split'
            AND i_cd_ref != f_cd_ref
    ) AS l
    LEFT JOIN (
        SELECT *
        FROM tmp_taxref_changes.comp_grap
        WHERE cas = 'split'
            AND i_cd_ref = f_cd_ref
    ) AS k
    ON k.i_cd_ref = l.i_cd_ref
) AS a
WHERE a.i_cd_ref = c.i_cd_ref
    AND a.f_cd_ref = c.f_cd_ref ;


-- ----------------------------------------------------------------------
-- Medium & attributs: case "merge", detect conflicts for attributs
WITH atts AS (
    SELECT DISTINCT *
    FROM taxonomie.cor_taxon_attribut AS a
        JOIN tmp_taxref_changes.comp_grap AS c
            ON a.cd_ref = c.i_cd_ref
    WHERE valeur_attribut != '{}'
        AND valeur_attribut != ''
        AND cas = 'merge'
),
conflict_atts AS (
    SELECT
        f_cd_ref,
        id_attribut,
        count(DISTINCT valeur_attribut)
    FROM atts
    GROUP BY f_cd_ref, id_attribut
    HAVING count(DISTINCT valeur_attribut) > 1
),
conflict_atts_text AS (
    SELECT
        f_cd_ref,
        string_agg(nom_attribut::varchar, ', ') AS atts
    FROM conflict_atts AS c
        JOIN taxonomie.bib_attributs AS a
            ON a.id_attribut = c.id_attribut
    GROUP BY f_cd_ref
)
UPDATE tmp_taxref_changes.comp_grap AS c SET
    "action" = 'Conflicts with attributes : ' || atts
FROM conflict_atts_text AS a
WHERE a.f_cd_ref = c.f_cd_ref
    AND cas = 'merge' ;

UPDATE tmp_taxref_changes.comp_grap SET
    "action" = 'Merge attributes if exists'
WHERE cas = 'merge'
    AND "action" IS NULL ;


-- ----------------------------------------------------------------------
-- Medium & attributs: case "split and merge"
UPDATE tmp_taxref_changes.comp_grap AS c SET
    "action" = 'Keep attributes and medium'
WHERE cas = 'split and merge'
    AND i_cd_ref = f_cd_ref ;

UPDATE tmp_taxref_changes.comp_grap AS c SET
    "action" = 'Loose attributes and medium now attach to ' || COALESCE(cd_ref_attr::varchar, 'No one')
FROM (
    SELECT
        l.*,
        k.i_cd_ref AS cd_ref_attr
    FROM (
            SELECT *
            FROM tmp_taxref_changes.comp_grap
            WHERE cas = 'split and merge'
                AND i_cd_ref != f_cd_ref
        ) AS l
        LEFT JOIN (
            SELECT *
            FROM tmp_taxref_changes.comp_grap
            WHERE  cas = 'split and merge' AND  i_cd_ref = f_cd_ref
        ) AS k
            ON k.i_cd_ref = l.i_cd_ref
) AS a
WHERE a.i_cd_ref = c.i_cd_ref
    AND a.f_cd_ref = c.f_cd_ref ;

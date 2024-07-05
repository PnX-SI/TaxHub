-- ----------------------------------------------------------------------
-- Create temporary taxref schema
CREATE SCHEMA IF NOT EXISTS tmp_taxref_changes;


-- ----------------------------------------------------------------------
-- Intialize comp_grap table to store impacts of taxonomic changes

DROP TABLE IF EXISTS tmp_taxref_changes.comp_grap ;

-- TODO: why not used import_taxref for array_agg in "grappe_final" !?
CREATE TABLE tmp_taxref_changes.comp_grap AS
    WITH grappe_init AS (
        SELECT DISTINCT
            cd_ref,
            array_agg(cd_nom ORDER BY cd_nom) AS array_agg,
            count(DISTINCT cd_nom)
        FROM taxonomie.tmp_bib_noms_copy
        WHERE deleted != true
            AND cd_nom IS NOT NULL
        GROUP BY cd_ref
    ),
    grappe_final AS (
        SELECT DISTINCT
            it.cd_ref,
            array_agg(n.cd_nom ORDER BY n.cd_nom) AS array_agg,
            count(DISTINCT n.cd_nom)
        FROM taxonomie.tmp_bib_noms_copy AS n
            JOIN taxonomie.import_taxref AS it
                ON n.cd_nom = it.cd_nom
        WHERE n.deleted != true
            AND n.cd_nom IS NOT NULL
        GROUP BY it.cd_ref
    ),
    attribs AS (
        SELECT DISTINCT
            cd_ref,
            array_agg(id_attribut) AS att_list,
            count(DISTINCT id_attribut) AS att_nb
        FROM taxonomie.cor_taxon_attribut
        WHERE valeur_attribut !='{}'
            AND valeur_attribut != ''
        GROUP BY cd_ref
    ),
    media AS (
        SELECT DISTINCT
            cd_ref,
            count(id_media) AS media_nb
        FROM taxonomie.t_medias
        GROUP BY cd_ref
    ),
    init_cdnom AS (
        SELECT DISTINCT
            gi.cd_ref,
            n.cd_nom,
            gi.array_agg,
            gi.count
        FROM grappe_init AS gi, taxonomie.tmp_bib_noms_copy AS n
        WHERE gi.cd_ref = n.cd_ref
            AND n.deleted != true
            AND n.cd_nom IS NOT NULL
        ORDER BY 1, 2
    ),
    final_cdnom AS (
        SELECT DISTINCT
            it.cd_ref,
            n.cd_nom,
            gf.array_agg,
            gf.count
        FROM grappe_final AS gf, taxonomie.tmp_bib_noms_copy AS n, taxonomie.import_taxref AS it
        WHERE gf.cd_ref = it.cd_ref
            AND n.deleted != true
            AND n.cd_nom IS NOT NULL
            AND n.cd_nom = it.cd_nom
        ORDER BY 1, 2
    )
    SELECT DISTINCT
        i.cd_ref AS i_cd_ref,
        i.array_agg AS i_array_agg,
        i.count AS i_count,
        f.cd_ref AS f_cd_ref,
        f.array_agg AS f_array_agg,
        f.count AS f_count,
        att_list,
        att_nb,
        media_nb
    FROM init_cdnom AS i
        LEFT JOIN final_cdnom AS f
            ON i.cd_nom = f.cd_nom
        LEFT JOIN attribs AS a
            ON i.cd_ref = a.cd_ref
        LEFT JOIN media AS m
            ON i.cd_ref = m.cd_ref ;


ALTER TABLE tmp_taxref_changes.comp_grap ADD grappe_change varchar(250) ;
ALTER TABLE tmp_taxref_changes.comp_grap ADD "action" varchar(250) ;
ALTER TABLE tmp_taxref_changes.comp_grap ADD cas varchar(50) ;
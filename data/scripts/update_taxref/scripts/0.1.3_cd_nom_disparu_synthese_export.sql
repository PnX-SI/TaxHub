
-- Exporter les cd_nom disparus qui sont présents dans la synthese

DO $$
    BEGIN
        BEGIN
            COPY (
                SELECT DISTINCT s.cd_nom, string_agg(DISTINCT s.nom_cite, ',') as nom_cite, string_agg(DISTINCT ts.name_source::varchar, ',')  as sources, count(*) as nb, d.plus_recente_diffusion, d.cd_nom_remplacement, d.cd_raison_suppression
                FROM gn_synthese.synthese  s
                JOIN  gn_synthese.t_sources  ts
                ON ts.id_source = s.id_source
                LEFT OUTER JOIN taxonomie.cdnom_disparu d
                ON d.cd_nom = s.cd_nom
                LEFT OUTER JOIN taxonomie.import_taxref t
                ON s.cd_nom = t.cd_nom
                WHERE t.cd_nom IS NULL
                GROUP BY s.cd_nom, d.plus_recente_diffusion, d.cd_nom_remplacement, d.cd_raison_suppression
            )
                TO '/tmp/liste_cd_nom_disparus_synthese.csv'
            DELIMITER ';' CSV HEADER;
        EXCEPTION
            WHEN undefined_table THEN RAISE NOTICE 'Géonature non présent dans la base de données';
        END;
    END;
$$;
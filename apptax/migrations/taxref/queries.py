EXPORT_QUERIES_MISSING_CD_NOM_GN2_SYNTHESE = """
    SELECT DISTINCT s.cd_nom, string_agg(DISTINCT s.nom_cite, ',') as nom_cite, string_agg(DISTINCT ts.name_source::varchar, ',')  as sources, count(*) as nb, d.plus_recente_diffusion, d.cd_nom_remplacement, d.cd_raison_suppression
    FROM gn_synthese.synthese  s
    JOIN  gn_synthese.t_sources  ts
    ON ts.id_source = s.id_source
    LEFT OUTER JOIN taxonomie.cdnom_disparu d
    ON d.cd_nom = s.cd_nom
    LEFT OUTER JOIN taxonomie.import_taxref t
    ON s.cd_nom = t.cd_nom
    WHERE t.cd_nom IS NULL AND NOT s.cd_nom IS NULL
    GROUP BY s.cd_nom, d.plus_recente_diffusion, d.cd_nom_remplacement, d.cd_raison_suppression;
"""

EXPORT_QUERIES_MISSING_CD_NOMS_IN_BIB_NOMS = """
    SELECT s.cd_nom, t.nom_complet, d.plus_recente_diffusion, d.cd_nom_remplacement, d.cd_raison_suppression
    FROM taxonomie.cdnom_disparu d
    JOIN taxonomie.bib_noms s
    ON s.cd_nom = d.cd_nom
    JOIN taxonomie.taxref t
    ON s.cd_nom = t.cd_nom
    ORDER BY plus_recente_diffusion
"""

EXPORT_QUERIES_MISSING_CD_NOMS_IN_DB = """
    SELECT public.deps_test_fk_dependencies_cd_nom();

    SELECT fk.table_name, t.cd_nom, t.nom_complet, count(*) AS nb_occurence ,  d.plus_recente_diffusion, d.cd_nom_remplacement, d.cd_raison_suppression
    FROM tmp_taxref_changes.dps_fk_cd_nom fk
    JOIN taxonomie.taxref t
    ON t.cd_nom = fk.cd_nom
    JOIN taxonomie.cdnom_disparu d
    ON d.cd_nom = fk.cd_nom
    WHERE NOT fk.table_name='taxonomie.bdc_statut_taxons'
    GROUP BY fk.table_name, t.cd_nom, t.nom_complet,  d.plus_recente_diffusion, d.cd_nom_remplacement, d.cd_raison_suppression;
"""

# -- Décompte des changements de grappe de cd_nom qui vont être réalisé et les potentiels conflits qu'ils faur résoudre en amont
EXPORT_QUERIES_MODIFICATION_NB = """
    SELECT DISTINCT COALESCE(cas, 'no changes') AS cas, count(*)
    FROM tmp_taxref_changes.comp_grap c
    GROUP BY  cas
    ORDER BY count
"""
# -- Liste des changements  de grappe de cd_nom  avec potentiels conflicts et perte de données attributaires
EXPORT_QUERIES_MODIFICATION_LIST = """
    SELECT
        t.regne , t.group1_inpn , t.group2_inpn ,
        c.i_cd_ref, c.i_array_agg AS i_cd_nom_list, t.nom_valide AS i_nom_valid, i_count AS i_nb_cd_nom,
        f_cd_ref, f_array_agg AS f_cd_nom_list, it.nom_valide AS f_nom_valid, f_count AS f_nb_cd_nom,
        att_list, att_nb, media_nb, grappe_change, "action", cas
    FROM tmp_taxref_changes.comp_grap c
    JOIN taxonomie.taxref t
    ON t.cd_nom = c.i_cd_ref
    JOIN taxonomie.import_taxref it
    ON it.cd_nom = c.f_cd_ref
    WHERE NOT action ='no changes';
"""

EXPORT_QUERIES_CONFLICTS = """
    SELECT count(*) FROM tmp_taxref_changes.comp_grap WHERE action ilike '%Conflict%';
"""

# -- Test des cd_noms de la base présents dans la table cdnom_disparu
EXPORT_QUERIES_MISSING_CD_NOMS_IN_DB = """
    SELECT public.deps_test_fk_dependencies_cd_nom();

    SELECT
        fk.table_name, t.cd_nom, t.nom_complet, count(*) AS nb_occurence ,
        d.plus_recente_diffusion, d.cd_nom_remplacement, d.cd_raison_suppression
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
        c.i_cd_ref,   t.nom_valide AS i_nom_valid,
        f_cd_ref,  it.nom_valide AS f_nom_valid,
        att_list, att_nb, media_nb,   "action", cas
    FROM tmp_taxref_changes.comp_grap c
    JOIN taxonomie.taxref t
    ON t.cd_nom = c.i_cd_ref
    JOIN taxonomie.import_taxref it
    ON it.cd_nom = c.f_cd_ref
    WHERE NOT cas = 'no changes' OR cas IS NULL;
"""

EXPORT_QUERIES_CONFLICTS = """
    SELECT count(*) FROM tmp_taxref_changes.comp_grap WHERE action ilike '%Conflicts%';
"""


EXPORT_QUERIES_SPLIT = """
SELECT
    t.regne, t.group1_inpn, t.group2_inpn,
    s.i_cd_ref, s.i_array_agg AS i_cd_noms, t.nom_valide AS i_nom_valid,
    s.f_cd_ref, s.f_array_agg AS f_cd_noms, it.nom_valide AS f_nom_valid,
    cas
FROM tmp_taxref_changes.split_analyze s
JOIN taxonomie.taxref t
ON t.cd_nom = s.i_cd_ref
JOIN taxonomie.import_taxref it
ON it.cd_nom = s.f_cd_ref
WHERE not cas IS NULL;
"""

EXPORT_QUERIES_NB_SPLIT = """
SELECT count(*) FROM tmp_taxref_changes.split_analyze WHERE cas ilike '%split%'
"""

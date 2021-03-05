
TRUNCATE TABLE  taxonomie.taxref_bdc_statut_type ;
TRUNCATE TABLE  taxonomie.taxref_bdc_statut ;
ALTER TABLE taxonomie.taxref_bdc_statut DROP id;
---------------------------
---------------------------
-- COPY DATA
---------------------------
---------------------------

COPY taxonomie.taxref_bdc_statut_type
FROM  '/tmp/taxhub/BDC-Statuts-v14/BDC_STATUTS_TYPES_14.csv'
WITH  CSV HEADER;


COPY taxonomie.taxref_bdc_statut
FROM  '/tmp/taxhub/BDC-Statuts-v14/BDC_STATUTS_14.csv'
WITH  CSV HEADER
    ENCODING 'ISO 8859-1';



---------------------------
---------------------------

-- Suppression des doublons
-- 829 doublons lorsque l'on test tous les champs
ALTER TABLE taxonomie.taxref_bdc_statut ADD id serial;


WITH d AS (
    SELECT
        count(*), min(id), array_agg(id),  cd_nom, cd_ref, cd_sup, cd_type_statut, lb_type_statut, regroupement_type, code_statut, label_statut, rq_statut,
        cd_sig, cd_doc, lb_nom, lb_auteur, nom_complet_html, nom_valide_html, regne, phylum, classe, ordre, famille, group1_inpn,
        group2_inpn, lb_adm_tr, niveau_admin, cd_iso3166_1, cd_iso3166_2, full_citation, doc_url, thematique, type_value
    FROM taxonomie.taxref_bdc_statut
    GROUP BY
        cd_nom, cd_ref, cd_sup, cd_type_statut, lb_type_statut, regroupement_type, code_statut, label_statut, rq_statut,
        cd_sig, cd_doc, lb_nom, lb_auteur, nom_complet_html, nom_valide_html, regne, phylum, classe, ordre, famille, group1_inpn,
        group2_inpn, lb_adm_tr, niveau_admin, cd_iso3166_1, cd_iso3166_2, full_citation, doc_url, thematique, type_value
    HAVING count(*) >1
) , id_doublon AS (
    SELECT id as id_d
    FROM taxonomie.taxref_bdc_statut
    JOIN (SELECT min, unnest(array_agg) as to_del FROM d) d
    ON to_del = id
    WHERE NOT id = min
)
DELETE FROM  taxonomie.taxref_bdc_statut
WHERE id IN (SELECT id_d FROM id_doublon);


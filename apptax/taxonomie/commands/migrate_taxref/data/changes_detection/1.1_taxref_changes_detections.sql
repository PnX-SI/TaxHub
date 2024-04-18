---- #################################################################################
---- #################################################################################
----		Répercussion des changements taxonomiques
---- #################################################################################
---- #################################################################################

CREATE SCHEMA IF NOT EXISTS tmp_taxref_changes;

DROP TABLE IF EXISTS tmp_taxref_changes.comp_grap ;

CREATE TABLE tmp_taxref_changes.comp_grap AS
WITH grappe_init AS (
	SELECT distinct b.cd_ref , array_agg(cd_nom ORDER BY cd_nom) as array_agg, count(DISTINCT cd_nom)
	FROM  taxonomie.tmp_bib_noms_copy b
	WHERE NOT deleted = true and cd_nom is not null
	GROUP BY cd_ref
),
grappe_final AS (
	SELECT distinct t.cd_ref , array_agg(b.cd_nom ORDER BY b.cd_nom) as array_agg, count(DISTINCT b.cd_nom)
	FROM  taxonomie.tmp_bib_noms_copy b
	JOIN taxonomie.import_taxref t
	ON b.cd_nom = t.cd_nom
	WHERE NOT deleted = true and b.cd_nom is not null
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
),
init_cdnom as (
	select distinct t1.cd_ref, t2.cd_nom, t1.array_agg, t1.count
	from grappe_init t1, taxonomie.tmp_bib_noms_copy t2
	where t1.cd_ref = t2.cd_ref and NOT t2.deleted = true and t2.cd_nom is not null
	order by 1,2),
final_cdnom as (
	select distinct t3.cd_ref, t2.cd_nom, t1.array_agg, t1.count
	from grappe_final t1, taxonomie.tmp_bib_noms_copy t2, taxonomie.import_taxref t3
	where t1.cd_ref = t3.cd_ref and NOT t2.deleted = true and t2.cd_nom is not null
	and t2.cd_nom = t3.cd_nom
	order by 1,2)
SELECT distinct i.cd_ref as i_cd_ref, i.array_agg as i_array_agg, i.count as i_count,
		f.cd_ref as f_cd_ref, f.array_agg as f_array_agg, f.count as f_count,
		att_list, att_nb, media_nb
FROM init_cdnom i
LEFT OUTER JOIN  final_cdnom f ON i.cd_nom = f.cd_nom
LEFT OUTER JOIN  attribs a ON i.cd_ref = a.cd_ref
LEFT OUTER JOIN  media m ON i.cd_ref = m.cd_ref;


ALTER TABLE tmp_taxref_changes.comp_grap ADD grappe_change varchar(250);
ALTER TABLE tmp_taxref_changes.comp_grap ADD action varchar(250);
ALTER TABLE tmp_taxref_changes.comp_grap ADD cas varchar(50);


TRUNCATE TABLE taxonomie.vm_taxref_list_forautocomplete;
INSERT INTO taxonomie.vm_taxref_list_forautocomplete
SELECT t.cd_nom,
  t.cd_ref,
  t.search_name,
  t.nom_valide,
  t.lb_nom,
  t.regne,
  t.group2_inpn,
  cnl.id_liste
FROM (
  -- PARTIE NOM SCIENTIFIQUE : ici on prend TOUS les synonymes.
  SELECT t_1.cd_nom,
        t_1.cd_ref,
        concat(t_1.lb_nom, ' =  <i> ', t_1.nom_valide, '</i>', ' - [', t_1.id_rang, ' - ', t_1.cd_nom , ']') AS search_name,
        t_1.nom_valide,
        t_1.lb_nom,
        t_1.regne,
        t_1.group2_inpn
  FROM taxonomie.taxref t_1
  UNION
  -- PARTIE NOM FRANCAIS : ici on prend une seule fois (DISTINCT) dans taxref tous les taxons de références présents dans bib_noms (t_1.cd_nom = n.cd_ref)
  -- même si un taxon n'a qu'un synonyme et pas son taxon de référence dans bib_noms.
  -- On ne prend pas les taxons qui n'ont pas de nom français dans bib_noms,
  -- donc si un taxon n'a pas de nom français dans bib_noms, il n'est accessible que par son nom scientifique.
  SELECT DISTINCT
        t_1.cd_nom,
        t_1.cd_ref,
        concat(n.nom_francais, ' =  <i> ', t_1.nom_valide, '</i>', ' - [', t_1.id_rang, ' - ', t_1.cd_ref , ']' ) AS search_name,
        t_1.nom_valide,
        t_1.lb_nom,
        t_1.regne,
        t_1.group2_inpn
  FROM taxonomie.taxref t_1
  JOIN taxonomie.bib_noms n ON t_1.cd_nom = n.cd_ref AND n.nom_francais IS NOT null
) t
-- ici on filtre pour ne conserver que les taxons présents dans les listes (cor_nom_liste)
-- la jointure est double : sur le cd_nom + le cd_ref (pour les noms qui n'auraient pas leur taxon référence dans bib_noms)
JOIN taxonomie.bib_noms n ON n.cd_nom = t.cd_nom OR n.cd_ref = t.cd_ref
JOIN taxonomie.cor_nom_liste cnl ON cnl.id_nom = n.id_nom;


TRUNCATE TABLE taxonomie.vm_taxref_hierarchie;
INSERT INTO taxonomie.vm_taxref_hierarchie
SELECT tx.regne,tx.phylum,tx.classe,tx.ordre,tx.famille, tx.cd_nom, tx.cd_ref, lb_nom, trim(id_rang) AS id_rang, f.nb_tx_fm, o.nb_tx_or, c.nb_tx_cl, p.nb_tx_ph, r.nb_tx_kd FROM taxonomie.taxref tx
  LEFT JOIN (SELECT famille ,count(*) AS nb_tx_fm  FROM taxonomie.taxref where id_rang NOT IN ('FM') GROUP BY  famille) f ON f.famille = tx.famille
  LEFT JOIN (SELECT ordre ,count(*) AS nb_tx_or FROM taxonomie.taxref where id_rang NOT IN ('OR') GROUP BY  ordre) o ON o.ordre = tx.ordre
  LEFT JOIN (SELECT classe ,count(*) AS nb_tx_cl  FROM taxonomie.taxref where id_rang NOT IN ('CL') GROUP BY  classe) c ON c.classe = tx.classe
  LEFT JOIN (SELECT phylum ,count(*) AS nb_tx_ph  FROM taxonomie.taxref where id_rang NOT IN ('PH') GROUP BY  phylum) p ON p.phylum = tx.phylum
  LEFT JOIN (SELECT regne ,count(*) AS nb_tx_kd  FROM taxonomie.taxref where id_rang NOT IN ('KD') GROUP BY  regne) r ON r.regne = tx.regne
WHERE id_rang IN ('KD','PH','CL','OR','FM') AND tx.cd_nom = tx.cd_ref;

REFRESH MATERIALIZED VIEW taxonomie.vm_classe;
REFRESH MATERIALIZED VIEW taxonomie.vm_famille;
REFRESH MATERIALIZED VIEW taxonomie.vm_group1_inpn;
REFRESH MATERIALIZED VIEW taxonomie.vm_group2_inpn;
REFRESH MATERIALIZED VIEW taxonomie.vm_ordre;
REFRESH MATERIALIZED VIEW taxonomie.vm_phylum;
REFRESH MATERIALIZED VIEW taxonomie.vm_regne;

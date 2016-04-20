CREATE TABLE taxonomie.vm_taxref_hierarchie AS
SELECT tx.regne,tx.phylum,tx.classe,tx.ordre,tx.famille, tx.cd_nom, tx.cd_ref, lb_nom, trim(id_rang) AS id_rang, f.nb_tx_fm, o.nb_tx_or, c.nb_tx_cl, p.nb_tx_ph, r.nb_tx_kd FROM taxonomie.taxref tx
  LEFT JOIN (SELECT famille ,count(*) AS nb_tx_fm  FROM taxonomie.taxref where id_rang NOT IN ('FM') GROUP BY  famille) f ON f.famille = tx.famille
  LEFT JOIN (SELECT ordre ,count(*) AS nb_tx_or FROM taxonomie.taxref where id_rang NOT IN ('OR') GROUP BY  ordre) o ON o.ordre = tx.ordre
  LEFT JOIN (SELECT classe ,count(*) AS nb_tx_cl  FROM taxonomie.taxref where id_rang NOT IN ('CL') GROUP BY  classe) c ON c.classe = tx.classe
  LEFT JOIN (SELECT phylum ,count(*) AS nb_tx_ph  FROM taxonomie.taxref where id_rang NOT IN ('PH') GROUP BY  phylum) p ON p.phylum = tx.phylum
  LEFT JOIN (SELECT regne ,count(*) AS nb_tx_kd  FROM taxonomie.taxref where id_rang NOT IN ('KD') GROUP BY  regne) r ON r.regne = tx.regne
WHERE id_rang IN ('KD','PH','CL','OR','FM');

ALTER TABLE taxonomie.vm_taxref_hierarchie OWNER TO geonatuser;

ALTER TABLE ONLY taxonomie.vm_taxref_hierarchie ADD CONSTRAINT vm_taxref_hierarchie_pkey PRIMARY KEY (cd_nom);


CREATE OR REPLACE VIEW taxonomie.v_taxref_hierarchie_bibtaxons AS 
WITH mestaxons AS (SELECT tx.*  FROM taxonomie.taxref tx JOIN taxonomie.bib_taxons t ON t.cd_nom =  tx.cd_nom)
SELECT DISTINCT tx.regne,tx.phylum,tx.classe,tx.ordre,tx.famille, tx.cd_nom, tx.cd_ref, lb_nom, trim(id_rang) AS id_rang, f.nb_tx_fm, o.nb_tx_or, c.nb_tx_cl, p.nb_tx_ph, r.nb_tx_kd
FROM taxonomie.taxref tx
JOIN (SELECT DISTINCT tx.regne,tx.phylum,tx.classe,tx.ordre,tx.famille FROM mestaxons tx) a ON
        (a.regne = tx.regne AND tx.id_rang = 'KD')
        OR (a.phylum = tx.phylum AND tx.id_rang = 'PH')
        OR (a.classe = tx.classe AND tx.id_rang = 'CL')
        OR (a.ordre = tx.ordre AND tx.id_rang = 'OR')
        OR (a.famille = tx.famille AND tx.id_rang = 'FM')

  LEFT JOIN (SELECT famille ,count(*) AS nb_tx_fm  FROM mestaxons where id_rang NOT IN ('FM') GROUP BY  famille) f ON f.famille = tx.famille
  LEFT JOIN (SELECT ordre ,count(*) AS nb_tx_or FROM mestaxons where id_rang NOT IN ('OR') GROUP BY  ordre) o ON o.ordre = tx.ordre
  LEFT JOIN (SELECT classe ,count(*) AS nb_tx_cl  FROM mestaxons where id_rang NOT IN ('CL') GROUP BY  classe) c ON c.classe = tx.classe
  LEFT JOIN (SELECT phylum ,count(*) AS nb_tx_ph  FROM mestaxons where id_rang NOT IN ('PH') GROUP BY  phylum) p ON p.phylum = tx.phylum
  LEFT JOIN (SELECT regne ,count(*) AS nb_tx_kd  FROM mestaxons where id_rang NOT IN ('KD') GROUP BY  regne) r ON r.regne = tx.regne
WHERE id_rang IN ('KD','PH','CL','OR','FM');

ALTER TABLE taxonomie.v_taxref_hierarchie_bibtaxons OWNER TO geonatuser;


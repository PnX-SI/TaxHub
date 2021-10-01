-- Création des vues matérialisées de TaxHub en version 1.8.1
-- A partir de la version 1.9.0, les évolutions de la BDD sont gérées dans des migrations Alembic

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = taxonomie, pg_catalog, public;
----------------------
--MATERIALIZED VIEWS--
----------------------

-- FIXME Table? Not materialized view?
CREATE TABLE vm_taxref_hierarchie AS
SELECT tx.regne,tx.phylum,tx.classe,tx.ordre,tx.famille, tx.cd_nom, tx.cd_ref, lb_nom, trim(id_rang) AS id_rang, f.nb_tx_fm, o.nb_tx_or, c.nb_tx_cl, p.nb_tx_ph, r.nb_tx_kd FROM taxonomie.taxref tx
  LEFT JOIN (SELECT famille ,count(*) AS nb_tx_fm  FROM taxonomie.taxref where id_rang NOT IN ('FM') GROUP BY  famille) f ON f.famille = tx.famille
  LEFT JOIN (SELECT ordre ,count(*) AS nb_tx_or FROM taxonomie.taxref where id_rang NOT IN ('OR') GROUP BY  ordre) o ON o.ordre = tx.ordre
  LEFT JOIN (SELECT classe ,count(*) AS nb_tx_cl  FROM taxonomie.taxref where id_rang NOT IN ('CL') GROUP BY  classe) c ON c.classe = tx.classe
  LEFT JOIN (SELECT phylum ,count(*) AS nb_tx_ph  FROM taxonomie.taxref where id_rang NOT IN ('PH') GROUP BY  phylum) p ON p.phylum = tx.phylum
  LEFT JOIN (SELECT regne ,count(*) AS nb_tx_kd  FROM taxonomie.taxref where id_rang NOT IN ('KD') GROUP BY  regne) r ON r.regne = tx.regne
WHERE id_rang IN ('KD','PH','CL','OR','FM') AND tx.cd_nom = tx.cd_ref;
ALTER TABLE ONLY taxonomie.vm_taxref_hierarchie ADD CONSTRAINT vm_taxref_hierarchie_pkey PRIMARY KEY (cd_nom);


CREATE VIEW v_taxref_hierarchie_bibtaxons AS
 WITH mestaxons AS (
         SELECT tx_1.cd_nom,
            tx_1.id_statut,
            tx_1.id_habitat,
            tx_1.id_rang,
            tx_1.regne,
            tx_1.phylum,
            tx_1.classe,
            tx_1.ordre,
            tx_1.famille,
            tx_1.cd_taxsup,
            tx_1.cd_sup,
            tx_1.cd_ref,
            tx_1.lb_nom,
            tx_1.lb_auteur,
            tx_1.nom_complet,
            tx_1.nom_complet_html,
            tx_1.nom_valide,
            tx_1.nom_vern,
            tx_1.nom_vern_eng,
            tx_1.group1_inpn,
            tx_1.group2_inpn
           FROM taxonomie.taxref tx_1
             JOIN taxonomie.bib_noms t ON t.cd_nom = tx_1.cd_nom
        )
 SELECT DISTINCT tx.regne,
    tx.phylum,
    tx.classe,
    tx.ordre,
    tx.famille,
    tx.cd_nom,
    tx.cd_ref,
    tx.lb_nom,
    btrim(tx.id_rang::text) AS id_rang,
    f.nb_tx_fm,
    o.nb_tx_or,
    c.nb_tx_cl,
    p.nb_tx_ph,
    r.nb_tx_kd
   FROM taxonomie.taxref tx
     JOIN ( SELECT DISTINCT tx_1.regne,
            tx_1.phylum,
            tx_1.classe,
            tx_1.ordre,
            tx_1.famille
           FROM mestaxons tx_1) a ON a.regne::text = tx.regne::text AND tx.id_rang::text = 'KD'::text OR a.phylum::text = tx.phylum::text AND tx.id_rang::text = 'PH'::text OR a.classe::text = tx.classe::text AND tx.id_rang::text = 'CL'::text OR a.ordre::text = tx.ordre::text AND tx.id_rang::text = 'OR'::text OR a.famille::text = tx.famille::text AND tx.id_rang::text = 'FM'::text
     LEFT JOIN ( SELECT mestaxons.famille,
            count(*) AS nb_tx_fm
           FROM mestaxons
          WHERE mestaxons.id_rang::text <> 'FM'::text
          GROUP BY mestaxons.famille) f ON f.famille::text = tx.famille::text
     LEFT JOIN ( SELECT mestaxons.ordre,
            count(*) AS nb_tx_or
           FROM mestaxons
          WHERE mestaxons.id_rang::text <> 'OR'::text
          GROUP BY mestaxons.ordre) o ON o.ordre::text = tx.ordre::text
     LEFT JOIN ( SELECT mestaxons.classe,
            count(*) AS nb_tx_cl
           FROM mestaxons
          WHERE mestaxons.id_rang::text <> 'CL'::text
          GROUP BY mestaxons.classe) c ON c.classe::text = tx.classe::text
     LEFT JOIN ( SELECT mestaxons.phylum,
            count(*) AS nb_tx_ph
           FROM mestaxons
          WHERE mestaxons.id_rang::text <> 'PH'::text
          GROUP BY mestaxons.phylum) p ON p.phylum::text = tx.phylum::text
     LEFT JOIN ( SELECT mestaxons.regne,
            count(*) AS nb_tx_kd
           FROM mestaxons
          WHERE mestaxons.id_rang::text <> 'KD'::text
          GROUP BY mestaxons.regne) r ON r.regne::text = tx.regne::text
  WHERE (tx.id_rang::text = ANY (ARRAY['KD'::character varying::text, 'PH'::character varying::text, 'CL'::character varying::text, 'OR'::character varying::text, 'FM'::character varying::text])) AND tx.cd_nom = tx.cd_ref;

--Vue materialisée permettant d'améliorer fortement les performances des contraintes check sur les champs filtres 'regne' et 'group2_inpn'
CREATE MATERIALIZED VIEW taxonomie.vm_regne AS (SELECT DISTINCT regne FROM taxref tx) WITH DATA;
CREATE MATERIALIZED VIEW taxonomie.vm_phylum AS (SELECT DISTINCT phylum FROM taxref tx) WITH DATA;
CREATE MATERIALIZED VIEW taxonomie.vm_classe AS (SELECT DISTINCT classe FROM taxref tx) WITH DATA;
CREATE MATERIALIZED VIEW taxonomie.vm_ordre AS (SELECT DISTINCT ordre FROM taxref tx) WITH DATA;
CREATE MATERIALIZED VIEW taxonomie.vm_famille AS (SELECT DISTINCT famille FROM taxref tx) WITH DATA;
CREATE MATERIALIZED VIEW taxonomie.vm_group1_inpn AS (SELECT DISTINCT group1_inpn FROM taxref tx) WITH DATA;
CREATE MATERIALIZED VIEW taxonomie.vm_group2_inpn AS (SELECT DISTINCT group2_inpn FROM taxref tx) WITH DATA;

CREATE UNIQUE INDEX i_unique_ordre
  ON taxonomie.vm_ordre
  USING btree
  (ordre);
CREATE UNIQUE INDEX i_unique_phylum
  ON taxonomie.vm_phylum
  USING btree
  (phylum);
CREATE UNIQUE INDEX i_unique_regne
  ON taxonomie.vm_regne
  USING btree
  (regne);
CREATE UNIQUE INDEX i_unique_famille
  ON taxonomie.vm_famille
  USING btree
  (famille);
CREATE UNIQUE INDEX i_unique_classe
  ON taxonomie.vm_classe
  USING btree
  (classe);
CREATE UNIQUE INDEX i_unique_group1_inpn
  ON taxonomie.vm_group1_inpn
  USING btree
  (group1_inpn);
CREATE UNIQUE INDEX i_unique_group2_inpn
  ON taxonomie.vm_group2_inpn
  USING btree
  (group2_inpn);

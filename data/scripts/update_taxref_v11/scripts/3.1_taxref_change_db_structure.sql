-- ######################################################################
-- ######################################################################
--	APPLICATION DES CHANGEMENTS DE STRUCTURES POUR TAXREF
-- ######################################################################
-- ######################################################################

DROP VIEW taxonomie.v_taxref_hierarchie_bibtaxons;


INSERT INTO  taxonomie.bib_taxref_rangs (id_rang, nom_rang) VALUES ('PVCL', 'Parv-Classe');


ALTER TABLE taxonomie.taxref ADD sous_famille character varying(50);
ALTER TABLE taxonomie.taxref ADD tribu character varying(50);
ALTER TABLE taxonomie.taxref ADD url text;


ALTER TABLE taxonomie.taxref ALTER COLUMN  nom_vern TYPE character varying(1000) USING nom_vern::character varying(1000);
ALTER TABLE taxonomie.taxref ALTER COLUMN  lb_auteur TYPE character varying(250) USING lb_auteur::character varying(250);


CREATE OR REPLACE VIEW taxonomie.v_taxref_hierarchie_bibtaxons AS 
 WITH mestaxons AS (
         SELECT tx_1.cd_nom,
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

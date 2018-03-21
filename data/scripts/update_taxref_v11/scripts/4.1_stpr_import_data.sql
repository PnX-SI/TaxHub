
DROP TABLE IF EXISTS tmp_taxref_changes.import_protection_especes;
CREATE TABLE  tmp_taxref_changes.taxref_protection_articles_structure AS 
SELECT * 
FROM taxonomie.taxref_protection_articles_structure;

----PROTECTION
---import des statuts de protections
TRUNCATE TABLE taxonomie.taxref_protection_articles CASCADE;
COPY  taxonomie.taxref_protection_articles (
cd_protection, article, intitule, arrete, 
url_inpn, cd_doc, url, date_arrete, type_protection
)
FROM  '/tmp/taxhub/PROTECTION_ESPECES_TYPES_11.csv'
WITH  CSV HEADER;

---import des statuts de protections associés au taxon
DROP TABLE IF EXISTS taxonomie.import_protection_especes;
CREATE TABLE taxonomie.import_protection_especes (
	cd_nom int,
	cd_protection varchar(250),
	nom_cite text,
	syn_cite text,
	nom_francais_cite text,
	precisions varchar(500),
	cd_nom_cite int
);

COPY taxonomie.import_protection_especes
FROM  '/tmp/taxhub/PROTECTION_ESPECES_11.csv'
WITH  CSV HEADER;

TRUNCATE TABLE taxonomie.taxref_protection_especes;
INSERT INTO taxonomie.taxref_protection_especes
SELECT DISTINCT  p.* 
FROM  (
  SELECT cd_nom , cd_protection , string_agg(DISTINCT nom_cite, ',') nom_cite, 
    string_agg(DISTINCT syn_cite, ',')  syn_cite, string_agg(DISTINCT nom_francais_cite, ',')  nom_francais_cite,
    string_agg(DISTINCT precisions, ',')  precisions, cd_nom_cite 
  FROM   taxonomie.import_protection_especes
  GROUP BY cd_nom , cd_protection , cd_nom_cite 
) p
JOIN taxonomie.taxref t
USING(cd_nom) ;


INSERT INTO taxonomie.taxref_protection_articles_structure
SELECT tps.* 
FROM tmp_taxref_changes.taxref_protection_articles_structure tps
JOIN taxonomie.taxref_protection_articles
USING (cd_protection);

--- Recréation des constantes
ALTER TABLE taxonomie.taxref_protection_especes
  ADD CONSTRAINT taxref_protection_especes_cd_nom_fkey FOREIGN KEY (cd_nom)
      REFERENCES taxonomie.taxref (cd_nom) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE NO ACTION;

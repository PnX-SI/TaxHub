-------------------------------------------------------------
------------Insertion des dictionnaires taxref --------------
-------------------------------------------------------------

SET search_path = taxonomie, pg_catalog;
--
-- TOC entry 3270 (class 0 OID 17759)
-- Dependencies: 242
-- Data for Name: bib_taxref_habitats; Type: TABLE DATA; Schema: taxonomie; Owner: geonatuser
--

INSERT INTO bib_taxref_habitats (id_habitat, nom_habitat, desc_habitat) VALUES (1, 'Marin', 'Espèces vivant uniquement en milieu marin');
INSERT INTO bib_taxref_habitats (id_habitat, nom_habitat, desc_habitat) VALUES (2, 'Eau douce', 'Espèces vivant uniquement en milieu d''eau douce');
INSERT INTO bib_taxref_habitats (id_habitat, nom_habitat, desc_habitat) VALUES (3, 'Terrestre', 'Espèces vivant uniquement en milieu terrestre');
INSERT INTO bib_taxref_habitats (id_habitat, nom_habitat, desc_habitat) VALUES (5, 'Marin et Terrestre', 'Espèces effectuant une partie de leur cycle de vie en eau douce et l''autre partie en mer (espèces diadromes, amphidromes, anadromes ou catadromes)');
INSERT INTO bib_taxref_habitats (id_habitat, nom_habitat, desc_habitat) VALUES (6, 'Eau Saumâtre', 'Cas des pinnipèdes, des tortues et des oiseaux marins (par exemple)');
INSERT INTO bib_taxref_habitats (id_habitat, nom_habitat, desc_habitat) VALUES (7, 'Continental (Terrestre et/ou Eau douce)', 'Espèces vivant exclusivement en eau saumâtre');
INSERT INTO bib_taxref_habitats (id_habitat, nom_habitat, desc_habitat) VALUES (0, 'Non renseigné', null);
INSERT INTO bib_taxref_habitats (id_habitat, nom_habitat, desc_habitat) VALUES (4, 'Marin et Eau douce', 'Espèces continentales (non marines) dont on ne sait pas si elles sont terrestres et/ou d''eau douce (taxons provenant de Fauna Europaea)');
INSERT INTO bib_taxref_habitats (id_habitat, nom_habitat, desc_habitat) VALUES (8, 'Continental (Terrestre et Eau douce)', 'Espèces terrestres effectuant une partie de leur cycle en eau douce (odonates par exemple), ou fortement liées au milieu aquatique (loutre par exemple)');


--
-- TOC entry 3271 (class 0 OID 17762)
-- Dependencies: 243
-- Data for Name: bib_taxref_rangs; Type: TABLE DATA; Schema: taxonomie; Owner: geonatuser
--

INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('Dumm', 'Domaine');
INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('SPRG', 'Super-Règne');
INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('KD  ', 'Règne');
INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('SSRG', 'Sous-Règne');
INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('IFRG', 'Infra-Règne');
INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('PH  ', 'Phylum/Embranchement');
INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('SBPH', 'Sous-Phylum');
INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('IFPH', 'Infra-Phylum');
INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('DV  ', 'Division');
INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('SBDV', 'Sous-division');
INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('SPCL', 'Super-Classe');
INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('CLAD', 'Cladus');
INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('CL  ', 'Classe');
INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('SBCL', 'Sous-Classe');
INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('IFCL', 'Infra-classe');
INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('LEG ', 'Legio');
INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('COH ', 'Cohorte ');
INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('SPOR', 'Super-Ordre');
INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('OR  ', 'Ordre');
INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('SBOR', 'Sous-Ordre');
INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('IFOR', 'Infra-Ordre');
INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('SPFM', 'Super-Famille');
INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('FM  ', 'Famille');
INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('SBFM', 'Sous-Famille');
INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('SPTR', 'Super-Tribu');
INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('TR  ', 'Tribu');
INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('SSTR', 'Sous-Tribu');
INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('GN  ', 'Genre');
INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('SSGN', 'Sous-Genre');
INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('SC  ', 'Section');
INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('SBSC', 'Sous-Section');
INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('SER ', 'Série');
INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('SSER', 'Sous-Série');

INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('AGES', 'Agrégat');
INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('ES  ', 'Espèce');
INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('SMES', 'Semi-Espèce');
INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('MES ', 'Micro-Espèce');
INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('SSES', 'Sous-espèce');
INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('NAT ', 'Natio');
INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('VAR ', 'Variété');
INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('SVAR', 'Sous-Variété');
INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('FO  ', 'Forme');
INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('SSFO', 'Sous-Forme');
INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('FOES', 'Forma species');
INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('LIN ', 'Linea');
INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('CLO ', 'Clône');
INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('RACE', 'Race');
INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('CAR ', 'Cultivar');
INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('MO ', 'Morpha');
INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('AB  ', 'Abberatio');

INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('SSCO', '?');
INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('SCO ', '?');
INSERT INTO bib_taxref_rangs (id_rang, nom_rang) VALUES ('PVOR  ', '?');




--
-- TOC entry 3272 (class 0 OID 17765)
-- Dependencies: 244
-- Data for Name: bib_taxref_statuts; Type: TABLE DATA; Schema: taxonomie; Owner: geonatuser
--

INSERT INTO bib_taxref_statuts (id_statut, nom_statut) VALUES ('A', 'Absente');
INSERT INTO bib_taxref_statuts (id_statut, nom_statut) VALUES ('B', 'Accidentelle / Visiteuse');
INSERT INTO bib_taxref_statuts (id_statut, nom_statut) VALUES ('C', 'Cryptogène');
INSERT INTO bib_taxref_statuts (id_statut, nom_statut) VALUES ('D', 'Douteux');
INSERT INTO bib_taxref_statuts (id_statut, nom_statut) VALUES ('E', 'Endemique');
INSERT INTO bib_taxref_statuts (id_statut, nom_statut) VALUES ('F', 'Trouvé en fouille');
INSERT INTO bib_taxref_statuts (id_statut, nom_statut) VALUES ('I', 'Introduite');
INSERT INTO bib_taxref_statuts (id_statut, nom_statut) VALUES ('J', 'Introduite envahissante');
INSERT INTO bib_taxref_statuts (id_statut, nom_statut) VALUES ('M', 'Domestique / Introduite non établie');
INSERT INTO bib_taxref_statuts (id_statut, nom_statut) VALUES ('P', 'Présente');
INSERT INTO bib_taxref_statuts (id_statut, nom_statut) VALUES ('S', 'Subendémique');
INSERT INTO bib_taxref_statuts (id_statut, nom_statut) VALUES ('W', 'Disparue');
INSERT INTO bib_taxref_statuts (id_statut, nom_statut) VALUES ('X', 'Eteinte');
INSERT INTO bib_taxref_statuts (id_statut, nom_statut) VALUES ('Y', 'Introduite éteinte');
INSERT INTO bib_taxref_statuts (id_statut, nom_statut) VALUES ('Z', 'Endémique éteinte');
INSERT INTO bib_taxref_statuts (id_statut, nom_statut) VALUES ('0', 'Non renseigné');
INSERT INTO bib_taxref_statuts (id_statut, nom_statut) VALUES ('Q', 'Mentionné par erreur');
INSERT INTO bib_taxref_statuts (id_statut, nom_statut) VALUES (' ', 'Non précisé');

-------------------------------------------------------------
------------Insertion des données taxref	-------------
-------------------------------------------------------------

---import taxref--
TRUNCATE TABLE import_taxref;
COPY import_taxref (regne, phylum, classe, ordre, famille, group1_inpn, group2_inpn, 
          cd_nom, cd_taxsup, cd_sup, cd_ref, rang, lb_nom, lb_auteur, nom_complet, nom_complet_html,
          nom_valide, nom_vern, nom_vern_eng, habitat, fr, gf, mar, gua, 
          sm, sb, spm, may, epa, reu, taaf, pf, nc, wf, cli, url)
FROM  '/home/synthese/taxhubdev/data/inpn/TAXREFv90.txt'
WITH  CSV HEADER 
DELIMITER E'\t'  encoding 'LATIN1';

--insertion dans la table taxref
TRUNCATE TABLE taxref CASCADE;
INSERT INTO taxref
      SELECT cd_nom, fr as id_statut, habitat::int as id_habitat, rang as  id_rang, regne, phylum, classe, 
             ordre, famille, cd_taxsup, cd_sup, cd_ref, lb_nom, substring(lb_auteur, 1, 150),
             nom_complet, nom_complet_html,nom_valide, substring(nom_vern,1,255), nom_vern_eng, group1_inpn, group2_inpn
        FROM import_taxref;


----PROTECTION

---import des statuts de protections
TRUNCATE TABLE taxref_protection_articles CASCADE;
COPY taxref_protection_articles (
cd_protection, article, intitule, arrete, 
url_inpn, cd_doc, url, date_arrete, type_protection
)
FROM  '/home/synthese/taxhubdev/data/inpn/PROTECTION_ESPECES_TYPES_90.csv'
WITH  CSV HEADER 
DELIMITER ';'  encoding 'LATIN1';


---import des statuts de protections associés au taxon
CREATE TABLE import_protection_especes (
	CD_NOM int,
	CD_PROTECTION varchar(250),
	NOM_CITE text,
	SYN_CITE text,
	NOM_FRANCAIS_CITE text,
	PRECISIONS varchar(500),
	CD_NOM_CITE int
);

COPY import_protection_especes
FROM  '/home/synthese/taxhubdev/data/inpn/PROTECTION_ESPECES_90.csv'
WITH  CSV HEADER 
DELIMITER ';'  encoding 'LATIN1';


TRUNCATE TABLE taxref_protection_especes;
INSERT INTO taxref_protection_especes
SELECT DISTINCT  p.* 
FROM  (
  SELECT cd_nom , cd_protection , string_agg(DISTINCT nom_cite, ',') nom_cite, 
    string_agg(DISTINCT syn_cite, ',')  syn_cite, string_agg(DISTINCT nom_francais_cite, ',')  nom_francais_cite,
    string_agg(DISTINCT precisions, ',')  precisions, cd_nom_cite 
  FROM   import_protection_especes
  GROUP BY cd_nom , cd_protection , cd_nom_cite 
) p
JOIN taxref t
USING(cd_nom) ;

DROP TABLE  import_protection_especes;


--- Nettoyage des statuts de protections non utilisés
DELETE FROM  taxref_protection_articles
WHERE cd_protection IN (
  SELECT cd_protection 
  FROM taxref_protection_articles
  WHERE NOT cd_protection IN (SELECT DISTINCT cd_protection FROM  taxref_protection_especes)
);


--- Activation des textes valides pour la structure
--      Par défaut activation de tous les textes nationaux et internationaux
--          Pour des considérations locales à faire au cas par cas !!!
UPDATE  taxonomie.taxref_protection_articles SET concerne_mon_territoire = true
WHERE cd_protection IN (
	SELECT cd_protection
	FROM  taxonomie.taxref_protection_articles
	WHERE type_protection = 'Protection'
);

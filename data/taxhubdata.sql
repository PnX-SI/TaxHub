SET search_path = taxonomie, pg_catalog;

--
-- TOC entry 3122 (class 0 OID 126729)
-- Dependencies: 194
-- Data for Name: bib_taxons; Type: TABLE DATA; Schema: taxonomie; Owner: -
--

INSERT INTO bib_taxons (id_taxon, cd_nom, nom_latin, nom_francais, auteur) VALUES (704, 67111, 'Alburnus alburnus', 'Ablette', '(Linnaeus, 1758)');
INSERT INTO bib_taxons (id_taxon, cd_nom, nom_latin, nom_francais, auteur) VALUES (64, 60612, 'Lynx lynx', 'Lynx boréal', '(Linnaeus, 1758)');
INSERT INTO bib_taxons (id_taxon, cd_nom, nom_latin, nom_francais, auteur) VALUES (23, 351, 'Rana temporaria', 'Grenouille rousse', 'Linnaeus, 1758');
INSERT INTO bib_taxons (id_taxon, cd_nom, nom_latin, nom_francais, auteur) VALUES (1950, 8326, 'Cicindela hybrida', 'Cicindela hybrida', 'Linné, 1758');
INSERT INTO bib_taxons (id_taxon, cd_nom, nom_latin, nom_francais, auteur) VALUES (2804, 11165, 'Coccinella septempunctata', 'Coccinella septempunctata', 'Linnaeus, 1758');
INSERT INTO bib_taxons (id_taxon, cd_nom, nom_latin, nom_francais, auteur) VALUES (816, 18437, 'Austropotamobius pallipes', 'Ecrevisse à pieds blancs', '(Lereboullet, 1858)');
INSERT INTO bib_taxons (id_taxon, cd_nom, nom_latin, nom_francais, auteur) VALUES (100001, 81065, 'Alchemilla decumbens', 'Alchémille rampante', 'Buser, 1894 ');
INSERT INTO bib_taxons (id_taxon, cd_nom, nom_latin, nom_francais, auteur) VALUES (100002, 95186, 'Dittrichia graveolens', 'Inule fétide', '(L.) Greuter, 1973');


--
-- 
-- Data for Name: bib_attributs; Type: TABLE DATA; Schema: taxonomie; Owner: -
--

INSERT INTO bib_attributs (id_attribut ,nom_attribut, label_attribut, liste_valeur_attribut, obligatoire, desc_attribut, type_attribut, regne, group2_inpn) VALUES (1, 'patrimonial', 'Patrimonial', 'oui;non',true,'Défini si le taxon est patrimonial pour le territoire','string',null,null);
INSERT INTO bib_attributs (id_attribut ,nom_attribut, label_attribut, liste_valeur_attribut, obligatoire, desc_attribut, type_attribut, regne, group2_inpn) VALUES (2, 'protection_stricte', 'Protégé', 'oui;non',true,'Défini si le taxon bénéficie d''une protection juridique stricte pour le territoire','string',null,null);


--
-- 
-- Data for Name: cor_taxon_attribut; Type: TABLE DATA; Schema: taxonomie; Owner: -
--

INSERT INTO cor_taxon_attribut (id_taxon ,id_attribut, valeur_attribut) VALUES (704, 1, 'non');
INSERT INTO cor_taxon_attribut (id_taxon ,id_attribut, valeur_attribut) VALUES (704, 2, 'non');
INSERT INTO cor_taxon_attribut (id_taxon ,id_attribut, valeur_attribut) VALUES (64, 1, 'oui');
INSERT INTO cor_taxon_attribut (id_taxon ,id_attribut, valeur_attribut) VALUES (64, 2, 'oui');
INSERT INTO cor_taxon_attribut (id_taxon ,id_attribut, valeur_attribut) VALUES (23, 1, 'non');
INSERT INTO cor_taxon_attribut (id_taxon ,id_attribut, valeur_attribut) VALUES (23, 2, 'oui');
INSERT INTO cor_taxon_attribut (id_taxon ,id_attribut, valeur_attribut) VALUES (1950, 1, 'non');
INSERT INTO cor_taxon_attribut (id_taxon ,id_attribut, valeur_attribut) VALUES (1950, 2, 'non');
INSERT INTO cor_taxon_attribut (id_taxon ,id_attribut, valeur_attribut) VALUES (2804, 1, 'non');
INSERT INTO cor_taxon_attribut (id_taxon ,id_attribut, valeur_attribut) VALUES (2804, 2, 'non');
INSERT INTO cor_taxon_attribut (id_taxon ,id_attribut, valeur_attribut) VALUES (816, 1, 'non');
INSERT INTO cor_taxon_attribut (id_taxon ,id_attribut, valeur_attribut) VALUES (816, 2, 'oui');
INSERT INTO cor_taxon_attribut (id_taxon ,id_attribut, valeur_attribut) VALUES (100001, 1, 'non');
INSERT INTO cor_taxon_attribut (id_taxon ,id_attribut, valeur_attribut) VALUES (100001, 2, 'non');
INSERT INTO cor_taxon_attribut (id_taxon ,id_attribut, valeur_attribut) VALUES (100002, 1, 'non');
INSERT INTO cor_taxon_attribut (id_taxon ,id_attribut, valeur_attribut) VALUES (100002, 2, 'non');

--
-- 
-- Data for Name: bib_listes; Type: TABLE DATA; Schema: taxonomie; Owner: -
--

INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto) VALUES (1, 'Amphibiens',null, 'images/pictos/amphibien.gif');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto) VALUES (2, 'Vers',null, 'images/pictos/nopicto.gif');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto) VALUES (3, 'Entognathes',null, 'images/pictos/nopicto.gif');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto) VALUES (4, 'Echinodermes',null, 'images/pictos/nopicto.gif');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto) VALUES (5, 'Crustacés',null, 'images/pictos/ecrevisse.gif');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto) VALUES (7, 'Pycnogonides',null, 'images/pictos/nopicto.gif');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto) VALUES (8, 'Gastéropodes',null, 'images/pictos/nopicto.gif');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto) VALUES (9, 'Insectes',null, 'images/pictos/insecte.gif');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto) VALUES (10, 'Bivalves',null, 'images/pictos/nopicto.gif');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto) VALUES (11, 'Mammifères',null, 'images/pictos/mammifere.gif');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto) VALUES (12, 'Oiseaux',null, 'images/pictos/oiseau.gif');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto) VALUES (13, 'Poissons',null, 'images/pictos/poisson.gif');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto) VALUES (14, 'Reptiles',null, 'images/pictos/reptile.gif');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto) VALUES (15, 'Myriapodes',null, 'images/pictos/nopicto.gif');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto) VALUES (16, 'Arachnides',null, 'images/pictos/araignee.gif');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto) VALUES (20, 'Rotifères',null, 'images/pictos/nopicto.gif');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto) VALUES (21, 'Tardigrades',null, 'images/pictos/nopicto.gif');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto) VALUES (101, 'Mollusques',null, 'images/pictos/mollusque.gif');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto) VALUES (301, 'Bryophytes',null, 'images/pictos/mousse.gif');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto) VALUES (302, 'Lichens',null, 'images/pictos/nopicto.gif');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto) VALUES (303, 'Algues',null, 'images/pictos/nopicto.gif');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto) VALUES (305, 'Ptéridophytes',null, 'images/pictos/nopicto.gif');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto) VALUES (306, 'Monocotylédones',null, 'images/pictos/nopicto.gif');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto) VALUES (307, 'Dycotylédones',null, 'images/pictos/nopicto.gif');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto) VALUES (666, 'Nuisibles',null, 'images/pictos/nopicto.gif');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto) VALUES (1001, 'Faune vertébrée', 'Liste servant à l''affichage des taxons de la faune vertébré pouvant être saisis', 'images/pictos/nopicto.gif');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto) VALUES (1002, 'Faune invertébrée', 'Liste servant à l''affichage des taxons de la faune invertébré pouvant être saisis', 'images/pictos/nopicto.gif');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto) VALUES (1003, 'Flore', 'Liste servant à l''affichage des taxons de la flore pouvant être saisis', 'images/pictos/nopicto.gif');
INSERT INTO bib_listes (id_liste ,nom_liste,desc_liste,picto) VALUES (1004, 'Fonge','Liste servant à l''affichage des taxons de la fonge pouvant être saisis', 'images/pictos/champignon.gif');


--
-- 
-- Data for Name: cor_taxon_liste; Type: TABLE DATA; Schema: taxonomie; Owner: -
--

INSERT INTO cor_taxon_liste (id_taxon ,id_liste) VALUES (704, 1001);
INSERT INTO cor_taxon_liste (id_taxon ,id_liste) VALUES (64, 1001);
INSERT INTO cor_taxon_liste (id_taxon ,id_liste) VALUES (23, 1001);
INSERT INTO cor_taxon_liste (id_taxon ,id_liste) VALUES (1950, 1002);
INSERT INTO cor_taxon_liste (id_taxon ,id_liste) VALUES (2804, 1002);
INSERT INTO cor_taxon_liste (id_taxon ,id_liste) VALUES (816, 1002);
INSERT INTO cor_taxon_liste (id_taxon ,id_liste) VALUES (23, 1);
INSERT INTO cor_taxon_liste (id_taxon ,id_liste) VALUES (64, 11);
INSERT INTO cor_taxon_liste (id_taxon ,id_liste) VALUES (704, 13);
INSERT INTO cor_taxon_liste (id_taxon ,id_liste) VALUES (816, 5);
INSERT INTO cor_taxon_liste (id_taxon ,id_liste) VALUES (1950, 9);
INSERT INTO cor_taxon_liste (id_taxon ,id_liste) VALUES (2804,9);
INSERT INTO cor_taxon_liste (id_taxon ,id_liste) VALUES (100001,1003);
INSERT INTO cor_taxon_liste (id_taxon ,id_liste) VALUES (100002,1003);
INSERT INTO cor_taxon_liste (id_taxon ,id_liste) VALUES (100001,306);
INSERT INTO cor_taxon_liste (id_taxon ,id_liste) VALUES (100002,307);

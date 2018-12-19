
SET search_path = utilisateurs, pg_catalog;

-- Insérer les applications de base liées à TaxHub
INSERT INTO t_applications (code_application, nom_application, desc_application, id_parent) VALUES 
('TH', 'TaxHub', 'Application permettant d''administrer les taxons.', NULL)
;
SELECT pg_catalog.setval('t_applications_id_application_seq', (SELECT max(id_application)+1 FROM t_applications), false);	

--Définir les profils utilisables pour TaxHub
INSERT INTO cor_profil_for_app (id_profil, id_application) VALUES
(2, (SELECT id_application FROM utilisateurs.t_applications WHERE code_application = 'TH'))
,(3, (SELECT id_application FROM utilisateurs.t_applications WHERE code_application = 'TH')) 
,(4, (SELECT id_application FROM utilisateurs.t_applications WHERE code_application = 'TH'))
,(6, (SELECT id_application FROM utilisateurs.t_applications WHERE code_application = 'TH'))
;

INSERT INTO cor_role_app_profil (id_role, id_application, id_profil) VALUES
(9, (SELECT id_application FROM utilisateurs.t_applications WHERE code_application = 'TH'), 6) --admin Taxhub
;

-- Vue permettant de simuler le contenu de la table "t_menus" de la V1
CREATE OR REPLACE VIEW t_menus AS 
SELECT 
 id_liste AS id_menu,
 nom_liste AS nom_menu,
 desc_liste AS desc_menu,
 null::integer AS id_application
FROM utilisateurs.t_listes
;

-- Vue permettant de simuler le contenu de la table "cor_role_menu" de la V1
CREATE OR REPLACE VIEW cor_role_menu AS 
SELECT 
DISTINCT
crl.id_role,
crl.id_liste AS id_menu
FROM utilisateurs.cor_role_liste crl;	 

-- Vue permettant de simuler le contenu de la table "bib_droits" de la V1
CREATE OR REPLACE VIEW bib_droits AS 
SELECT 
 id_profil AS id_droit,
 nom_profil AS nom_droit,
 desc_profil AS desc_droit
FROM utilisateurs.t_profils
WHERE id_profil <= 6;	 

-- Vue permettant de simuler le contenu de la table "cor_role_droit_application" de la V1
CREATE OR REPLACE VIEW cor_role_droit_application AS 
SELECT 
 id_role,
 id_profil as id_droit, 
 id_application
FROM utilisateurs.cor_role_app_profil; 

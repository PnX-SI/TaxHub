
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

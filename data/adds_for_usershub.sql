-- Insérer les applications de base liées à TaxHub
INSERT INTO utilisateurs.t_applications (code_application, nom_application, desc_application, id_parent) VALUES 
('TH', 'TaxHub', 'Application permettant d''administrer les taxons.', NULL)
;

--Définir les profils utilisables pour TaxHub
INSERT INTO utilisateurs.cor_profil_for_app (id_profil, id_application) VALUES
(
    (SELECT id_profil FROM utilisateurs.t_profils WHERE code_profil = '2'),
    (SELECT id_application FROM utilisateurs.t_applications WHERE code_application = 'TH')
),(
    (SELECT id_profil FROM utilisateurs.t_profils WHERE code_profil = '3'),
    (SELECT id_application FROM utilisateurs.t_applications WHERE code_application = 'TH')
),(
    (SELECT id_profil FROM utilisateurs.t_profils WHERE code_profil = '4'),
    (SELECT id_application FROM utilisateurs.t_applications WHERE code_application = 'TH')
),(
    (SELECT id_profil FROM utilisateurs.t_profils WHERE code_profil = '6'),
    (SELECT id_application FROM utilisateurs.t_applications WHERE code_application = 'TH')
)
;

INSERT INTO utilisateurs.cor_role_app_profil (id_role, id_application, id_profil) VALUES
(
    (SELECT id_role FROM utilisateurs.t_roles WHERE nom_role = 'Grp_admin'),
    (SELECT id_application FROM utilisateurs.t_applications WHERE code_application = 'TH'),
    (SELECT id_profil FROM utilisateurs.t_profils WHERE code_profil = '6')
)
;

-- Vues permettant de gérer la compatibilité avec UsersHub V1. Quelle utilité ?

SET search_path = utilisateurs, pg_catalog;

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

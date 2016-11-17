CREATE SCHEMA IF NOT EXISTS utilisateurs;

CREATE SEQUENCE utilisateurs.bib_organismes_id_seq
  INCREMENT 1
  MINVALUE 1
  MAXVALUE 9223372036854775807
  START 1
  CACHE 1;
  
CREATE SEQUENCE utilisateurs.bib_unites_id_seq
  INCREMENT 1
  MINVALUE 1
  MAXVALUE 9223372036854775807
  START 1
  CACHE 1;
CREATE SEQUENCE utilisateurs.t_applications_id_application_seq
  INCREMENT 1
  MINVALUE 1
  MAXVALUE 9223372036854775807
  START 1
  CACHE 1;
  
CREATE TABLE utilisateurs.bib_droits
(
  id_droit integer NOT NULL,
  nom_droit character varying(50),
  desc_droit text,
  CONSTRAINT bib_droits_pkey PRIMARY KEY (id_droit)
);

CREATE SEQUENCE utilisateurs.t_menus_id_menu_seq
  INCREMENT 1
  MINVALUE 1
  MAXVALUE 9223372036854775807
  START 1
  CACHE 1;
  
CREATE SEQUENCE utilisateurs.t_roles_id_seq
  INCREMENT 1
  MINVALUE 1
  MAXVALUE 9223372036854775807
  START 1
  CACHE 1;
  
CREATE TABLE utilisateurs.bib_organismes
(
  nom_organisme character varying(100) NOT NULL,
  adresse_organisme character varying(128),
  cp_organisme character varying(5),
  ville_organisme character varying(100),
  tel_organisme character varying(14),
  fax_organisme character varying(14),
  email_organisme character varying(100),
  id_organisme integer NOT NULL DEFAULT nextval('utilisateurs.bib_organismes_id_seq'::regclass),
  CONSTRAINT pk_bib_organismes PRIMARY KEY (id_organisme)
);

CREATE TABLE utilisateurs.bib_unites
(
  nom_unite character varying(50) NOT NULL,
  adresse_unite character varying(128),
  cp_unite character varying(5),
  ville_unite character varying(100),
  tel_unite character varying(14),
  fax_unite character varying(14),
  email_unite character varying(100),
  id_unite integer NOT NULL DEFAULT nextval('utilisateurs.bib_unites_id_seq'::regclass),
  CONSTRAINT pk_bib_services PRIMARY KEY (id_unite)
);

CREATE TABLE utilisateurs.t_applications
(
  id_application serial NOT NULL,
  nom_application character varying(50) NOT NULL,
  desc_application text,
  CONSTRAINT t_applications_pkey PRIMARY KEY (id_application)
);

CREATE TABLE utilisateurs.t_menus
(
  id_menu serial NOT NULL,
  nom_menu character varying(50) NOT NULL,
  desc_menu text,
  id_application integer,
  CONSTRAINT t_menus_pkey PRIMARY KEY (id_menu),
  CONSTRAINT t_menus_id_application_fkey FOREIGN KEY (id_application)
      REFERENCES utilisateurs.t_applications (id_application) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE utilisateurs.t_roles
(
  groupe boolean NOT NULL DEFAULT false,
  id_role integer NOT NULL DEFAULT nextval('utilisateurs.t_roles_id_seq'::regclass),
  identifiant character varying(100),
  nom_role character varying(50),
  prenom_role character varying(50),
  desc_role text,
  pass character varying(100),
  email character varying(250),
  id_organisme integer,
  organisme character(32),
  id_unite integer,
  remarques text,
  pn boolean,
  session_appli character varying(50),
  date_insert timestamp without time zone,
  date_update timestamp without time zone,
  CONSTRAINT pk_roles PRIMARY KEY (id_role),
  CONSTRAINT t_roles_id_organisme_fkey FOREIGN KEY (id_organisme)
      REFERENCES utilisateurs.bib_organismes (id_organisme) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE NO ACTION,
  CONSTRAINT t_roles_id_unite_fkey FOREIGN KEY (id_unite)
      REFERENCES utilisateurs.bib_unites (id_unite) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE NO ACTION
);

CREATE TABLE utilisateurs.cor_roles
(
  id_role_groupe integer NOT NULL,
  id_role_utilisateur integer NOT NULL,
  CONSTRAINT cor_roles_pkey PRIMARY KEY (id_role_groupe, id_role_utilisateur),
  CONSTRAINT cor_roles_id_role_groupe_fkey FOREIGN KEY (id_role_groupe)
      REFERENCES utilisateurs.t_roles (id_role) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT cor_roles_id_role_utilisateur_fkey FOREIGN KEY (id_role_utilisateur)
      REFERENCES utilisateurs.t_roles (id_role) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE utilisateurs.cor_role_menu
(
  id_role integer NOT NULL,
  id_menu integer NOT NULL,
  CONSTRAINT cor_role_menu_pkey PRIMARY KEY (id_role, id_menu),
  CONSTRAINT cor_role_menu_application_id_menu_fkey FOREIGN KEY (id_menu)
      REFERENCES utilisateurs.t_menus (id_menu) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT cor_role_menu_application_id_role_fkey FOREIGN KEY (id_role)
      REFERENCES utilisateurs.t_roles (id_role) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE utilisateurs.cor_role_droit_application
(
  id_role integer NOT NULL,
  id_droit integer NOT NULL,
  id_application integer NOT NULL,
  CONSTRAINT cor_role_droit_application_pkey PRIMARY KEY (id_role, id_droit, id_application),
  CONSTRAINT cor_role_droit_application_id_application_fkey FOREIGN KEY (id_application)
      REFERENCES utilisateurs.t_applications (id_application) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT cor_role_droit_application_id_droit_fkey FOREIGN KEY (id_droit)
      REFERENCES utilisateurs.bib_droits (id_droit) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT cor_role_droit_application_id_role_fkey FOREIGN KEY (id_role)
      REFERENCES utilisateurs.t_roles (id_role) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE OR REPLACE VIEW utilisateurs.v_userslist_forall_applications AS 
 SELECT a.groupe,
    a.id_role,
    a.identifiant,
    a.nom_role,
    a.prenom_role,
    a.desc_role,
    a.pass,
    a.email,
    a.id_organisme,
    a.organisme,
    a.id_unite,
    a.remarques,
    a.pn,
    a.session_appli,
    a.date_insert,
    a.date_update,
    max(a.id_droit) AS id_droit_max,
    a.id_application
   FROM ( SELECT u.groupe,
            u.id_role,
            u.identifiant,
            u.nom_role,
            u.prenom_role,
            u.desc_role,
            u.pass,
            u.email,
            u.id_organisme,
            u.organisme,
            u.id_unite,
            u.remarques,
            u.pn,
            u.session_appli,
            u.date_insert,
            u.date_update,
            c.id_droit,
            c.id_application
           FROM utilisateurs.t_roles u
             JOIN utilisateurs.cor_role_droit_application c ON c.id_role = u.id_role
          WHERE u.groupe = false
        UNION
         SELECT u.groupe,
            u.id_role,
            u.identifiant,
            u.nom_role,
            u.prenom_role,
            u.desc_role,
            u.pass,
            u.email,
            u.id_organisme,
            u.organisme,
            u.id_unite,
            u.remarques,
            u.pn,
            u.session_appli,
            u.date_insert,
            u.date_update,
            c.id_droit,
            c.id_application
           FROM utilisateurs.t_roles u
             JOIN utilisateurs.cor_roles g ON g.id_role_utilisateur = u.id_role
             JOIN utilisateurs.cor_role_droit_application c ON c.id_role = g.id_role_groupe
          WHERE u.groupe = false) a
  GROUP BY a.groupe, a.id_role, a.identifiant, a.nom_role, a.prenom_role, a.desc_role, a.pass, a.email, a.id_organisme, a.organisme, a.id_unite, a.remarques, a.pn, a.session_appli, a.date_insert, a.date_update, a.id_application;

  
--données exemples

SET search_path = utilisateurs, pg_catalog;
INSERT INTO utilisateurs.bib_droits (id_droit, nom_droit, desc_droit) VALUES (5, 'validateur', 'Il valide bien sur');
INSERT INTO utilisateurs.bib_droits (id_droit, nom_droit, desc_droit) VALUES (4, 'modérateur', 'Peu utilisé');
INSERT INTO utilisateurs.bib_droits (id_droit, nom_droit, desc_droit) VALUES (0, 'aucun', 'aucun droit.');
INSERT INTO utilisateurs.bib_droits (id_droit, nom_droit, desc_droit) VALUES (1, 'utilisateur', 'Ne peut que consulter');
INSERT INTO utilisateurs.bib_droits (id_droit, nom_droit, desc_droit) VALUES (2, 'rédacteur', 'Il possède des droit d''écriture pour créer des enregistrements');
INSERT INTO utilisateurs.bib_droits (id_droit, nom_droit, desc_droit) VALUES (6, 'administrateur', 'Il a tous les droits');
INSERT INTO utilisateurs.bib_droits (id_droit, nom_droit, desc_droit) VALUES (3, 'référent', 'utilisateur ayant des droits complémentaires au rédacteur (par exemple exporter des données ou autre)');

INSERT INTO utilisateurs.bib_organismes (nom_organisme, adresse_organisme, cp_organisme, ville_organisme, tel_organisme, fax_organisme, email_organisme, id_organisme) VALUES ('PNF', NULL, NULL, 'Montpellier', NULL, NULL, NULL, 1);
INSERT INTO utilisateurs.bib_organismes (nom_organisme, adresse_organisme, cp_organisme, ville_organisme, tel_organisme, fax_organisme, email_organisme, id_organisme) VALUES ('Ma structure', 'qq part', '00001', 'ICI', '04 00 10 20 30', '', '', 2);
INSERT INTO utilisateurs.bib_organismes (nom_organisme, adresse_organisme, cp_organisme, ville_organisme, tel_organisme, fax_organisme, email_organisme, id_organisme) VALUES ('Autre', '', '', '', '', '', '', 99);

INSERT INTO utilisateurs.bib_unites (nom_unite, adresse_unite, cp_unite, ville_unite, tel_unite, fax_unite, email_unite, id_unite) VALUES ('Virtuel', NULL, NULL, NULL, NULL, NULL, NULL, 1);
INSERT INTO utilisateurs.bib_unites (nom_unite, adresse_unite, cp_unite, ville_unite, tel_unite, fax_unite, email_unite, id_unite) VALUES ('personnels partis', NULL, NULL, NULL, NULL, NULL, NULL, 2);
INSERT INTO utilisateurs.bib_unites (nom_unite, adresse_unite, cp_unite, ville_unite, tel_unite, fax_unite, email_unite, id_unite) VALUES ('Stagiaires', NULL, NULL, '', '', NULL, NULL, 3);
INSERT INTO utilisateurs.bib_unites (nom_unite, adresse_unite, cp_unite, ville_unite, tel_unite, fax_unite, email_unite, id_unite) VALUES ('Secretariat général', '', '', '', '', NULL, NULL, 4);
INSERT INTO utilisateurs.bib_unites (nom_unite, adresse_unite, cp_unite, ville_unite, tel_unite, fax_unite, email_unite, id_unite) VALUES ('Service scientifique', '', '', '', '', NULL, NULL, 5);
INSERT INTO utilisateurs.bib_unites (nom_unite, adresse_unite, cp_unite, ville_unite, tel_unite, fax_unite, email_unite, id_unite) VALUES ('Service SI', '', '', '', '', NULL, NULL, 6);
INSERT INTO utilisateurs.bib_unites (nom_unite, adresse_unite, cp_unite, ville_unite, tel_unite, fax_unite, email_unite, id_unite) VALUES ('Service Communication', '', '', '', '', NULL, NULL, 7);
INSERT INTO utilisateurs.bib_unites (nom_unite, adresse_unite, cp_unite, ville_unite, tel_unite, fax_unite, email_unite, id_unite) VALUES ('Conseil scientifique', '', '', '', NULL, NULL, NULL, 8);
INSERT INTO utilisateurs.bib_unites (nom_unite, adresse_unite, cp_unite, ville_unite, tel_unite, fax_unite, email_unite, id_unite) VALUES ('Conseil d''administration', '', '', '', NULL, NULL, NULL, 9);
INSERT INTO utilisateurs.bib_unites (nom_unite, adresse_unite, cp_unite, ville_unite, tel_unite, fax_unite, email_unite, id_unite) VALUES ('Partenaire fournisseur', NULL, NULL, NULL, NULL, NULL, NULL, 10);
INSERT INTO utilisateurs.bib_unites (nom_unite, adresse_unite, cp_unite, ville_unite, tel_unite, fax_unite, email_unite, id_unite) VALUES ('Autres', NULL, NULL, NULL, NULL, NULL, NULL, 99);

INSERT INTO t_applications (id_application, nom_application, desc_application) VALUES (1, 'application utilisateurs', 'application permettant d''administrer les utilisateurs.');
INSERT INTO utilisateurs.t_applications (id_application, nom_application, desc_application) VALUES (2, 'Taxhub', 'application permettant d''administrer la liste des taxons.');
INSERT INTO utilisateurs.t_applications (id_application, nom_application, desc_application) VALUES (14, 'application GeoNature', 'Application permettant la consultation et la gestion des relevés faune et flore.');

INSERT INTO utilisateurs.t_roles (groupe, id_role, identifiant, nom_role, prenom_role, desc_role, pass, email, organisme, id_unite, pn, session_appli, date_insert, date_update, id_organisme, remarques) VALUES (true, 20002, NULL, 'grp_en_poste', NULL, 'Tous les agents en poste', NULL, NULL, 'monpn', 99, true, NULL, NULL, NULL, NULL,'groupe test');
INSERT INTO utilisateurs.t_roles (groupe, id_role, identifiant, nom_role, prenom_role, desc_role, pass, email, organisme, id_unite, pn, session_appli, date_insert, date_update, id_organisme, remarques) VALUES (false, 1, 'admin', 'Administrateur', 'test', NULL, '21232f297a57a5a743894a0e4a801fc3', '', 'Parc national des Ecrins', 1, true, NULL, NULL, NULL, 99,'utilisateur test à modifier ou supprimer');
INSERT INTO utilisateurs.t_roles (groupe, id_role, identifiant, nom_role, prenom_role, desc_role, pass, email, organisme, id_unite, pn, session_appli, date_insert, date_update, id_organisme, remarques) VALUES (false, 3, 'partenaire', 'Partenaire', 'test', NULL, '5bd40a8524882d75f3083903f2c912fc', '', 'Autre', 99, true, NULL, NULL, NULL, 99,'utilisateur test à modifier ou supprimer');
INSERT INTO utilisateurs.t_roles (groupe, id_role, identifiant, nom_role, prenom_role, desc_role, pass, email, organisme, id_unite, pn, session_appli, date_insert, date_update, id_organisme, remarques) VALUES (false, 2, 'agent', 'Agent', 'test', NULL, 'b33aed8f3134996703dc39f9a7c95783', '', 'Parc national des Ecrins', 1, true, NULL, NULL, NULL, 99,'utilisateur test à modifier ou supprimer');

INSERT INTO utilisateurs.cor_role_droit_application (id_role, id_droit, id_application) VALUES (1, 6, 1);
INSERT INTO utilisateurs.cor_role_droit_application (id_role, id_droit, id_application) VALUES (1, 6, 2);
INSERT INTO utilisateurs.cor_role_droit_application (id_role, id_droit, id_application) VALUES (1, 6, 14);
INSERT INTO utilisateurs.cor_role_droit_application (id_role, id_droit, id_application) VALUES (20002, 3, 14);
INSERT INTO utilisateurs.cor_role_droit_application (id_role, id_droit, id_application) VALUES (2, 2, 14);
INSERT INTO utilisateurs.cor_role_droit_application (id_role, id_droit, id_application) VALUES (3, 1, 14);

INSERT INTO utilisateurs.t_menus (id_menu, nom_menu, desc_menu, id_application) VALUES (9, 'faune - Observateurs', 'listes des observateurs faune', 14);
INSERT INTO utilisateurs.t_menus (id_menu, nom_menu, desc_menu, id_application) VALUES (10, 'flore - Observateurs', 'Liste des observateurs flore', 14);

INSERT INTO utilisateurs.cor_role_menu (id_role, id_menu) VALUES (20002, 10);
INSERT INTO utilisateurs.cor_role_menu (id_role, id_menu) VALUES (20002, 9);

INSERT INTO cor_roles (id_role_groupe, id_role_utilisateur) VALUES (20002, 1);
INSERT INTO cor_roles (id_role_groupe, id_role_utilisateur) VALUES (20002, 2);

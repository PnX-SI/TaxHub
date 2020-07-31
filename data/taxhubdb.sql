SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;


CREATE SCHEMA taxonomie;

SET search_path = taxonomie, pg_catalog, public;


-------------
--FUNCTIONS--
-------------
CREATE OR REPLACE FUNCTION check_is_inbibnoms(mycdnom integer)
  RETURNS boolean AS
$BODY$
--fonction permettant de vérifier si un texte proposé correspond à un group2_inpn dans la table taxref
  BEGIN
    IF mycdnom IN(SELECT cd_nom FROM taxonomie.bib_noms) THEN
      RETURN true;
    ELSE
      RETURN false;
    END IF;
  END;
$BODY$
  LANGUAGE plpgsql IMMUTABLE
  COST 100;


CREATE OR REPLACE FUNCTION check_is_group2inpn(mygroup text)
  RETURNS boolean AS
$BODY$
--fonction permettant de vérifier si un texte proposé correspond à un group2_inpn dans la table taxref
  BEGIN
    IF mygroup IN(SELECT group2_inpn FROM taxonomie.vm_group2_inpn) OR mygroup IS NULL THEN
      RETURN true;
    ELSE
      RETURN false;
    END IF;
  END;
$BODY$
  LANGUAGE plpgsql IMMUTABLE
  COST 100;


CREATE OR REPLACE FUNCTION check_is_regne(myregne text)
  RETURNS boolean AS
$BODY$
--fonction permettant de vérifier si un texte proposé correspond à un regne dans la table taxref
  BEGIN
    IF myregne IN(SELECT regne FROM taxonomie.vm_regne) OR myregne IS NULL THEN
      return true;
    ELSE
      RETURN false;
    END IF;
  END;
$BODY$
  LANGUAGE plpgsql IMMUTABLE
  COST 100;

CREATE OR REPLACE FUNCTION find_regne(mycdnom integer)
  RETURNS text AS
$BODY$
--fonction permettant de renvoyer le regne d'un taxon à partir de son cd_nom
  DECLARE theregne character varying(255);
  BEGIN
    SELECT INTO theregne regne FROM taxonomie.taxref WHERE cd_nom = mycdnom;
    return theregne;
  END;
$BODY$
  LANGUAGE plpgsql IMMUTABLE
  COST 100;

CREATE OR REPLACE FUNCTION find_group2inpn(mycdnom integer)
  RETURNS text AS
$BODY$
--fonction permettant de renvoyer le group2_inpn d'un taxon à partir de son cd_nom
  DECLARE group2 character varying(255);
  BEGIN
    SELECT INTO group2 group2_inpn FROM taxonomie.taxref WHERE cd_nom = mycdnom;
    return group2;
  END;
$BODY$
  LANGUAGE plpgsql IMMUTABLE
  COST 100;

CREATE FUNCTION fct_build_bibtaxon_attributs_view(sregne character varying) RETURNS void
    LANGUAGE plpgsql
    AS $_$
DECLARE
    r taxonomie.bib_attributs%rowtype;
    sql_select text;
    sql_join text;
    sql_where text;
BEGIN
	sql_join :=' FROM taxonomie.bib_noms b JOIN taxonomie.taxref taxref USING(cd_nom) ';
	sql_select := 'SELECT b.* ';
	sql_where := ' WHERE regne=''' ||$1 || '''';
	FOR r IN
		SELECT id_attribut, nom_attribut, label_attribut, liste_valeur_attribut,
		       obligatoire, desc_attribut, type_attribut, type_widget, regne,
		       group2_inpn
		FROM taxonomie.bib_attributs
		WHERE regne IS NULL OR regne=sregne
	LOOP
		sql_select := sql_select || ', ' || r.nom_attribut || '.valeur_attribut::' || r.type_attribut || ' as ' || r.nom_attribut;
		sql_join := sql_join || ' LEFT OUTER JOIN (SELECT valeur_attribut, cd_ref FROM taxonomie.cor_taxon_attribut WHERE id_attribut= '
			|| r.id_attribut || ') as  ' || r.nom_attribut || '  ON b.cd_ref= ' || r.nom_attribut || '.cd_ref ';

	--RETURN NEXT r; -- return current row of SELECT
	END LOOP;
	EXECUTE 'DROP VIEW IF EXISTS taxonomie.v_bibtaxon_attributs_' || sregne ;
	EXECUTE 'CREATE OR REPLACE VIEW taxonomie.v_bibtaxon_attributs_' || sregne ||  ' AS ' || sql_select || sql_join || sql_where ;
END
$_$;

CREATE FUNCTION find_cdref(id integer) RETURNS integer
    LANGUAGE plpgsql IMMUTABLE
    AS $$
--fonction permettant de renvoyer le cd_ref d'un taxon à partir de son cd_nom
--
--Gil DELUERMOZ septembre 2011

  DECLARE ref integer;
  BEGIN
	SELECT INTO ref cd_ref FROM taxonomie.taxref WHERE cd_nom = id;
	return ref;
  END;
$$;


CREATE FUNCTION insert_t_medias() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    trimtitre text;
BEGIN
    new.date_media = now();
    trimtitre = replace(new.titre, ' ', '');
    --new.url = new.chemin || new.cd_ref || '_' || trimtitre || '.jpg';
    RETURN NEW;
END;
$$;


CREATE OR REPLACE FUNCTION unique_type1() RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    nbimgprincipale integer;
    mymedia record;
BEGIN
  IF new.id_type = 1 THEN
    SELECT count(*) INTO nbimgprincipale FROM taxonomie.t_medias WHERE cd_ref = new.cd_ref AND id_type = 1 AND NOT id_media = NEW.id_media;
    IF nbimgprincipale > 0 THEN
      FOR mymedia  IN SELECT * FROM taxonomie.t_medias WHERE cd_ref = new.cd_ref AND id_type = 1 LOOP
        UPDATE taxonomie.t_medias SET id_type = 2 WHERE id_media = mymedia.id_media;
        RAISE NOTICE USING MESSAGE =
        'La photo principale a été mise à jour pour le cd_ref ' || new.cd_ref ||
        '. La photo avec l''id_media ' || mymedia.id_media  || ' n''est plus la photo principale.';
      END LOOP;
    END IF;
  END IF;
  RETURN NEW;
END;
$$;


CREATE OR REPLACE FUNCTION  trg_fct_refresh_attributesviews_per_kingdom()
  RETURNS trigger AS
$$
DECLARE
   sregne text;
BEGIN
	if NEW.regne IS NULL THEN
		FOR sregne IN
			SELECT DISTINCT regne
			FROM taxonomie.taxref t
			JOIN taxonomie.bib_noms n
			ON t.cd_nom = n.cd_nom
			WHERE t.regne IS NOT NULL
		LOOP
			PERFORM taxonomie.fct_build_bibtaxon_attributs_view(sregne);
		END LOOP;
	ELSE
		PERFORM taxonomie.fct_build_bibtaxon_attributs_view(NEW.regne);
	END IF;
   RETURN NEW;
END
$$  LANGUAGE plpgsql;

DROP FUNCTION IF EXISTS taxonomie.find_all_taxons_children(integer);
DROP FUNCTION IF EXISTS taxonomie.find_all_taxons_children(integer,boolean);

CREATE OR REPLACE FUNCTION taxonomie.find_all_taxons_children(id integer, use_mv boolean DEFAULT true)
 RETURNS TABLE(cd_nom integer, cd_ref integer)
 LANGUAGE plpgsql
 IMMUTABLE
AS $function$
 --Param : cd_nom ou cd_ref d'un taxon quelque soit son rang
 --Retourne le cd_nom de tous les taxons enfants sous forme d'un jeu de données utilisable comme une table
 --Usage SELECT taxonomie.find_all_taxons_children(197047);
 --ou SELECT * FROM atlas.vm_taxons WHERE cd_ref IN(SELECT * FROM taxonomie.find_all_taxons_children(197047))
  BEGIN
	  IF NOT use_mv THEN
	      RETURN QUERY
	      WITH RECURSIVE descendants AS (
	        SELECT tx1.cd_nom, tx1.cd_ref FROM taxonomie.taxref tx1 WHERE tx1.cd_sup = taxonomie.find_cdref(id)
	      UNION ALL
	      SELECT tx2.cd_nom, tx2.cd_ref FROM descendants d JOIN taxonomie.taxref tx2 ON tx2.cd_sup = d.cd_nom
	      )
	      SELECT * FROM descendants;
     ELSE
	      RETURN QUERY
	      SELECT tx.cd_nom, tx.cd_ref 
	  	  FROM taxonomie.taxref_tree_parents ttp 
  	      JOIN taxonomie.taxref tx ON tx.cd_ref = ttp.cd_nom
  	      WHERE ttp.cd_nom_parent=taxonomie.find_cdref(id);
  	 END IF;
  END;
$function$
;



DROP FUNCTION IF EXISTS taxonomie.find_all_taxons_children(integer[]);
DROP FUNCTION IF EXISTS taxonomie.find_all_taxons_children(integer[],boolean);

CREATE OR REPLACE FUNCTION taxonomie.find_all_taxons_children(ids integer[], use_mv boolean DEFAULT true)
 RETURNS TABLE(cd_nom integer, cd_ref integer)
 LANGUAGE plpgsql
 IMMUTABLE
AS $function$
 --Param : cd_nom ou cd_ref d'un taxon quelque soit son rang
 --Retourne le cd_nom de tous les taxons enfants sous forme d'un jeu de données utilisable comme une table
 --Usage SELECT taxonomie.find_all_taxons_children(197047);
 --ou SELECT * FROM atlas.vm_taxons WHERE cd_ref IN(SELECT * FROM taxonomie.find_all_taxons_children(197047))
  BEGIN
	IF NOT use_mv THEN
      RETURN QUERY
      WITH RECURSIVE descendants AS (
        SELECT tx1.cd_nom, tx1.cd_ref FROM taxonomie.taxref tx1 WHERE tx1.cd_sup = ANY(ids)
      UNION ALL
      SELECT tx2.cd_nom, tx2.cd_ref FROM descendants d JOIN taxonomie.taxref tx2 ON tx2.cd_sup = d.cd_nom
      )
      SELECT * FROM descendants;
   ELSE
   	   RETURN QUERY
	   SELECT DISTINCT tx.cd_nom, tx.cd_ref 
  	   FROM taxonomie.taxref_tree_parents ttp 
       JOIN taxonomie.taxref tx ON tx.cd_ref = ttp.cd_nom
       WHERE ttp.cd_nom_parent=ANY(ids);
   END IF;
  END;
$function$
;

DROP FUNCTION IF EXISTS taxonomie.find_all_taxons_parents(int);
DROP FUNCTION IF EXISTS taxonomie.find_all_taxons_parents(int,boolean);

CREATE OR REPLACE FUNCTION taxonomie.find_all_taxons_parents(id integer, use_mv boolean DEFAULT true)
 RETURNS TABLE(cd_nom integer, distance smallint)
 LANGUAGE plpgsql
 IMMUTABLE
AS $function$
 --Param : cd_nom d'un taxon quelque soit son rang. Paramètre optionnelle pour définir si on utilise la vm (plus rapide, par défaut) ou seulement la table taxref
 --Retourne une table avec le cd_nom de tout les taxons parents et leur id_rang.
 --Retourne le cd_nom de tous les taxons parents sous forme d'un jeu de données utilisable comme une table. Les cd_nom sont ordonnées du plus bas vers le plus haut (Dumm)
 --Usage SELECT * FROM taxonomie.find_all_taxons_parents(457346);
  DECLARE
    inf RECORD;
 BEGIN
  IF NOT use_mv THEN
  	RETURN QUERY
		WITH RECURSIVE parents AS (
			SELECT tx1.cd_nom,tx1.cd_sup, tx1.id_rang, 0 AS nr FROM taxonomie.taxref tx1 WHERE tx1.cd_nom = taxonomie.find_cdref(id)
			UNION ALL 
			SELECT tx2.cd_nom,tx2.cd_sup, tx2.id_rang, nr + 1
				FROM parents p
				JOIN taxonomie.taxref tx2 ON tx2.cd_nom = p.cd_sup
		)
		SELECT parents.cd_nom, nr::smallint AS distance FROM parents
		ORDER BY parents.nr;
	ELSE
	  RETURN QUERY
	  	SELECT ttp.cd_nom_parent, ttp.distance::SMALLINT 
	  	FROM taxonomie.taxref_tree_parents ttp
	  	WHERE ttp.cd_nom=id
	    ORDER BY  ttp.distance  ASC;
	END IF;
  END;
$function$
;


DROP FUNCTION IF EXISTS taxonomie.find_all_taxons_parents(int[]);
DROP FUNCTION IF EXISTS taxonomie.find_all_taxons_parents(int[],boolean);

CREATE OR REPLACE FUNCTION taxonomie.find_all_taxons_parents(id integer[], use_mv boolean DEFAULT true)
 RETURNS TABLE(cd_nom integer, distance smallint)
 LANGUAGE plpgsql
 IMMUTABLE
AS $function$
 --Param : cd_nom d'un taxon quelque soit son rang
 --Retourne une table avec le cd_nom de tout les taxons parents et leur id_rang.
 --Retourne le cd_nom de tous les taxons parents sous forme d'un jeu de données utilisable comme une table. Les cd_nom sont ordonnées du plus bas vers le plus haut (Dumm)
 --Usage SELECT * FROM taxonomie.find_all_taxons_parents_t(457346);
  DECLARE
    inf RECORD;
   BEGIN
 IF NOT use_mv THEN
   RETURN QUERY
  WITH RECURSIVE parents AS (
   SELECT tx1.cd_nom,tx1.cd_sup, tx1.id_rang, 0 AS nr FROM taxonomie.taxref tx1 WHERE tx1.cd_nom = ANY(id)
   UNION ALL 
   SELECT tx2.cd_nom,tx2.cd_sup, tx2.id_rang, nr + 1
    FROM parents p
    JOIN taxonomie.taxref tx2 ON tx2.cd_nom = p.cd_sup
  )
  SELECT parents.cd_nom, parents.nr::SMALLINT as distance FROM parents
  ORDER BY parents.nr;
 ELSE
 RETURN QUERY
	SELECT ttp.cd_nom_parent, ttp.distance::SMALLINT 
	  	FROM taxonomie.taxref_tree_parents ttp
	  	WHERE ttp.cd_nom=ANY(id)
	    ORDER BY  ttp.distance  ASC;
 END IF;
  END;
$function$
;						   
							   
							   
CREATE OR REPLACE FUNCTION taxonomie.find_parent(mycd_nom integer, myid_rang character varying, use_mv boolean DEFAULT true)
 RETURNS integer
 LANGUAGE plpgsql
 STABLE
AS $function$
---Fonction permettant de retourner le cd_nom d'un taxon parent. 
---Le rang demandé doit être supérieur ou égal au rang du taxon en entrée, sinon la fonction retourne NULL.
  DECLARE cd_nom_parent integer;
  BEGIN
    SELECT INTO cd_nom_parent fatp.cd_nom 
    FROM taxonomie.find_all_taxons_parents(mycd_nom, use_mv) fatp
    JOIN taxonomie.taxref txp ON txp.cd_nom=fatp.cd_nom
   	WHERE txp.id_rang=myid_rang;
    return cd_nom_parent;
  END;
$function$
;

CREATE OR REPLACE FUNCTION taxonomie.find_cdref_sp(id integer)
 RETURNS integer
 LANGUAGE plpgsql
 STABLE
 AS $function$
 --fonction permettant de renvoyer le cd_ref d'un espèce a partir de son cd_nom ou du cd_nom d'une sous-espece (null si rang != ES ou SSES)
  DECLARE ref integer;
  DECLARE rang varchar;
  BEGIN
    SELECT INTO rang id_rang FROM taxonomie.taxref WHERE cd_nom=taxonomie.find_cdref(id);
    IF rang='ES' THEN
        ref=taxonomie.find_cdref(id);
    ELSE
	    SELECT INTO ref 
		    taxonomie.find_parent(id,'ES',true);
    END IF;
	return ref;
  END;
$function$
;


CREATE OR REPLACE FUNCTION taxonomie.find_lowest_common_ancestor(ids integer[])
 RETURNS integer
 LANGUAGE plpgsql
 STABLE
AS $function$
  --Param : Array de cd_nom
  --Retourne le cd_nom de l'ancêtre commun le plus proche
  DECLARE
  out_cd_nom integer;
BEGIN
	SELECT INTO out_cd_nom 
	cd_nom
		FROM ( SELECT cd_nom, distance FROM taxonomie.find_all_taxons_parents(ids) ) AS a
	GROUP BY cd_nom
	ORDER BY count(*) DESC, sum(distance) ASC LIMIT 1;
	
	RETURN out_cd_nom;
END;
$function$
;
							   
------------------------
---MATERIALIZED VIEW----
------------------------
DROP MATERIALIZED VIEW IF EXISTS taxonomie.taxref_tree_parents;

CREATE MATERIALIZED VIEW taxonomie.taxref_tree_parents AS ( 
		WITH RECURSIVE parents AS (
			SELECT tx1.cd_nom,tx1.cd_sup, tx1.id_rang, 0 AS nr 
				FROM taxonomie.taxref tx1 
				WHERE tx1.cd_nom=tx1.cd_ref
			UNION 
			SELECT p.cd_nom,tx2.cd_sup, tx2.id_rang, nr + 1
			FROM parents p
				JOIN taxonomie.taxref tx2 ON tx2.cd_nom = p.cd_sup
            AND tx2.cd_nom=tx2.cd_ref
		)
		SELECT cd_nom, cd_sup as cd_nom_parent, nr::smallint AS distance FROM parents WHERE cd_sup is not NULL
		ORDER BY parents.nr
);

CREATE UNIQUE INDEX taxref_tree_parents_cd_nom_cd_com_parent_idx ON taxonomie.taxref_tree_parents USING btree (cd_nom, cd_nom_parent);

COMMENT ON MATERIALIZED VIEW taxonomie.taxref_tree_parents IS 'Liste les taxons ayant un lien de parenté, utilisée pour optimiser les fonctions find_all_taxons_children et find_all_taxons_parents';
				       
------------------------
--TABLES AND SEQUENCES--
------------------------
CREATE SEQUENCE bib_attributs_id_attribut_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


SET default_tablespace = '';

SET default_with_oids = false;


CREATE TABLE bib_attributs (
    id_attribut integer DEFAULT nextval('bib_attributs_id_attribut_seq'::regclass) NOT NULL,
    nom_attribut character varying(255) NOT NULL,
    label_attribut character varying(50) NOT NULL,
    liste_valeur_attribut text NOT NULL,
    obligatoire boolean NOT NULL DEFAULT(False),
    desc_attribut text,
    type_attribut character varying(50),
    type_widget character varying(50),
    regne character varying(20),
    group2_inpn character varying(255),
    id_theme integer NOT NULL,
    ordre integer
);

CREATE TABLE bib_listes (
    id_liste integer NOT NULL,
    nom_liste character varying(255) NOT NULL ,
    desc_liste text,
    picto character varying(50) NOT NULL DEFAULT 'images/pictos/nopicto.gif',
    regne character varying(20),
    group2_inpn character varying(255)
);
COMMENT ON COLUMN bib_listes.picto IS 'Indique le chemin vers l''image du picto représentant le groupe taxonomique dans les menus déroulants de taxons';

ALTER TABLE taxonomie.bib_listes
  ADD CONSTRAINT unique_bib_listes_nom_liste UNIQUE (nom_liste);


CREATE TABLE bib_noms (
    id_nom integer NOT NULL,
    cd_nom integer,
    cd_ref integer,
    nom_francais character varying(1000),
    comments character varying(1000),
    CONSTRAINT check_is_valid_cd_ref CHECK ((cd_ref = find_cdref(cd_ref)))
);

CREATE SEQUENCE bib_noms_id_nom_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE bib_noms_id_nom_seq OWNED BY bib_noms.id_nom;

CREATE TABLE bib_taxref_categories_lr
(
  id_categorie_france character(2) NOT NULL,
  categorie_lr character varying(50) NOT NULL,
  nom_categorie_lr character varying(255) NOT NULL,
  desc_categorie_lr character varying(255)
);

CREATE TABLE bib_taxref_habitats (
    id_habitat integer NOT NULL,
    nom_habitat character varying(50) NOT NULL,
    desc_habitat text
);

CREATE TABLE bib_taxref_rangs (
    id_rang character(4) NOT NULL,
    nom_rang character varying(20) NOT NULL,
    tri_rang integer
);

CREATE TABLE bib_taxref_statuts (
    id_statut character(1) NOT NULL,
    nom_statut character varying(50) NOT NULL
);

CREATE TABLE bib_themes (
    id_theme integer NOT NULL,
    nom_theme character varying(20),
    desc_theme character varying(255),
    ordre integer,
    id_droit integer NOT NULL DEFAULT 0
);

CREATE SEQUENCE bib_themes_id_theme_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE bib_themes_id_theme_seq OWNED BY bib_themes.id_theme;

CREATE TABLE bib_types_media (
    id_type integer NOT NULL,
    nom_type_media character varying(100) NOT NULL,
    desc_type_media text
);

CREATE TABLE cor_nom_liste (
    id_liste integer NOT NULL,
    id_nom integer NOT NULL
);

CREATE TABLE cor_taxon_attribut (
    id_attribut integer NOT NULL,
    valeur_attribut text NOT NULL,
    cd_ref integer,
    CONSTRAINT check_is_cd_ref CHECK ((cd_ref = find_cdref(cd_ref)))
);

CREATE TABLE import_taxref (
    regne character varying(20),
    phylum character varying(50),
    classe character varying(50),
    ordre character varying(50),
    famille character varying(50),
    SOUS_FAMILLE character varying(50),
    TRIBU character varying(50),
    group1_inpn character varying(50),
    group2_inpn character varying(50),
    cd_nom integer NOT NULL,
    cd_taxsup integer,
    cd_sup integer,
    cd_ref integer,
    rang character varying(10),
    lb_nom character varying(100),
    lb_auteur character varying(500),
    nom_complet character varying(500),
    nom_complet_html character varying(500),
    nom_valide character varying(500),
    nom_vern character varying(1000),
    nom_vern_eng character varying(500),
    habitat character varying(10),
    fr character varying(10),
    gf character varying(10),
    mar character varying(10),
    gua character varying(10),
    sm character varying(10),
    sb character varying(10),
    spm character varying(10),
    may character varying(10),
    epa character varying(10),
    reu character varying(10),
    SA character varying(10),
    TA character varying(10),
    taaf character varying(10),
    pf character varying(10),
    nc character varying(10),
    wf character varying(10),
    cli character varying(10),
    url text
);

CREATE TABLE t_medias (
    id_media integer NOT NULL,
    cd_ref integer,
    titre character varying(255) NOT NULL,
    url character varying(255),
    chemin character varying(255),
    auteur character varying(1000),
    desc_media text,
    date_media date,
    is_public boolean DEFAULT true NOT NULL,
    supprime boolean DEFAULT false NOT NULL,
    id_type integer NOT NULL,
    source varchar(25),
    licence varchar(100),
    CONSTRAINT check_cd_ref_is_ref CHECK ((cd_ref = find_cdref(cd_ref)))
);

CREATE SEQUENCE t_medias_id_media_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE t_medias_id_media_seq OWNED BY t_medias.id_media;

CREATE TABLE taxref (
    cd_nom integer NOT NULL,
    id_statut character(1),
    id_habitat integer,
    id_rang character varying(10),
    regne character varying(20),
    phylum character varying(50),
    classe character varying(50),
    ordre character varying(50),
    famille character varying(50),
    sous_famille character varying(50),
    tribu character varying(50),
    cd_taxsup integer,
    cd_sup integer,
    cd_ref integer,
    lb_nom character varying(250),
    lb_auteur character varying(500),
    nom_complet character varying(500),
    nom_complet_html character varying(500),
    nom_valide character varying(500),
    nom_vern character varying(1000),
    nom_vern_eng character varying(500),
    group1_inpn character varying(50),
    group2_inpn character varying(50),
    url text
);

CREATE TABLE taxref_changes (
    cd_nom integer NOT NULL,
    num_version_init character varying(5),
    num_version_final character varying(5),
    champ character varying(50) NOT NULL,
    valeur_init character varying(255),
    valeur_final character varying(255),
    type_change character varying(25)
);

CREATE TABLE taxref_liste_rouge_fr
(
  id_lr serial NOT NULL,
  ordre_statut integer,
  vide character varying(255),
  cd_nom integer,
  cd_ref integer,
  nomcite character varying(255),
  nom_scientifique character varying(255),
  auteur character varying(255),
  nom_vernaculaire character varying(255),
  nom_commun character varying(255),
  rang character(4),
  famille character varying(50),
  endemisme character varying(255),
  population character varying(255),
  commentaire text,
  id_categorie_france character(2) NOT NULL,
  criteres_france character varying(255),
  liste_rouge character varying(255),
  fiche_espece character varying(255),
  tendance character varying(255),
  liste_rouge_source character varying(255),
  annee_publication integer,
  categorie_lr_europe character varying(2),
  categorie_lr_mondiale character varying(5)
);

CREATE TABLE taxref_protection_articles (
    cd_protection character varying(20) NOT NULL,
    article character varying(100),
    intitule text,
    arrete text,
    cd_arrete integer,
    url_inpn character varying(250),
    cd_doc integer,
    url character varying(250),
    date_arrete integer,
    type_protection character varying(250),
    concerne_mon_territoire boolean
);

CREATE TABLE taxref_protection_especes (
    cd_nom integer NOT NULL,
    cd_protection character varying(20) NOT NULL,
    nom_cite character varying(200),
    syn_cite character varying(200),
    nom_francais_cite character varying(100),
    precisions text,
    cd_nom_cite character varying(255) NOT NULL
);

CREATE TABLE taxref_protection_articles_structure
(
  cd_protection character varying(50) NOT NULL,
  alias_statut character varying(10),
  concerne_structure boolean
);

CREATE TABLE taxhub_admin_log
(
  id serial NOT NULL,
  action_time timestamp with time zone NOT NULL DEFAULT now(),
  id_role integer,
  object_type character varying(50),
  object_id integer,
  object_repr character varying(200) NOT NULL,
  change_type character varying(250),
  change_message character varying(250),
  CONSTRAINT taxhub_admin_log_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);

ALTER TABLE ONLY bib_noms ALTER COLUMN id_nom SET DEFAULT nextval('bib_noms_id_nom_seq'::regclass);

ALTER TABLE ONLY bib_themes ALTER COLUMN id_theme SET DEFAULT nextval('bib_themes_id_theme_seq'::regclass);

ALTER TABLE ONLY t_medias ALTER COLUMN id_media SET DEFAULT nextval('t_medias_id_media_seq'::regclass);

ALTER TABLE ONLY bib_noms
    ADD CONSTRAINT bib_noms_cd_nom_key UNIQUE (cd_nom);


----------------
--PRIMARY KEYS--
----------------
ALTER TABLE ONLY bib_noms
    ADD CONSTRAINT bib_noms_pkey PRIMARY KEY (id_nom);

ALTER TABLE ONLY bib_themes
    ADD CONSTRAINT bib_themes_pkey PRIMARY KEY (id_theme);

ALTER TABLE ONLY cor_nom_liste
    ADD CONSTRAINT cor_nom_liste_pkey PRIMARY KEY (id_nom, id_liste);

ALTER TABLE cor_taxon_attribut
  ADD CONSTRAINT cor_taxon_attribut_pkey PRIMARY KEY(id_attribut, cd_ref);

ALTER TABLE ONLY bib_types_media
    ADD CONSTRAINT id PRIMARY KEY (id_type);

ALTER TABLE ONLY t_medias
    ADD CONSTRAINT id_media PRIMARY KEY (id_media);

ALTER TABLE ONLY bib_attributs
    ADD CONSTRAINT pk_bib_attributs PRIMARY KEY (id_attribut);

ALTER TABLE ONLY bib_listes
    ADD CONSTRAINT pk_bib_listes PRIMARY KEY (id_liste);

ALTER TABLE ONLY bib_taxref_categories_lr
    ADD CONSTRAINT pk_bib_taxref_id_categorie_france PRIMARY KEY (id_categorie_france);

ALTER TABLE ONLY bib_taxref_habitats
    ADD CONSTRAINT pk_bib_taxref_habitats PRIMARY KEY (id_habitat);

ALTER TABLE ONLY bib_taxref_rangs
    ADD CONSTRAINT pk_bib_taxref_rangs PRIMARY KEY (id_rang);

ALTER TABLE ONLY bib_taxref_statuts
    ADD CONSTRAINT pk_bib_taxref_statuts PRIMARY KEY (id_statut);

ALTER TABLE ONLY import_taxref
    ADD CONSTRAINT pk_import_taxref PRIMARY KEY (cd_nom);

ALTER TABLE ONLY taxref
    ADD CONSTRAINT pk_taxref PRIMARY KEY (cd_nom);

ALTER TABLE ONLY taxref_changes
    ADD CONSTRAINT pk_taxref_changes PRIMARY KEY (cd_nom, champ);

ALTER TABLE ONLY taxref_liste_rouge_fr
    ADD CONSTRAINT pk_taxref_liste_rouge_fr PRIMARY KEY (id_lr);

ALTER TABLE ONLY taxref_protection_articles
    ADD CONSTRAINT taxref_protection_articles_pkey PRIMARY KEY (cd_protection);

ALTER TABLE ONLY taxref_protection_especes
    ADD CONSTRAINT taxref_protection_especes_pkey PRIMARY KEY (cd_nom, cd_protection, cd_nom_cite);

ALTER TABLE ONLY taxref_protection_articles_structure
    ADD CONSTRAINT taxref_protection_articles_structure_pkey PRIMARY KEY (cd_protection);



---------
--INDEX--
---------
CREATE INDEX fki_cd_nom_taxref_protection_especes ON taxref_protection_especes USING btree (cd_nom);

CREATE INDEX fki_cor_taxon_attribut ON cor_taxon_attribut USING btree (valeur_attribut);

CREATE INDEX i_fk_taxref_bib_taxref_habitat ON taxref USING btree (id_habitat);

CREATE INDEX i_fk_taxref_bib_taxref_rangs ON taxref USING btree (id_rang);

CREATE INDEX i_fk_taxref_bib_taxref_statuts ON taxref USING btree (id_statut);

CREATE INDEX i_taxref_cd_ref ON taxref USING btree (cd_ref);

CREATE INDEX i_taxref_hierarchy ON taxref USING btree (regne, phylum, classe, ordre, famille);

CREATE INDEX i_fk_taxref_group1_inpn ON taxref USING btree (group1_inpn);

CREATE INDEX i_fk_taxref_group2_inpn ON taxref USING btree (group2_inpn);

CREATE INDEX i_fk_taxref_nom_vern ON taxref USING btree (nom_vern);

CREATE INDEX i_bib_noms_cd_ref ON bib_noms USING btree (cd_ref);


----------------
--FOREIGN KEYS--
----------------
ALTER TABLE ONLY bib_attributs
    ADD CONSTRAINT bib_attributs_id_theme_fkey FOREIGN KEY (id_theme) REFERENCES bib_themes(id_theme);

ALTER TABLE ONLY cor_nom_liste
    ADD CONSTRAINT cor_nom_listes_bib_listes_fkey FOREIGN KEY (id_liste) REFERENCES bib_listes(id_liste) ON UPDATE CASCADE;

ALTER TABLE ONLY cor_nom_liste
    ADD CONSTRAINT cor_nom_listes_bib_noms_fkey FOREIGN KEY (id_nom) REFERENCES bib_noms(id_nom);

ALTER TABLE ONLY cor_taxon_attribut
    ADD CONSTRAINT cor_taxon_attrib_bib_attrib_fkey FOREIGN KEY (id_attribut) REFERENCES bib_attributs(id_attribut);

ALTER TABLE ONLY bib_noms
    ADD CONSTRAINT fk_bib_nom_taxref FOREIGN KEY (cd_nom) REFERENCES taxref(cd_nom);

ALTER TABLE ONLY t_medias
    ADD CONSTRAINT fk_t_media_bib_noms FOREIGN KEY (cd_ref) REFERENCES bib_noms(cd_nom) MATCH FULL ON UPDATE CASCADE;

ALTER TABLE ONLY t_medias
    ADD CONSTRAINT fk_t_media_bib_types_media FOREIGN KEY (id_type) REFERENCES bib_types_media(id_type) MATCH FULL ON UPDATE CASCADE;

ALTER TABLE ONLY taxref
    ADD CONSTRAINT fk_taxref_bib_taxref_habitats FOREIGN KEY (id_habitat) REFERENCES bib_taxref_habitats(id_habitat) ON UPDATE CASCADE;

ALTER TABLE ONLY taxref
    ADD CONSTRAINT fk_taxref_bib_taxref_rangs FOREIGN KEY (id_rang) REFERENCES bib_taxref_rangs(id_rang) ON UPDATE CASCADE;

ALTER TABLE ONLY taxref
    ADD CONSTRAINT taxref_id_statut_fkey FOREIGN KEY (id_statut) REFERENCES bib_taxref_statuts(id_statut) ON UPDATE CASCADE;

ALTER TABLE ONLY taxref_liste_rouge_fr
    ADD  CONSTRAINT fk_taxref_lr_bib_taxref_categories FOREIGN KEY (id_categorie_france) REFERENCES taxonomie.bib_taxref_categories_lr (id_categorie_france) MATCH SIMPLE
    ON UPDATE CASCADE ON DELETE NO ACTION;

ALTER TABLE ONLY taxref_protection_especes
    ADD CONSTRAINT taxref_protection_especes_cd_nom_fkey FOREIGN KEY (cd_nom) REFERENCES taxref(cd_nom) ON UPDATE CASCADE;

ALTER TABLE ONLY taxref_protection_especes
    ADD CONSTRAINT taxref_protection_especes_cd_protection_fkey FOREIGN KEY (cd_protection) REFERENCES taxref_protection_articles(cd_protection);

ALTER TABLE ONLY taxref_protection_articles_structure
    ADD CONSTRAINT taxref_protection_articles_structure_cd_protect_fkey FOREIGN KEY (cd_protection) REFERENCES taxref_protection_articles(cd_protection);

ALTER TABLE bib_themes
  ADD CONSTRAINT is_valid_id_droit_theme CHECK (id_droit >= 0 AND id_droit <= 6);


------------
--TRIGGERS--
------------
CREATE TRIGGER tri_insert_t_medias BEFORE INSERT ON t_medias FOR EACH ROW EXECUTE PROCEDURE insert_t_medias();

CREATE TRIGGER tri_unique_type1 BEFORE INSERT OR UPDATE ON t_medias FOR EACH ROW EXECUTE PROCEDURE unique_type1();

CREATE TRIGGER trg_refresh_attributes_views_per_kingdom AFTER INSERT OR UPDATE OR DELETE ON bib_attributs FOR EACH ROW EXECUTE PROCEDURE trg_fct_refresh_attributesviews_per_kingdom();

---------
--VIEWS--
---------
--DROP VIEW IF EXISTS v_taxref_all_listes CASCADE;
CREATE OR REPLACE VIEW v_taxref_all_listes AS
 WITH bib_nom_lst AS (
         SELECT cor_nom_liste.id_nom,
            bib_noms.cd_nom,
            bib_noms.nom_francais,
            cor_nom_liste.id_liste
           FROM taxonomie.cor_nom_liste
             JOIN taxonomie.bib_noms USING (id_nom)
        )
 SELECT t.regne,
    t.phylum,
    t.classe,
    t.ordre,
    t.famille,
    t.group1_inpn,
    t.group2_inpn,
    t.cd_nom,
    t.cd_ref,
    t.nom_complet,
    t.nom_valide,
    d.nom_francais AS nom_vern,
    t.lb_nom,
    d.id_liste
   FROM taxonomie.taxref t
     JOIN bib_nom_lst d ON t.cd_nom = d.cd_nom;


CREATE TABLE vm_taxref_list_forautocomplete AS
SELECT t.cd_nom,
  t.cd_ref,
  t.search_name,
  t.nom_valide,
  t.lb_nom,
  t.regne,
  t.group2_inpn,
  cnl.id_liste
FROM (
  -- PARTIE NOM SCIENTIFIQUE : ici on prend TOUS les synonymes.
  SELECT t_1.cd_nom,
        t_1.cd_ref,
        concat(t_1.lb_nom, ' =  <i> ', t_1.nom_valide, '</i>', ' - [', t_1.id_rang, ' - ', t_1.cd_nom , ']') AS search_name,
        t_1.nom_valide,
        t_1.lb_nom,
        t_1.regne,
        t_1.group2_inpn
  FROM taxonomie.taxref t_1
  UNION
  -- PARTIE NOM FRANCAIS : ici on prend une seule fois (DISTINCT) dans taxref tous les taxons de références présents dans bib_noms (t_1.cd_nom = n.cd_ref)
  -- même si un taxon n'a qu'un synonyme et pas son taxon de référence dans bib_noms.
  -- On ne prend pas les taxons qui n'ont pas de nom français dans bib_noms,
  -- donc si un taxon n'a pas de nom français dans bib_noms, il n'est accessible que par son nom scientifique.
  SELECT DISTINCT
        t_1.cd_nom,
        t_1.cd_ref,
        concat(n.nom_francais, ' =  <i> ', t_1.nom_valide, '</i>', ' - [', t_1.id_rang, ' - ', t_1.cd_ref , ']' ) AS search_name,
        t_1.nom_valide,
        t_1.lb_nom,
        t_1.regne,
        t_1.group2_inpn
  FROM taxonomie.taxref t_1
  JOIN taxonomie.bib_noms n ON t_1.cd_nom = n.cd_ref AND n.nom_francais IS NOT null
) t
-- ici on filtre pour ne conserver que les taxons présents dans les listes (cor_nom_liste)
-- la jointure est double : sur le cd_nom + le cd_ref (pour les noms qui n'auraient pas leur taxon référence dans bib_noms)
JOIN taxonomie.bib_noms n ON n.cd_nom = t.cd_nom OR n.cd_ref = t.cd_ref
JOIN taxonomie.cor_nom_liste cnl ON cnl.id_nom = n.id_nom;
COMMENT ON TABLE vm_taxref_list_forautocomplete
     IS 'Table construite à partir d''une requete sur la base et mise à jour via le trigger trg_refresh_mv_taxref_list_forautocomplete de la table cor_nom_liste';


CREATE OR REPLACE FUNCTION trg_fct_refresh_mv_taxref_list_forautocomplete()
  RETURNS trigger AS
$BODY$
DECLARE
	new_cd_nom int;
  new_cd_ref int;
	new_nom_vern varchar(1000);
	count_cdref int;
BEGIN
	IF TG_OP in ('DELETE', 'TRUNCATE', 'UPDATE') THEN
	    DELETE FROM taxonomie.vm_taxref_list_forautocomplete
      WHERE cd_nom IN (SELECT cd_nom FROM taxonomie.bib_noms WHERE id_nom =  OLD.id_nom)
      AND id_liste = OLD.id_liste;
	END IF;
	IF TG_OP in ('INSERT', 'UPDATE') THEN
		SELECT cd_nom, nom_francais, cd_ref INTO new_cd_nom, new_nom_vern, new_cd_ref FROM taxonomie.bib_noms WHERE id_nom = NEW.id_nom;
    SELECT count(*) INTO count_cdref FROM taxonomie.vm_taxref_list_forautocomplete WHERE cd_ref = new_cd_ref AND id_liste = NEW.id_liste;

		INSERT INTO taxonomie.vm_taxref_list_forautocomplete
		SELECT t.cd_nom,
            t.cd_ref,
		    concat(t.lb_nom, ' =  <i> ', t.nom_valide, '</i>', ' - [', t.id_rang, ' - ', t.cd_nom , ']') AS search_name,
		    t.nom_valide,
		    t.lb_nom,
		    t.regne,
		    t.group2_inpn,
		    NEW.id_liste
		FROM taxonomie.taxref t  WHERE cd_nom = new_cd_nom;

		IF NOT new_nom_vern IS NULL AND count_cdref = 0 THEN
			INSERT INTO taxonomie.vm_taxref_list_forautocomplete
			SELECT t.cd_nom,
                t.cd_ref,
                concat(new_nom_vern, ' =  <i> ', t.nom_valide, '</i>', ' - [', t.id_rang, ' - ', t.cd_nom , ']') AS search_name,
			    t.nom_valide,
			    t.lb_nom,
			    t.regne,
			    t.group2_inpn,
          NEW.id_liste
			FROM taxonomie.taxref t
			WHERE cd_nom = new_cd_nom AND t.cd_nom = t.cd_ref;
		END IF;
	END IF;
  RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;


CREATE INDEX i_vm_taxref_list_forautocomplete_cd_nom
  ON vm_taxref_list_forautocomplete (cd_nom ASC NULLS LAST);
CREATE INDEX i_vm_taxref_list_forautocomplete_search_name
  ON vm_taxref_list_forautocomplete (search_name ASC NULLS LAST);
CREATE INDEX i_tri_vm_taxref_list_forautocomplete_search_name
  ON vm_taxref_list_forautocomplete
  USING gist
  (search_name  gist_trgm_ops);


CREATE TRIGGER trg_refresh_mv_taxref_list_forautocomplete
  AFTER INSERT OR UPDATE OR DELETE
  ON cor_nom_liste
  FOR EACH ROW
  EXECUTE PROCEDURE trg_fct_refresh_mv_taxref_list_forautocomplete();


CREATE OR REPLACE FUNCTION taxonomie.trg_fct_refresh_nomfrancais_mv_taxref_list_forautocomplete()
  RETURNS trigger AS
$BODY$
DECLARE
BEGIN
    UPDATE taxonomie.vm_taxref_list_forautocomplete v
    SET search_name = concat(NEW.nom_francais, ' =  <i> ', t.nom_valide, '</i>', ' - [', t.id_rang, ' - ', t.cd_nom , ']')
    FROM taxonomie.taxref t
		WHERE v.cd_nom = NEW.cd_nom AND t.cd_nom = NEW.cd_nom;
    RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;


CREATE TRIGGER trg_refresh_nomfrancais_mv_taxref_list_forautocomplete AFTER UPDATE OF nom_francais
ON bib_noms FOR EACH ROW
EXECUTE PROCEDURE trg_fct_refresh_nomfrancais_mv_taxref_list_forautocomplete();

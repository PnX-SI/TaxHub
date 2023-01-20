"""Drop old status table

Revision ID: 188bc535258a
Revises: 27fd7e2b4b79
Create Date: 2022-12-16 12:29:29.143531

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "188bc535258a"
down_revision = "27fd7e2b4b79"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        DROP TABLE taxonomie.taxref_liste_rouge_fr;
        DROP TABLE taxonomie.bib_taxref_categories_lr;
        DROP TABLE taxonomie.taxref_protection_especes;
        DROP TABLE taxonomie.taxref_protection_articles_structure;
        DROP TABLE taxonomie.taxref_protection_articles;
    """
    )


def downgrade():
    """
    Create LR table
    Create LR constraints
    Create taxref protection tables
    Create taxref protection constraints
    """
    op.execute(
        """
        CREATE TABLE taxonomie.bib_taxref_categories_lr
        (
            id_categorie_france character(2) NOT NULL,
            categorie_lr character varying(50) NOT NULL,
            nom_categorie_lr character varying(255) NOT NULL,
            desc_categorie_lr character varying(255)
        );

        CREATE TABLE taxonomie.taxref_liste_rouge_fr
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
        ALTER TABLE ONLY taxonomie.bib_taxref_categories_lr
            ADD CONSTRAINT pk_bib_taxref_id_categorie_france PRIMARY KEY (id_categorie_france);
        ALTER TABLE ONLY taxonomie.taxref_liste_rouge_fr
            ADD CONSTRAINT pk_taxref_liste_rouge_fr PRIMARY KEY (id_lr);
        ALTER TABLE ONLY taxonomie.taxref_liste_rouge_fr
            ADD  CONSTRAINT fk_taxref_lr_bib_taxref_categories FOREIGN KEY (id_categorie_france) REFERENCES taxonomie.bib_taxref_categories_lr (id_categorie_france) MATCH SIMPLE
            ON UPDATE CASCADE ON DELETE NO ACTION;

        CREATE TABLE taxonomie.taxref_protection_articles (
            cd_protection character varying(20) PRIMARY KEY ,
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

        CREATE TABLE taxonomie.taxref_protection_especes (
            cd_nom integer NOT NULL,
            cd_protection character varying(20) NOT NULL,
            nom_cite character varying(200),
            syn_cite character varying(200),
            nom_francais_cite character varying(100),
            precisions text,
            cd_nom_cite character varying(255) NOT NULL,
            PRIMARY KEY (cd_nom, cd_protection, cd_nom_cite)
        );

        CREATE TABLE taxonomie.taxref_protection_articles_structure (
            cd_protection character varying(50) NOT NULL PRIMARY KEY,
            alias_statut character varying(10),
            concerne_structure boolean
        );
        ALTER TABLE ONLY taxonomie.taxref_protection_especes
            ADD CONSTRAINT taxref_protection_especes_cd_nom_fkey FOREIGN KEY (cd_nom)
            REFERENCES taxonomie.taxref(cd_nom) ON UPDATE CASCADE;

        ALTER TABLE ONLY taxonomie.taxref_protection_especes
            ADD CONSTRAINT taxref_protection_especes_cd_protection_fkey FOREIGN KEY (cd_protection)
            REFERENCES taxonomie.taxref_protection_articles(cd_protection);

        ALTER TABLE ONLY taxonomie.taxref_protection_articles_structure
            ADD CONSTRAINT taxref_protection_articles_structure_cd_protect_fkey FOREIGN KEY (cd_protection)
            REFERENCES taxonomie.taxref_protection_articles(cd_protection);

        CREATE INDEX fki_cd_nom_taxref_protection_especes ON taxonomie.taxref_protection_especes USING btree (cd_nom);
    """
    )

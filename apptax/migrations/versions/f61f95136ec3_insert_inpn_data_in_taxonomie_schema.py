"""insert inpn data in taxonomie schema

Revision ID: f61f95136ec3
Create Date: 2021-09-22 10:31:52.366014

"""
import logging
import importlib.resources
from zipfile import ZipFile

from alembic import op
import sqlalchemy as sa

from utils_flask_sqla.migrations.utils import logger, open_remote_file


# revision identifiers, used by Alembic.
revision = 'f61f95136ec3'
down_revision = None
branch_labels = ('taxonomie_inpn_data',)
depends_on = (
    '9c2c0254aadc',  # taxonomie
)


base_url = 'http://geonature.fr/data/inpn/taxonomie/'


def upgrade():
    logger.info("Insert habitats…")
    # FIXME remove id_habitat?
    op.execute("""
INSERT INTO taxonomie.bib_taxref_habitats (id_habitat, nom_habitat, desc_habitat) VALUES (1, 'Marin', 'Espèces vivant uniquement en milieu marin');
INSERT INTO taxonomie.bib_taxref_habitats (id_habitat, nom_habitat, desc_habitat) VALUES (2, 'Eau douce', 'Espèces vivant uniquement en milieu d''eau douce');
INSERT INTO taxonomie.bib_taxref_habitats (id_habitat, nom_habitat, desc_habitat) VALUES (3, 'Terrestre', 'Espèces vivant uniquement en milieu terrestre');
INSERT INTO taxonomie.bib_taxref_habitats (id_habitat, nom_habitat, desc_habitat) VALUES (5, 'Marin et Terrestre', 'Espèces effectuant une partie de leur cycle de vie en eau douce et l''autre partie en mer (espèces diadromes, amphidromes, anadromes ou catadromes)');
INSERT INTO taxonomie.bib_taxref_habitats (id_habitat, nom_habitat, desc_habitat) VALUES (6, 'Eau Saumâtre', 'Cas des pinnipèdes, des tortues et des oiseaux marins (par exemple)');
INSERT INTO taxonomie.bib_taxref_habitats (id_habitat, nom_habitat, desc_habitat) VALUES (7, 'Continental (Terrestre et/ou Eau douce)', 'Espèces vivant exclusivement en eau saumâtre');
INSERT INTO taxonomie.bib_taxref_habitats (id_habitat, nom_habitat, desc_habitat) VALUES (0, 'Non renseigné', null);
INSERT INTO taxonomie.bib_taxref_habitats (id_habitat, nom_habitat, desc_habitat) VALUES (4, 'Marin et Eau douce', 'Espèces continentales (non marines) dont on ne sait pas si elles sont terrestres et/ou d''eau douce (taxons provenant de Fauna Europaea)');
INSERT INTO taxonomie.bib_taxref_habitats (id_habitat, nom_habitat, desc_habitat) VALUES (8, 'Continental (Terrestre et Eau douce)', 'Espèces terrestres effectuant une partie de leur cycle en eau douce (odonates par exemple), ou fortement liées au milieu aquatique (loutre par exemple)');
    """)

    logger.info("Insert status…")
    # FIXME remove id_statut?
    op.execute("""
INSERT INTO taxonomie.bib_taxref_statuts (id_statut, nom_statut) VALUES ('A', 'Absente');
INSERT INTO taxonomie.bib_taxref_statuts (id_statut, nom_statut) VALUES ('B', 'Accidentelle / Visiteuse');
INSERT INTO taxonomie.bib_taxref_statuts (id_statut, nom_statut) VALUES ('C', 'Cryptogène');
INSERT INTO taxonomie.bib_taxref_statuts (id_statut, nom_statut) VALUES ('D', 'Douteux');
INSERT INTO taxonomie.bib_taxref_statuts (id_statut, nom_statut) VALUES ('E', 'Endemique');
INSERT INTO taxonomie.bib_taxref_statuts (id_statut, nom_statut) VALUES ('F', 'Trouvé en fouille');
INSERT INTO taxonomie.bib_taxref_statuts (id_statut, nom_statut) VALUES ('I', 'Introduite');
INSERT INTO taxonomie.bib_taxref_statuts (id_statut, nom_statut) VALUES ('J', 'Introduite envahissante');
INSERT INTO taxonomie.bib_taxref_statuts (id_statut, nom_statut) VALUES ('M', 'Domestique / Introduite non établie');
INSERT INTO taxonomie.bib_taxref_statuts (id_statut, nom_statut) VALUES ('P', 'Présente');
INSERT INTO taxonomie.bib_taxref_statuts (id_statut, nom_statut) VALUES ('S', 'Subendémique');
INSERT INTO taxonomie.bib_taxref_statuts (id_statut, nom_statut) VALUES ('W', 'Disparue');
INSERT INTO taxonomie.bib_taxref_statuts (id_statut, nom_statut) VALUES ('X', 'Eteinte');
INSERT INTO taxonomie.bib_taxref_statuts (id_statut, nom_statut) VALUES ('Y', 'Introduite éteinte');
INSERT INTO taxonomie.bib_taxref_statuts (id_statut, nom_statut) VALUES ('Z', 'Endémique éteinte');
INSERT INTO taxonomie.bib_taxref_statuts (id_statut, nom_statut) VALUES ('0', 'Non renseigné');
INSERT INTO taxonomie.bib_taxref_statuts (id_statut, nom_statut) VALUES ('Q', 'Mentionné par erreur');
INSERT INTO taxonomie.bib_taxref_statuts (id_statut, nom_statut) VALUES (' ', 'Non précisé');
    """)

    logger.info("Insert red list categories …")
    op.execute("""
INSERT INTO taxonomie.bib_taxref_categories_lr VALUES ('EX', 'Disparues', 'Eteinte à l''état sauvage', 'Eteinte au niveau mondial');
INSERT INTO taxonomie.bib_taxref_categories_lr VALUES ('EW', 'Disparues', 'Eteinte à l''état sauvage', 'Eteinte à l''état sauvage');
INSERT INTO taxonomie.bib_taxref_categories_lr VALUES ('RE', 'Disparues', 'Disparue au niveau régional', 'Disparue au niveau régional');
INSERT INTO taxonomie.bib_taxref_categories_lr VALUES ('CR', 'Menacées de disparition', 'En danger critique', 'En danger critique');
INSERT INTO taxonomie.bib_taxref_categories_lr VALUES ('EN', 'Menacées de disparition', 'En danger', 'En danger');
INSERT INTO taxonomie.bib_taxref_categories_lr VALUES ('VU', 'Menacées de disparition', 'Vulnérable', 'Vulnérable');
INSERT INTO taxonomie.bib_taxref_categories_lr VALUES ('NT', 'Autre', 'Quasi menacée', 'Espèce proche du seuil des espèces menacées ou qui pourrait être menacée si des mesures de conservation spécifiques n''étaient pas prises');
INSERT INTO taxonomie.bib_taxref_categories_lr VALUES ('LC', 'Autre', 'Préoccupation mineure', 'Espèce pour laquelle le risque de disparition est faible');
INSERT INTO taxonomie.bib_taxref_categories_lr VALUES ('DD', 'Autre', 'Données insuffisantes', 'Espèce pour laquelle l''évaluation n''a pas pu être réalisée faute de données suffisantes');
INSERT INTO taxonomie.bib_taxref_categories_lr VALUES ('NA', 'Autre', 'Non applicable', 'Espèce non soumise à évaluation car (a) introduite dans la période récente ou (b) présente en métropole de manière occasionnelle ou marginale');
INSERT INTO taxonomie.bib_taxref_categories_lr VALUES ('NE', 'Autre', 'Non évaluée', 'Espèce non encore confrontée aux critères de la Liste rouge');
    """)

    cursor = op.get_bind().connection.cursor()
    with open_remote_file(base_url, 'TAXREF_v14_2020.zip', open_fct=ZipFile) as archive:
        with archive.open('TAXREF_v14_2020/rangs_note.csv') as f:
            logger.info("Insert TAXREFv14 rangs…")
            cursor.copy_expert("""
            COPY taxonomie.bib_taxref_rangs (tri_rang, id_rang, nom_rang, nom_rang_en)
            FROM STDIN WITH CSV HEADER DELIMITER E'\t'
            """, f)
        with archive.open('TAXREF_v14_2020/TAXREFv14.txt') as f:
            #op.create_table('import_taxref',
            #    sa.Column('regne', sa.String(20)),
            #    …
            #    schema='taxonomie',
            #)
            op.execute("""
            CREATE TABLE taxonomie.import_taxref (
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
            """)
            logger.info("Insert TAXREFv14 in temporary table…")
            cursor.copy_expert("""
            COPY taxonomie.import_taxref (regne, phylum, classe, ordre, famille, sous_famille, tribu, group1_inpn,
               group2_inpn, cd_nom, cd_taxsup, cd_sup, cd_ref, rang, lb_nom,
               lb_auteur, nom_complet, nom_complet_html, nom_valide, nom_vern,
               nom_vern_eng, habitat, fr, gf, mar, gua, sm, sb, spm, may, epa,
               reu, sa, ta, taaf, pf, nc, wf, cli, url)
            FROM STDIN WITH CSV HEADER DELIMITER E'\t'
            """, f)
            logger.info("Insert TAXREFv14 in final table…")
            op.execute("""
            INSERT INTO taxonomie.taxref
              SELECT cd_nom, fr as id_statut, habitat::int as id_habitat, rang as  id_rang,
                     regne, phylum, classe, ordre, famille,  sous_famille, tribu, cd_taxsup,
                     cd_sup, cd_ref, lb_nom, substring(lb_auteur, 1, 250), nom_complet,
                     nom_complet_html,nom_valide, substring(nom_vern,1,1000), nom_vern_eng,
                     group1_inpn, group2_inpn, url
                FROM taxonomie.import_taxref;
            """)
            op.drop_table('import_taxref', schema='taxonomie')

    with open_remote_file(base_url, 'ESPECES_REGLEMENTEES_v11.zip', open_fct=ZipFile) as archive:
        with archive.open('PROTECTION_ESPECES_TYPES_11.csv') as f:
            logger.info("Insert protection especes types…")
            cursor.copy_expert("""
            COPY taxonomie.taxref_protection_articles (
                cd_protection, article, intitule, arrete,
                url_inpn, cd_doc, url, date_arrete, type_protection )
            FROM STDIN WITH CSV HEADER
            """, f)

        op.create_table(
            'import_protection_especes',
            sa.Column('cd_nom', sa.INTEGER),
            sa.Column('cd_protection', sa.VARCHAR(250)),
            sa.Column('nom_cite', sa.TEXT),
            sa.Column('syn_cite', sa.TEXT),
            sa.Column('nom_francais_cite', sa.TEXT),
            sa.Column('precisions', sa.VARCHAR(500)),
            sa.Column('cd_nom_cite', sa.INTEGER),
            schema='taxonomie',
        )

        with archive.open('PROTECTION_ESPECES_11.csv') as f:
            logger.info("Insert protection especes in temporary table…")
            cursor.copy_expert("""
            COPY taxonomie.import_protection_especes
            FROM STDIN WITH CSV HEADER
            """, f)

    with open_remote_file(base_url, 'LR_FRANCE_20160000.zip', open_fct=ZipFile) as archive:
        with archive.open('LR_FRANCE.csv') as f:
            logger.info("Insert red list…")
            cursor.copy_expert("""
            COPY taxonomie.taxref_liste_rouge_fr (
                    ordre_statut,vide,cd_nom,cd_ref,nomcite,nom_scientifique,auteur,
                    nom_vernaculaire,nom_commun,rang,famille,endemisme,population,commentaire,
                    id_categorie_france,criteres_france,liste_rouge,fiche_espece,tendance,
                    liste_rouge_source,annee_publication,categorie_lr_europe,categorie_lr_mondiale)
            FROM STDIN WITH CSV HEADER DELIMITER E'\;'
            """, f)

    logger.info("Insert protection especes in final table…")
    op.execute("""
        INSERT INTO taxonomie.taxref_protection_especes
        SELECT DISTINCT  p.*
        FROM  (
          SELECT cd_nom , cd_protection , string_agg(DISTINCT nom_cite, ',') nom_cite,
            string_agg(DISTINCT syn_cite, ',')  syn_cite,
            string_agg(DISTINCT nom_francais_cite, ',')  nom_francais_cite,
            string_agg(DISTINCT precisions, ',')  precisions, cd_nom_cite
          FROM taxonomie.import_protection_especes
          GROUP BY cd_nom , cd_protection , cd_nom_cite
        ) p
        JOIN taxonomie.taxref t
        USING(cd_nom) ;
    """)

    op.drop_table('import_protection_especes', schema='taxonomie')

    logger.info("Clean unused protection status…")
    op.execute("""
    DELETE FROM taxonomie.taxref_protection_articles
        WHERE cd_protection IN (
          SELECT cd_protection
          FROM taxonomie.taxref_protection_articles
          WHERE NOT cd_protection IN
            (SELECT DISTINCT cd_protection FROM taxonomie.taxref_protection_especes)
        )
    """)

    with open_remote_file(base_url, 'BDC-Statuts-v14.zip', open_fct=ZipFile) as archive:
        with archive.open('BDC-Statuts-v14/BDC_STATUTS_TYPES_14.csv') as f:
            cursor.copy_expert("""
            COPY taxonomie.bdc_statut_type
            FROM STDIN WITH CSV HEADER
            """, f)
        with archive.open('BDC-Statuts-v14/BDC_STATUTS_14.csv') as f:
            cursor.copy_expert("""
            COPY taxonomie.bdc_statut (
                cd_nom,cd_ref,cd_sup,cd_type_statut,lb_type_statut,regroupement_type,code_statut,
                label_statut,rq_statut,cd_sig,cd_doc,lb_nom,lb_auteur,nom_complet_html,nom_valide_html,
                regne,phylum,classe,ordre,famille,group1_inpn,group2_inpn,lb_adm_tr,niveau_admin,
                cd_iso3166_1,cd_iso3166_2,full_citation,doc_url,thematique,type_value
            )
            FROM STDIN WITH CSV HEADER ENCODING 'ISO 8859-1'
            """, f)

    logger.info("Delete duplicate data in bdc_statut…")
    op.execute("""
WITH d AS (
    SELECT
        count(*), min(id), array_agg(id)
    FROM taxonomie.bdc_statut
    GROUP BY
        cd_nom, cd_ref, cd_sup, cd_type_statut, lb_type_statut, regroupement_type, code_statut, label_statut, rq_statut,
        cd_sig, cd_doc, lb_nom, lb_auteur, nom_complet_html, nom_valide_html, regne, phylum, classe, ordre, famille, group1_inpn,
        group2_inpn, lb_adm_tr, niveau_admin, cd_iso3166_1, cd_iso3166_2, full_citation, doc_url, thematique, type_value
    HAVING count(*) >1
) , id_doublon AS (
    SELECT min, unnest(array_agg) as to_del
    FROM d
)
DELETE
FROM  taxonomie.bdc_statut s
USING id_doublon d
WHERE s.id = d.to_del and not id = min;
    """)

    #op.execute("DROP INDEX taxonomie.bdc_statut_id_idx")


def downgrade():
    # FIXME vider les tables est-il acceptable ?
    op.execute("DELETE FROM taxonomie.bdc_statut")
    op.execute("DELETE FROM taxonomie.bdc_statut_type")
    op.execute("DELETE FROM taxonomie.taxref_protection_especes")
    op.execute("DELETE FROM taxonomie.taxref_liste_rouge_fr")
    op.execute("DELETE FROM taxonomie.taxref_protection_articles")
    op.execute("DELETE FROM taxonomie.taxref")
    op.execute("TRUNCATE taxonomie.import_taxref")  # TODO: remove this table?
    op.execute("DELETE FROM taxonomie.bib_taxref_categories_lr")
    op.execute("DELETE FROM taxonomie.bib_taxref_statuts")
    op.execute("DELETE FROM taxonomie.bib_taxref_rangs")
    op.execute("DELETE FROM taxonomie.bib_taxref_habitats")

import logging
import importlib.resources
from zipfile import ZipFile

import click
import sqlalchemy as sa
from sqlalchemy.schema import Table, MetaData
from flask.cli import with_appcontext

from utils_flask_sqla.migrations.utils import open_remote_file

from apptax.database import db
from apptax.taxonomie.commands.utils import copy_from_csv, refresh_taxref_vm, import_bdc_statuts


base_url = "http://geonature.fr/data/inpn/taxonomie/"


def import_bdc_statuts_v14(logger):
    import_bdc_statuts(
        logger,
        base_url,
        "BDC-Statuts-v14.zip",
        "BDC-Statuts-v14/BDC_STATUTS_TYPES_14.csv",
        "BDC-Statuts-v14/BDC_STATUTS_14.csv",
    )


@click.command()
@click.option("--skip-bdc-statuts", is_flag=True, help="Skip import of BDC Statuts")
@with_appcontext
def import_v14(skip_bdc_statuts):
    logger = logging.getLogger()
    bind = db.session.get_bind()
    metadata = MetaData(bind=bind)
    cursor = bind.raw_connection().cursor()
    with open_remote_file(base_url, "TAXREF_v14_2020.zip", open_fct=ZipFile) as archive:
        with archive.open("TAXREF_v14_2020/habitats_note.csv") as f:
            logger.info("Insert TAXREFv14 habitats…")
            copy_from_csv(f, "bib_taxref_habitats", encoding="WIN1252", delimiter=";")
        with archive.open("TAXREF_v14_2020/rangs_note.csv") as f:
            logger.info("Insert TAXREFv14 rangs…")
            copy_from_csv(
                f,
                "bib_taxref_rangs",
                delimiter="\t",
                dest_cols=("tri_rang", "id_rang", "nom_rang", "nom_rang_en"),
            )
        with archive.open("TAXREF_v14_2020/statuts_note.csv") as f:
            logger.info("Insert TAXREFv14 statuts…")
            copy_from_csv(
                f,
                "bib_taxref_statuts",
                encoding="WIN1252",
                delimiter=";",
                dest_cols=("id_statut", "nom_statut"),
                source_cols=("statut", "description"),
            )
        with archive.open("TAXREF_v14_2020/TAXREFv14.txt") as f:
            logger.info("Insert TAXREFv14 referentiel…")
            copy_from_csv(
                f,
                "taxref",
                delimiter="\t",
                dest_cols=(
                    "cd_nom",
                    "id_statut",
                    "id_habitat",
                    "id_rang",
                    "regne",
                    "phylum",
                    "classe",
                    "ordre",
                    "famille",
                    "sous_famille",
                    "tribu",
                    "cd_taxsup",
                    "cd_sup",
                    "cd_ref",
                    "lb_nom",
                    "lb_auteur",
                    "nom_complet",
                    "nom_complet_html",
                    "nom_valide",
                    "nom_vern",
                    "nom_vern_eng",
                    "group1_inpn",
                    "group2_inpn",
                    "url",
                ),
                source_cols=(
                    "cd_nom::int",
                    "fr as id_statut",
                    "habitat::int as id_habitat",
                    "rang as id_rang",
                    "regne",
                    "phylum",
                    "classe",
                    "ordre",
                    "famille",
                    "sous_famille",
                    "tribu",
                    "cd_taxsup::int",
                    "cd_sup::int",
                    "cd_ref::int",
                    "lb_nom",
                    "substring(lb_auteur, 1, 250)",
                    "nom_complet",
                    "nom_complet_html",
                    "nom_valide",
                    "substring(nom_vern,1,1000)",
                    "nom_vern_eng",
                    "group1_inpn",
                    "group2_inpn",
                    "url",
                ),
            )

    with open_remote_file(base_url, "ESPECES_REGLEMENTEES_v11.zip", open_fct=ZipFile) as archive:
        with archive.open("PROTECTION_ESPECES_TYPES_11.csv") as f:
            logger.info("Insert protection especes types…")
            copy_from_csv(
                f,
                "taxref_protection_articles",
                dest_cols=(
                    "cd_protection",
                    "article",
                    "intitule",
                    "arrete",
                    "url_inpn",
                    "cd_doc",
                    "url",
                    "date_arrete",
                    "type_protection",
                ),
            )

        import_protection_especes = Table(
            "import_protection_especes",
            metadata,
            sa.Column("cd_nom", sa.INTEGER),
            sa.Column("cd_protection", sa.VARCHAR(250)),
            sa.Column("nom_cite", sa.TEXT),
            sa.Column("syn_cite", sa.TEXT),
            sa.Column("nom_francais_cite", sa.TEXT),
            sa.Column("precisions", sa.VARCHAR(500)),
            sa.Column("cd_nom_cite", sa.INTEGER),
            schema="taxonomie",
        )
        import_protection_especes.create(bind=db.session.connection())

        with archive.open("PROTECTION_ESPECES_11.csv") as f:
            logger.info("Insert protection especes in temporary table…")
            cursor.copy_expert(
                """
            COPY taxonomie.import_protection_especes
            FROM STDIN WITH CSV HEADER
            """,
                f,
            )

    logger.info("Insert red list categories …")
    db.session.execute(
        """
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
    """
    )

    with open_remote_file(base_url, "LR_FRANCE_20160000.zip", open_fct=ZipFile) as archive:
        with archive.open("LR_FRANCE.csv") as f:
            logger.info("Insert red list…")
            cursor.copy_expert(
                """
            COPY taxonomie.taxref_liste_rouge_fr (
                    ordre_statut,vide,cd_nom,cd_ref,nomcite,nom_scientifique,auteur,
                    nom_vernaculaire,nom_commun,rang,famille,endemisme,population,commentaire,
                    id_categorie_france,criteres_france,liste_rouge,fiche_espece,tendance,
                    liste_rouge_source,annee_publication,categorie_lr_europe,categorie_lr_mondiale)
            FROM STDIN WITH CSV HEADER DELIMITER E'\;'
            """,
                f,
            )

    logger.info("Insert protection especes in final table…")
    db.session.execute(
        """
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
    """
    )

    db.session.execute("DROP TABLE taxonomie.import_protection_especes")

    logger.info("Clean unused protection status…")
    db.session.execute(
        """
    DELETE FROM taxonomie.taxref_protection_articles
        WHERE cd_protection IN (
          SELECT cd_protection
          FROM taxonomie.taxref_protection_articles
          WHERE NOT cd_protection IN
            (SELECT DISTINCT cd_protection FROM taxonomie.taxref_protection_especes)
        )
    """
    )

    if not skip_bdc_statuts:
        import_bdc_statuts_v14(logger)
    else:
        logger.info("Skipping BDC statuts.")

    logger.info("Refresh materialized views…")
    refresh_taxref_vm()

    logger.info("Committing…")
    db.session.commit()


@click.command()
@with_appcontext
def import_bdc_v14():
    logger = logging.getLogger()
    import_bdc_statuts_v14(logger)
    db.session.commit()

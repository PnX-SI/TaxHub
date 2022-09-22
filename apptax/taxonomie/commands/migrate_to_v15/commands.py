from flask import Blueprint

import importlib
import click
from zipfile import ZipFile
from sqlalchemy import text
from flask.cli import with_appcontext

from utils_flask_sqla.migrations.utils import open_remote_file

from apptax.database import db
from apptax.taxonomie.commands.utils import copy_from_csv
from .utils import save_data, analyse_taxref_changes
from . import logger


base_url = "http://geonature.fr/data/inpn/taxonomie/"


@click.group(help="Migrate to TaxRef v15.")
def migrate_to_v15():
    pass


@migrate_to_v15.command()
@with_appcontext
def import_taxref_v15():
    """
    Procédure de migration de taxref vers la version 15
        Test de la disparition des cd_noms
    """
    # Prerequis : deps_test_fk_dependencies_cd_nom
    query = text(
        importlib.resources.read_text(
            "apptax.taxonomie.commands.migrate_to_v15.data",
            "0.2_taxref_detection_repercussion_disparition_cd_nom.sql",
        )
    )
    db.session.execute(query)

    # import taxref v15 data
    import_data_taxref_v15()
    db.session.commit()

    # Analyse des changements à venir
    analyse_taxref_changes()


@migrate_to_v15.command()
@click.option("--keep-cdnom", is_flag=True)
@with_appcontext
def test_changes_detection(keep_cdnom):
    """Analyse des répercussions de changement de taxref

    :param keep-cdnom:  Indique si l'on souhaite concerver les cd_noms manquant au lieu de les supprimer
    :type keep-cdnom: boolean

    3 étapes :
        - Detection des cd_noms manquants
        - Création d'une copie de travail de bib_noms
        - Analyse des modifications taxonomique (split, merge, ...) et
            de leur répercussion sur les attributs et medias de taxhub
    """
    # Analyse des changements à venir
    analyse_taxref_changes(without_substitution=False, keep_missing_cd_nom=keep_cdnom)


@migrate_to_v15.command()
@click.option("--keep-oldtaxref", is_flag=True)
@click.option("--keep-oldbdc", is_flag=True)
@click.option("--keep-cdnom", is_flag=True)
@click.option("--script_predetection", type=click.Path(exists=True))
@click.option("--script_postdetection", type=click.Path(exists=True))
@with_appcontext
def apply_changes(
    keep_oldtaxref, keep_oldbdc, keep_cdnom, script_predetection, script_postdetection
):
    """Procédure de migration de taxref vers la version 15
         Application des changements import des données dans les tables taxref et bdc_status


    :param keep-oldtaxref: Indique si l'on souhaite concerver l'ancienne version du referentiel taxref
    :type keep-oldtaxref: boolean
    :param keep-oldbdc:  Indique si l'on souhaite concerver l'ancienne version du referentiel bdc_status
    :type keep-oldbdc: boolean
    :param keep-cdnom:  Indique si l'on souhaite concerver les cd_noms manquant au lieu de les supprimer
    :type keep-cdnom: boolean
    :param script_predetection: Emplacement d'un fichier sql de correction avant la detection des changements
    :type script_predetection: Path
    :param script_postdetection: Emplacement d'un fichier sql de correction après la detection des changements
    :type script_postdetection: Path
    """

    # Analyse des changements à venir
    analyse_taxref_changes(
        without_substitution=False,
        keep_missing_cd_nom=keep_cdnom,
        script_predetection=script_predetection,
        script_postdetection=script_postdetection,
    )

    # Save taxref and bdc_status data
    save_data(14, keep_oldtaxref, keep_oldbdc)

    # Update taxref v15
    logger.info("Migration of taxref ...")
    try:
        query = text(
            importlib.resources.read_text(
                "apptax.taxonomie.commands.migrate_to_v15.data", "3.2_alter_taxref_data.sql"
            )
        )
        db.session.execute(query)
        db.session.commit()
        logger.info("it's done")
    except Exception as e:
        logger.error(str(e))

    # Import bdc status data and insert into taxhub tables
    import_and_format_dbc_status()

    # Clean DB
    logger.info("Clean DB")
    query = text(
        importlib.resources.read_text(
            "apptax.taxonomie.commands.migrate_to_v15.data", "5_clean_db.sql"
        )
    )
    db.session.execute(query)

    db.session.commit()


def import_data_taxref_v15():
    """
    Import des données brutes de taxref v15 en base
    avant leur traitement
    """

    logger.info("Import TAXREFv15 into tmp table…")

    # Préparation création de table temporaire permettant d'importer taxref
    query = text(
        importlib.resources.read_text(
            "apptax.taxonomie.commands.migrate_to_v15.data", "0_taxrefv15_import_data.sql"
        )
    )
    db.session.execute(query)
    db.session.commit()

    with open_remote_file(
        base_url, "TAXREF_v15_2021.zip", open_fct=ZipFile, data_dir="tmp"
    ) as archive:
        with archive.open("TAXREFv15.txt") as f:
            logger.info("Insert TAXREFv15 into taxonomie.import_taxref table…")
            copy_from_csv(
                f,
                table_name="import_taxref",
                delimiter="\t",
            )
        with archive.open("CDNOM_DISPARUS.csv") as f:
            logger.info("Insert missing cd_nom into taxonomie.cdnom_disparu table…")
            copy_from_csv(
                f,
                table_name="cdnom_disparu",
                delimiter=",",
            )

        # No changes in taxref v15
        # with archive.open('rangs_note.csv') as f:
        #     logger.info("Insert rangs_note tmp table…")
        #     copy_from_csv(f,
        #         table_name="import_taxref_rangs",
        #         encoding="WIN1252", delimiter=";",
        #     )


def import_and_format_dbc_status():
    """
    Import des données brutes de la base bdc_status  en base
    Puis traitement des données de façon à les ventiler dans les différentes tables
    """

    import_data_dbc_status_15()
    # Delete doublons
    logger.info("Remove duplicate bdc_statut")
    db.session.execute(
        text(
            """
        --- Suppression des données en double contenu dans la table  bdc_statut
        CREATE INDEX IF NOT EXISTS bdc_statut_id_idx ON taxonomie.bdc_statut (id);

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
    """
        )
    )

    # Structure BDC_Statut
    logger.info("Import raw bdc_statut into structured table")
    query = text(
        importlib.resources.read_text("apptax.migrations.data", "taxonomie_bdc_statuts.sql")
    )
    db.session.execute(query)


def import_data_dbc_status_15():
    """
    Import des données brutes de la base bdc_status v15  en base
    """
    db.session.execute(
        text(
            """
        TRUNCATE TABLE  taxonomie.bdc_statut_type CASCADE;
        TRUNCATE TABLE  taxonomie.bdc_statut;
    """
        )
    )
    db.session.commit()

    with open_remote_file(
        base_url, "BDC-statuts-15.zip", open_fct=ZipFile, data_dir="tmp"
    ) as archive:
        with archive.open("BDC_STATUTS_TYPES_15.csv") as f:
            logger.info("Insert BDC_STATUTS_TYPES_15 table…")
            copy_from_csv(
                f,
                table_name="bdc_statut_type",
                delimiter=",",
            )
        with archive.open("BDC_STATUTS_15.csv") as f:
            logger.info("Insert bdc_statut table…")
            copy_from_csv(
                f,
                table_name="bdc_statut",
                encoding="WIN1252",
                delimiter=",",
                dest_cols=(
                    "cd_nom",
                    "cd_ref",
                    "cd_sup",
                    "cd_type_statut",
                    "lb_type_statut",
                    "regroupement_type",
                    "code_statut",
                    "label_statut",
                    "rq_statut",
                    "cd_sig",
                    "cd_doc",
                    "lb_nom",
                    "lb_auteur",
                    "nom_complet_html",
                    "nom_valide_html",
                    "regne",
                    "phylum",
                    "classe",
                    "ordre",
                    "famille",
                    "group1_inpn",
                    "group2_inpn",
                    "lb_adm_tr",
                    "niveau_admin",
                    "cd_iso3166_1",
                    "cd_iso3166_2",
                    "full_citation",
                    "doc_url",
                    "thematique",
                    "type_value",
                ),
            )

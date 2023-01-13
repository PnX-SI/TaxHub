import importlib.resources
from csv import DictReader
from io import TextIOWrapper
from zipfile import ZipFile

from alembic import op
import sqlalchemy as sa
from sqlalchemy.schema import Table, MetaData

from utils_flask_sqla.migrations.utils import open_remote_file

from apptax.database import db


def import_bdc_statuts(logger, base_url, zipfile, status_types_file, status_file):
    with open_remote_file(base_url, zipfile, open_fct=ZipFile) as archive:
        with archive.open(status_types_file) as f:
            logger.info("Insert BDC statuts types…")
            copy_from_csv(f, "bdc_statut_type")
        with archive.open(status_file) as f:
            logger.info("Insert BDC statuts…")
            copy_from_csv(
                f,
                "bdc_statut",
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

    logger.info("Populate BDC statuts…")
    db.session.execute(
        importlib.resources.read_text("apptax.migrations.data", "taxonomie_bdc_statuts.sql")
    )

    populate_bdc_statut_cor_text_area(logger)

    # FIXME: pourquoi on installe cet index si c’est pour le supprimer ?
    # db.session.execute("DROP INDEX taxonomie.bdc_statut_id_idx")


def populate_bdc_statut_cor_text_area(logger):
    # Clean table before populate

    logger.info("Populate Link BDC statuts with Areas…")

    db.session.execute(
        """
    TRUNCATE TABLE taxonomie.bdc_statut_cor_text_area;
    """
    )
    # Populate table
    db.session.execute(
        """
        WITH regions AS (
            SELECT jsonb_array_elements('[
                { "type": "old_r", "code" : "11", "name" :"Île-de-France", "deps": ["75","77","78","91","92","93","94","95"] },
                { "type": "old_r", "code" : "21", "name" :"Champagne-Ardenne", "deps": ["08","10","51","52"] },
                { "type": "old_r", "code" : "22", "name" :"Picardie", "deps": ["02","60","80"] },
                { "type": "old_r", "code" : "23", "name" :"Haute-Normandie", "deps": ["27", "76"] },
                { "type": "old_r", "code" : "24", "name" :"Centre", "deps": ["18","28","36","37","41","45"] },
                { "type": "old_r", "code" : "25", "name" :"Basse-Normandie", "deps": ["14","50","61"] },
                { "type": "old_r", "code" : "26", "name" :"Bourgogne", "deps": ["21","58","71","89"] },
                { "type": "old_r", "code" : "31", "name" :"Nord-Pas-de-Calais", "deps": ["59", "62"] },
                { "type": "old_r", "code" : "41", "name" :"Lorraine", "deps": ["54","55","57","88"] },
                { "type": "old_r", "code" : "42", "name" :"Alsace", "deps": ["67", "68"] },
                { "type": "old_r", "code" : "43", "name" :"Franche-Comté", "deps": ["25","39","70","90"] },
                { "type": "old_r", "code" : "52", "name" :"Pays de la Loire", "deps": ["44","49","53","72","85"] },
                { "type": "old_r", "code" : "53", "name" :"Bretagne", "deps": ["22","29","35","56"] },
                { "type": "old_r", "code" : "54", "name" :"Poitou-Charentes", "deps": ["16","17","79","86"] },
                { "type": "old_r", "code" : "72", "name" :"Aquitaine", "deps": ["24","33","40","47","64"] },
                { "type": "old_r", "code" : "73", "name" :"Midi-Pyrénées", "deps": ["09","12","31","32","46","65","81","82"] },
                { "type": "old_r", "code" : "74", "name" :"Limousin", "deps": ["19","23","87"] },
                { "type": "old_r", "code" : "82", "name" :"Rhône-Alpes", "deps": ["01","07","26","38","42","69","73","74"] },
                { "type": "old_r", "code" : "83", "name" :"Auvergne", "deps": ["03", "15", "43", "63"] },
                { "type": "old_r", "code" : "91", "name" :"Languedoc-Roussillon", "deps": ["11","30","34","48","66"] },
                { "type": "old_r", "code" : "93", "name" :"Provence-Alpes-Côte d’Azur", "deps": ["04", "05", "06", "13", "83", "84"] },
                { "type": "old_r", "code" : "94", "name" :"Corse", "deps": ["2A", "2B"] },
                { "type": "new_r", "code" : "11", "name" :"Île-de-France", "deps": ["75","77","78","91","92","93","94","95"] },
                { "type": "new_r", "code" : "24", "name" :"Centre-Val de Loire", "deps": ["18","28","36","37","41","45"] },
                { "type": "new_r", "code" : "27", "name" :"Bourgogne-Franche-Comté", "deps": ["21","25","39","58","70","71","89","90"] },
                { "type": "new_r", "code" : "28", "name" :"Normandie", "deps": ["14","27","50","61","76"] },
                { "type": "new_r", "code" : "32", "name" :"Hauts-de-France", "deps": ["02", "59", "60", "62", "80"] },
                { "type": "new_r", "code" : "44", "name" :"Grand Est", "deps": ["08","10","51","52","54","55","57","67","68","88"] },
                { "type": "new_r", "code" : "52", "name" :"Pays de la Loire", "deps": ["44","49","53","72","85"] },
                { "type": "new_r", "code" : "53", "name" :"Bretagne", "deps": ["22","29","35","56"] },
                { "type": "new_r", "code" : "75", "name" :"Nouvelle-Aquitaine", "deps": ["16","17","19","23","24","33","40","47","64","79","86","87"] },
                { "type": "new_r", "code" : "76", "name" :"Occitanie", "deps": ["09", "11", "12", "30", "31", "32", "34", "46", "48", "65", "66", "81", "82"] },
                { "type": "new_r", "code" : "84", "name" :"Auvergne-Rhône-Alpes", "deps": ["01", "03", "07", "15", "26", "38", "42", "43", "63", "69", "73", "74"] },
                { "type": "new_r", "code" : "93", "name" :"Provence-Alpes-Côte d’Azur", "deps": ["04", "05", "06", "13", "83", "84"] },
                { "type": "new_r", "code" : "94", "name" :"Corse", "deps": ["2A", "2B"] }
            ]'::jsonb)AS d
        ), regions_dep AS (
            SELECT jsonb_array_elements_text(d->'deps') AS dep, d->>'code'  AS code, d->>'type' AS type
            FROM regions
        ), regions_dep_areas AS (
            SELECT la.id_area, d.code, d.type
            FROM ref_geo.l_areas la
            JOIN regions_dep d ON d.dep = la.area_code
            WHERE id_type = ref_geo.get_id_area_type('DEP')
        ),
        texts AS (
            SELECT -- Si 'TERFXFR', 'ETATFRA' insertion de tous les départements
            bst.id_text,
            la.id_area
            FROM taxonomie.bdc_statut_text AS bst,
            ref_geo.l_areas AS la
            WHERE la.id_type = ref_geo.get_id_area_type('DEP')
            AND bst.cd_sig IN ('TERFXFR', 'ETATFRA')
            UNION
            SELECT DISTINCT -- Si département
            bst.id_text,
            (
                SELECT id_area
                FROM ref_geo.l_areas
                WHERE area_code = REPLACE(cd_sig, 'INSEED', '')
                    AND id_type = ref_geo.get_id_area_type('DEP')
            )
            FROM taxonomie.bdc_statut_text AS bst
            WHERE cd_sig ILIKE 'INSEED%'
            UNION
            SELECT DISTINCT -- Si nouvelle région
            bst.id_text,
            nrs.id_area
            FROM taxonomie.bdc_statut_text AS bst
            JOIN regions_dep_areas AS nrs ON (REPLACE(cd_sig, 'INSEENR', '') = nrs.code) AND nrs.TYPE= 'new_r'
            WHERE cd_sig ILIKE 'INSEENR%'
            UNION
            SELECT DISTINCT -- Si ancienne région
            bst.id_text,
            ors.id_area
            FROM taxonomie.bdc_statut_text AS bst
            JOIN regions_dep_areas AS ors ON (REPLACE(cd_sig, 'INSEER', '') = ors.code) AND ors.TYPE = 'old_r'
            WHERE cd_sig ILIKE 'INSEER%'
        )
        INSERT INTO taxonomie.bdc_statut_cor_text_area (id_text, id_area)
        SELECT id_text, id_area
        FROM texts AS t
        WHERE t.id_area IS NOT NULL
        ORDER BY t.id_text, t.id_area ASC;
     """
    )


def truncate_bdc_statuts():
    db.session.execute(
        """
        TRUNCATE
            taxonomie.bdc_statut,
            taxonomie.bdc_statut_type,
            taxonomie.bdc_statut_text,
            taxonomie.bdc_statut_values,
            taxonomie.bdc_statut_taxons,
            taxonomie.bdc_statut_cor_text_values,
            taxonomie.bdc_statut_cor_text_area
        """
    )


def refresh_taxref_vm():
    db.session.execute("REFRESH MATERIALIZED VIEW taxonomie.vm_classe")
    db.session.execute("REFRESH MATERIALIZED VIEW taxonomie.vm_famille")
    db.session.execute("REFRESH MATERIALIZED VIEW taxonomie.vm_group1_inpn")
    db.session.execute("REFRESH MATERIALIZED VIEW taxonomie.vm_group2_inpn")
    db.session.execute("REFRESH MATERIALIZED VIEW taxonomie.vm_ordre")
    db.session.execute("REFRESH MATERIALIZED VIEW taxonomie.vm_phylum")
    db.session.execute("REFRESH MATERIALIZED VIEW taxonomie.vm_regne")
    db.session.execute("REFRESH MATERIALIZED VIEW taxonomie.vm_taxref_list_forautocomplete")


def get_csv_field_names(f, encoding, delimiter):
    if encoding == "WIN1252":  # postgresql encoding
        encoding = "cp1252"  # python encoding
    t = TextIOWrapper(f, encoding=encoding)
    reader = DictReader(t, delimiter=delimiter)
    field_names = reader.fieldnames
    t.detach()  # avoid f to be closed on t garbage collection
    f.seek(0)
    return field_names


"""
Insert CSV file into specified table.
If source columns are specified, CSV file in copied in a temporary table,
then data restricted to specified source columns are copied in final table.
"""


def copy_from_csv(
    f,
    table_name,
    dest_cols="",
    source_cols=None,
    schema="taxonomie",
    header=True,
    encoding=None,
    delimiter=None,
):
    bind = db.session.get_bind()
    metadata = MetaData(bind=bind)
    if dest_cols:
        dest_cols = " (" + ", ".join(dest_cols) + ")"
    if source_cols:
        final_table_name = table_name
        final_table_cols = dest_cols
        table_name = f"import_{table_name}"
        dest_cols = ""
        field_names = get_csv_field_names(f, encoding=encoding, delimiter=delimiter)
        table = Table(
            table_name,
            metadata,
            *[sa.Column(c, sa.String) for c in map(str.lower, field_names)],
            schema=schema,
        )
        table.create(bind=db.session.connection())

    options = ["FORMAT CSV"]
    if header:
        options.append("HEADER")
    if encoding:
        options.append(f"ENCODING '{encoding}'")
    if delimiter:
        options.append(f"DELIMITER E'{delimiter}'")
    options = ", ".join(options)
    cursor = db.session.connection().connection.cursor()
    cursor.copy_expert(
        f"""
        COPY {schema}.{table_name}{dest_cols}
        FROM STDIN WITH ({options})
    """,
        f,
    )

    if source_cols:
        source_cols = ", ".join(source_cols)
        db.session.execute(
            f"""
        INSERT INTO {schema}.{final_table_name}{final_table_cols}
          SELECT {source_cols}
            FROM {schema}.{table_name};
        """
        )
        table.drop(bind=db.session.connection())

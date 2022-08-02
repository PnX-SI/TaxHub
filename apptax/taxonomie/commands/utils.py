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
    with open_remote_file(base_url, "BDC-Statuts-v14.zip", open_fct=ZipFile) as archive:
        with archive.open("BDC-Statuts-v14/BDC_STATUTS_TYPES_14.csv") as f:
            logger.info("Insert BDC statuts types…")
            copy_from_csv(f, "bdc_statut_type")
        with archive.open("BDC-Statuts-v14/BDC_STATUTS_14.csv") as f:
            logger.info("Insert BDC statuts…")
            copy_from_csv(
                f,
                "bdc_statut",
                encoding="ISO 8859-1",
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

    logger.info("Delete duplicate data in bdc_statut…")
    db.session.execute(
        """
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

    logger.info("Populate BDC statuts…")
    db.session.execute(
        importlib.resources.read_text("apptax.migrations.data", "taxonomie_bdc_statuts.sql")
    )

    # FIXME: pourquoi on installe cet index si c’est pour le supprimer ?
    # db.session.execute("DROP INDEX taxonomie.bdc_statut_id_idx")


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

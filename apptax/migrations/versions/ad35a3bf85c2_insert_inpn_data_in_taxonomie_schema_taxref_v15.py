"""insert inpn taxref v15 data in taxonomie schema

Revision ID: ad35a3bf85c2
Revises: f61f95136ec3
Create Date: 2022-03-14 11:26:20.887845

"""
import importlib.resources
from zipfile import ZipFile
from csv import DictReader
from io import TextIOWrapper

from alembic import op, context
import sqlalchemy as sa
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.exc import ProgrammingError
from utils_flask_sqla.migrations.utils import logger, open_remote_file

from apptax.taxonomie.models import Taxref


# revision identifiers, used by Alembic.
revision = 'ad35a3bf85c2'
down_revision = 'f61f95136ec3'
branch_labels = None
depends_on = ('c4415009f164')



base_url = 'http://geonature.fr/data/inpn/taxonomie/'


def get_csv_field_names(f, encoding, delimiter):
    if encoding == 'WIN1252':  # postgresql encoding
        encoding = 'cp1252'    # python encoding
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
def copy_from_csv(f, table, dest_cols='', source_cols=None,
                  schema='taxonomie', header=True, encoding=None, delimiter=None):
    tmp_table = False
    if dest_cols:
        dest_cols = ' (' + ', '.join(dest_cols) + ')'
    if source_cols:
        final_table = table
        final_table_cols = dest_cols
        table = f'import_{table}'
        dest_cols = ''
        field_names = get_csv_field_names(f, encoding=encoding, delimiter=delimiter)
        op.create_table(table, *[sa.Column(c, sa.String) for c in map(str.lower, field_names)], schema=schema)

    options = ["FORMAT CSV"]
    if header: options.append("HEADER")
    if encoding: options.append(f"ENCODING '{encoding}'")
    if delimiter: options.append(f"DELIMITER E'{delimiter}'")
    options = ', '.join(options)
    cursor = op.get_bind().connection.cursor()
    cursor.copy_expert(f"""
        COPY {schema}.{table}{dest_cols}
        FROM STDIN WITH ({options})
    """, f)

    if source_cols:
        source_cols = ', '.join(source_cols)
        op.execute(f"""
        INSERT INTO {schema}.{final_table}{final_table_cols}
          SELECT {source_cols}
            FROM {schema}.{table};
        """)
        op.drop_table(table, schema=schema)


def upgrade():
    # Test if table taxref is already populated => taxref is already install
    # Need to process upgrade data
    try:
        Taxref.query.one()
    except (NoResultFound, ProgrammingError):
        if not context.get_x_argument(as_dictionary=True).get("force-taxrefv14"):
            import_taxref_v15()
    except MultipleResultsFound:
        pass
    logger.info("Taxref is already populated you need to run migration process")

def import_taxref_v15():
    cursor = op.get_bind().connection.cursor()
    with open_remote_file(base_url, 'TAXREF_v15_2021.zip', open_fct=ZipFile) as archive:
        with archive.open('habitats_note.csv') as f:
            logger.info("Insert TAXREFv15 habitats…")
            copy_from_csv(f, 'bib_taxref_habitats', encoding='WIN1252', delimiter=';')
        with archive.open('rangs_note.csv') as f:
            logger.info("Insert TAXREFv15 rangs…")
            copy_from_csv(f, 'bib_taxref_rangs', encoding='WIN1252', delimiter=';',
                dest_cols=('tri_rang', 'id_rang', 'nom_rang', 'nom_rang_en'))
        with archive.open('statuts_note.csv') as f:
            logger.info("Insert TAXREFv15 statuts…")
            copy_from_csv(f, 'bib_taxref_statuts', encoding='WIN1252', delimiter=';',
                dest_cols=('id_statut', 'nom_statut'),
                source_cols=('statut', 'description'))
        with archive.open('TAXREFv15.txt') as f:
            logger.info("Insert TAXREFv15 referentiel…")
            copy_from_csv(f, 'taxref', delimiter='\t',
                dest_cols=('cd_nom', 'id_statut', 'id_habitat', 'id_rang', 'regne', 'phylum',
                           'classe', 'ordre', 'famille', 'sous_famille', 'tribu', 'cd_taxsup',
                           'cd_sup', 'cd_ref', 'lb_nom', 'lb_auteur', 'nom_complet',
                           'nom_complet_html', 'nom_valide', 'nom_vern', 'nom_vern_eng',
                           'group1_inpn', 'group2_inpn', 'group3_inpn', 'url'),
                source_cols=('cd_nom::int', 'NULLIF(fr, \'\') as id_statut', 'habitat::int as id_habitat',
                             'rang as id_rang', 'regne', 'phylum', 'classe', 'ordre', 'famille',
                             'sous_famille', 'tribu', 'cd_taxsup::int', 'cd_sup::int', 'cd_ref::int', 'lb_nom',
                             'substring(lb_auteur, 1, 250)', 'nom_complet', 'nom_complet_html',
                             'nom_valide', 'substring(nom_vern,1,1000)', 'nom_vern_eng',
                             'group1_inpn', 'group2_inpn', 'group3_inpn', 'url'))

    with open_remote_file(base_url, 'BDC-statuts-15.zip', open_fct=ZipFile) as archive:
        with archive.open('BDC_STATUTS_TYPES_15.csv') as f:
            logger.info("Insert BDC statuts types…")
            copy_from_csv(f, 'bdc_statut_type')
        with archive.open('BDC_STATUTS_15.csv') as f:
            logger.info("Insert BDC statuts…")
            copy_from_csv(f, 'bdc_statut', encoding='ISO 8859-1',
                dest_cols=('cd_nom', 'cd_ref', 'cd_sup', 'cd_type_statut', 'lb_type_statut', 'regroupement_type',
                           'code_statut', 'label_statut', 'rq_statut', 'cd_sig', 'cd_doc', 'lb_nom', 'lb_auteur',
                           'nom_complet_html', 'nom_valide_html', 'regne', 'phylum', 'classe', 'ordre', 'famille',
                           'group1_inpn', 'group2_inpn', 'lb_adm_tr', 'niveau_admin', 'cd_iso3166_1',
                           'cd_iso3166_2', 'full_citation', 'doc_url', 'thematique', 'type_value'))

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

    logger.info("Populate BDC statuts…")
    op.execute(importlib.resources.read_text('apptax.migrations.data', 'taxonomie_bdc_statuts.sql'))

    # FIXME: pourquoi on installe cet index si c’est pour le supprimer ?
    #op.execute("DROP INDEX taxonomie.bdc_statut_id_idx")

    logger.info("Refresh materialized views…")
    op.execute("REFRESH MATERIALIZED VIEW taxonomie.vm_classe")
    op.execute("REFRESH MATERIALIZED VIEW taxonomie.vm_famille")
    op.execute("REFRESH MATERIALIZED VIEW taxonomie.vm_group1_inpn")
    op.execute("REFRESH MATERIALIZED VIEW taxonomie.vm_group2_inpn")
    op.execute("REFRESH MATERIALIZED VIEW taxonomie.vm_ordre")
    op.execute("REFRESH MATERIALIZED VIEW taxonomie.vm_phylum")
    op.execute("REFRESH MATERIALIZED VIEW taxonomie.vm_regne")
    op.execute("REFRESH MATERIALIZED VIEW taxonomie.vm_taxref_list_forautocomplete")


def downgrade():
    # FIXME vider les tables est-il acceptable ?
    # logger.info("Truncate table…")
    # op.execute("""
    # TRUNCATE TABLE
    #     taxonomie.bdc_statut_cor_text_values,
    #     taxonomie.bdc_statut,
    #     taxonomie.bdc_statut_taxons,
    #     taxonomie.bdc_statut_text,
    #     taxonomie.bdc_statut_type,
    #     taxonomie.taxref_protection_especes,
    #     taxonomie.taxref_protection_articles,
    #     taxonomie.taxref_protection_articles_structure,
    #     taxonomie.taxref,
    #     taxonomie.cor_nom_liste,
    #     taxonomie.bib_noms,
    #     taxonomie.taxref_liste_rouge_fr,
    #     taxonomie.bib_taxref_categories_lr,
    #     taxonomie.bib_taxref_statuts,
    #     taxonomie.bib_taxref_rangs,
    #     taxonomie.bib_taxref_habitats,
    #     taxonomie.t_medias
    # """)

    logger.info("Refresh materialized views…")
    op.execute("REFRESH MATERIALIZED VIEW taxonomie.vm_classe")
    op.execute("REFRESH MATERIALIZED VIEW taxonomie.vm_famille")
    op.execute("REFRESH MATERIALIZED VIEW taxonomie.vm_group1_inpn")
    op.execute("REFRESH MATERIALIZED VIEW taxonomie.vm_group2_inpn")
    op.execute("REFRESH MATERIALIZED VIEW taxonomie.vm_ordre")
    op.execute("REFRESH MATERIALIZED VIEW taxonomie.vm_phylum")
    op.execute("REFRESH MATERIALIZED VIEW taxonomie.vm_regne")
    op.execute("REFRESH MATERIALIZED VIEW taxonomie.vm_taxref_list_forautocomplete")

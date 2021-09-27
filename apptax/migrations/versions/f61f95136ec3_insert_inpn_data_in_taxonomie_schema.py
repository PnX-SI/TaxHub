"""insert inpn data in taxonomie schema

Revision ID: f61f95136ec3
Create Date: 2021-09-22 10:31:52.366014

"""
import logging
import importlib.resources
from zipfile import ZipFile
from collections.abc import Iterable, Mapping
from csv import DictReader
from io import TextIOWrapper

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
    cursor = op.get_bind().connection.cursor()
    with open_remote_file(base_url, 'TAXREF_v14_2020.zip', open_fct=ZipFile) as archive:
        with archive.open('TAXREF_v14_2020/habitats_note.csv') as f:
            logger.info("Insert TAXREFv14 habitats…")
            copy_from_csv(f, 'bib_taxref_habitats', encoding='WIN1252', delimiter=';')
        with archive.open('TAXREF_v14_2020/rangs_note.csv') as f:
            logger.info("Insert TAXREFv14 rangs…")
            copy_from_csv(f, 'bib_taxref_rangs', delimiter='\t',
                dest_cols=('tri_rang', 'id_rang', 'nom_rang', 'nom_rang_en'))
        with archive.open('TAXREF_v14_2020/statuts_note.csv') as f:
            logger.info("Insert TAXREFv14 statuts…")
            copy_from_csv(f, 'bib_taxref_statuts', encoding='WIN1252', delimiter=';',
                dest_cols=('id_statut', 'nom_statut'),
                source_cols=('statut', 'description'))
        with archive.open('TAXREF_v14_2020/TAXREFv14.txt') as f:
            logger.info("Insert TAXREFv14 referentiel…")
            copy_from_csv(f, 'taxref', delimiter='\t',
                dest_cols=('cd_nom', 'id_statut', 'id_habitat', 'id_rang', 'regne', 'phylum',
                           'classe', 'ordre', 'famille', 'sous_famille', 'tribu', 'cd_taxsup',
                           'cd_sup', 'cd_ref', 'lb_nom', 'lb_auteur', 'nom_complet',
                           'nom_complet_html', 'nom_valide', 'nom_vern', 'nom_vern_eng',
                           'group1_inpn', 'group2_inpn', 'url'),
                source_cols=('cd_nom::int', 'fr as id_statut', 'habitat::int as id_habitat',
                             'rang as id_rang', 'regne', 'phylum', 'classe', 'ordre', 'famille',
                             'sous_famille', 'tribu', 'cd_taxsup::int', 'cd_sup::int', 'cd_ref::int', 'lb_nom',
                             'substring(lb_auteur, 1, 250)', 'nom_complet', 'nom_complet_html',
                             'nom_valide', 'substring(nom_vern,1,1000)', 'nom_vern_eng',
                             'group1_inpn', 'group2_inpn', 'url'))

    with open_remote_file(base_url, 'ESPECES_REGLEMENTEES_v11.zip', open_fct=ZipFile) as archive:
        with archive.open('PROTECTION_ESPECES_TYPES_11.csv') as f:
            logger.info("Insert protection especes types…")
            copy_from_csv(f, 'taxref_protection_articles',
                dest_cols=('cd_protection', 'article', 'intitule', 'arrete', 'url_inpn',
                           'cd_doc', 'url', 'date_arrete', 'type_protection'))

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
            logger.info("Insert BDC statuts types…")
            copy_from_csv(f, 'bdc_statut_type')
        with archive.open('BDC-Statuts-v14/BDC_STATUTS_14.csv') as f:
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
    op.execute("""
    TRUNCATE TABLE
        taxonomie.bdc_statut_cor_text_values,
        taxonomie.bdc_statut,
        taxonomie.bdc_statut_taxons,
        taxonomie.bdc_statut_text,
        taxonomie.bdc_statut_type,
        taxonomie.taxref_protection_especes,
        taxonomie.taxref_protection_articles,
        taxonomie.taxref_protection_articles_structure,
        taxonomie.taxref,
        taxonomie.cor_nom_liste,
        taxonomie.bib_noms,
        taxonomie.taxref_liste_rouge_fr,
        taxonomie.bib_taxref_categories_lr,
        taxonomie.bib_taxref_statuts,
        taxonomie.bib_taxref_rangs,
        taxonomie.bib_taxref_habitats,
        taxonomie.t_medias
    """)

    logger.info("Refresh materialized views…")
    op.execute("REFRESH MATERIALIZED VIEW taxonomie.vm_classe")
    op.execute("REFRESH MATERIALIZED VIEW taxonomie.vm_famille")
    op.execute("REFRESH MATERIALIZED VIEW taxonomie.vm_group1_inpn")
    op.execute("REFRESH MATERIALIZED VIEW taxonomie.vm_group2_inpn")
    op.execute("REFRESH MATERIALIZED VIEW taxonomie.vm_ordre")
    op.execute("REFRESH MATERIALIZED VIEW taxonomie.vm_phylum")
    op.execute("REFRESH MATERIALIZED VIEW taxonomie.vm_regne")
    op.execute("REFRESH MATERIALIZED VIEW taxonomie.vm_taxref_list_forautocomplete")

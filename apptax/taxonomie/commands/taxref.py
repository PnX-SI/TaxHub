import click
from flask.cli import with_appcontext

from apptax.database import db
from apptax.taxonomie.models import Taxref, TaxrefBdcStatutText

from .utils import truncate_bdc_statuts
from .taxref_v14 import import_v14, import_bdc_v14
from .taxref_v15 import import_v15, import_bdc_v15, link_bdc_statut_to_areas
from .migrate_to_v15.commands import migrate_to_v15


@click.group(help="Manager TaxRef referentials.")
def taxref():
    pass


@taxref.command()
@with_appcontext
def info():
    click.echo("TaxRef :")
    taxref_count = db.session.query(Taxref.cd_nom).count()
    click.echo(f"\tNombre de taxons : {taxref_count}")
    status_count = db.session.query(TaxrefBdcStatutText.id_text).count()
    enabled_status_count = (
        db.session.query(TaxrefBdcStatutText.id_text).filter_by(enable=True).count()
    )
    click.echo("Base de connaissances :")
    click.echo(f"\tStatuts (actifs / total) : {enabled_status_count} / {status_count}")


@taxref.command(help="Supprimer toutes les données TaxRef.")
@with_appcontext
def delete():
    click.confirm("Êtes vous sûr de vouloir supprimer toutes les données TaxRef ?", abort=True)
    tables = [
        "taxonomie.bdc_statut",
        "taxonomie.bdc_statut_values",
        "taxonomie.bdc_statut_taxons",
        "taxonomie.bdc_statut_cor_text_area",
        "taxonomie.bdc_statut_cor_text_values",
        "taxonomie.bdc_statut_text",
        "taxonomie.bdc_statut_type",
        "taxonomie.bib_noms",
        "taxonomie.taxref_protection_especes",
        "taxonomie.taxref",
        "taxonomie.taxref_liste_rouge_fr",
        "taxonomie.taxref_protection_articles",
        "taxonomie.taxref_protection_articles_structure",
        "taxonomie.bib_taxref_categories_lr",
        "taxonomie.bib_taxref_statuts",
        "taxonomie.bib_taxref_rangs",
        "taxonomie.bib_taxref_habitats",
    ]
    with click.progressbar(
        length=len(tables), label="Delete from table", item_show_func=lambda t: t, show_eta=False
    ) as bar:
        for i, table in enumerate(tables):
            bar.update(n_steps=i, current_item=table)
            db.session.execute(f"DELETE FROM {table}")

    db.session.commit()


@taxref.command(help="Supprimer la base de connaissance des statuts de protection.")
@with_appcontext
def delete_bdc():
    click.confirm(
        "Êtes vous sûr de vouloir supprimer toutes les données de la BDC Statuts ?",
        abort=True,
    )
    truncate_bdc_statuts()
    db.session.commit()


taxref.add_command(import_v14)
taxref.add_command(import_bdc_v14)
taxref.add_command(import_v15)
taxref.add_command(import_bdc_v15)
taxref.add_command(migrate_to_v15)
taxref.add_command(link_bdc_statut_to_areas)

import os
import csv
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import request, json, url_for, current_app, redirect
from jinja2.utils import markupsafe

from flask_admin import form
from flask_admin.contrib.sqla import ModelView
from flask_admin.model.form import InlineFormAdmin
from flask_admin.model.ajax import AjaxModelLoader, DEFAULT_PAGE_SIZE

from flask_admin.base import expose
from flask_admin.model.helpers import get_mdict_item_or_list

from flask_admin.form.upload import FileUploadField
from flask_admin.form.fields import Select2Field

from flask_admin.model.template import LinkRowAction, EndpointLinkRowAction
from flask_admin.contrib.sqla.filters import BaseSQLAFilter

from sqlalchemy import or_
from wtforms import Form, BooleanField, SelectField

from apptax.database import db
from apptax.taxonomie.models import (
    BibThemes,
    Taxref,
    BibAttributs,
    CorTaxonAttribut,
    BibListes,
    CorNomListe,
    TMedias,
)


def taxref_media_file_name(obj, file_data):
    return secure_filename(f"{obj.taxon.cd_ref}_{file_data.filename}")


class PopulateBibListesForm(Form):
    delimiter = SelectField(label="delimiter", choices=[(",", ","), (";", ";")])
    with_header = BooleanField(label="with_header")
    upload = FileUploadField("File")


class BibListesView(ModelView):

    can_view_details = True
    column_list = ("picto", "code_liste", "nom_liste", "regne", "group2_inpn")
    column_filters = ["regne", "group2_inpn"]
    form_excluded_columns = ("code_liste", "cnl", "noms")

    column_extra_row_actions = [  # Add a new action button
        EndpointLinkRowAction("fa fa-download", ".import_cd_nom_view", "Populate list"),
    ]

    def get_picto_list():
        pictos = os.listdir(os.path.join(current_app.static_folder, "images", "pictos"))
        return [(p, p) for p in pictos]

    form_extra_fields = {"picto": Select2Field("Picto", choices=get_picto_list(), default="")}

    def _list_picto(view, context, model, name):
        path = None
        if model.picto:
            path = url_for(
                "static",
                filename=f"{model.picto}",
                _external=True,
            )
        elif model.url:
            path = model.url

        if not path:
            return
        return markupsafe.Markup(f"<img src='{path}'>")

    column_formatters = {"picto": _list_picto}

    @expose("/import_cd_nom/", methods=("GET", "POST"))
    def import_cd_nom_view(self, *args, **kwargs):

        form = PopulateBibListesForm(request.form)

        if request.method == "POST":
            id_list = get_mdict_item_or_list(request.args, "id")
            delimiter = request.form.get("delimiter", default=",")
            with_header = request.form.get("with_header", default=False)
            file = request.files["upload"]

            fstring = file.read().decode()
            inputcsv = csv.reader(fstring.splitlines(), delimiter=delimiter)

            bibliste = BibListes.query.get(id_list)
            # if header skip first line
            if with_header:
                next(inputcsv, None)
            for row in inputcsv:
                tax = Taxref.query.get(row[0])
                if tax:
                    tax.liste.append(bibliste)

            db.session.commit()

            return redirect(self.get_url(".index_view"))

        return self.render("admin/populate_biblist.html", form=form)


class FilterList(BaseSQLAFilter):
    # Override to create an appropriate query and apply a
    # filter to said query with the passed value from the filter UI
    def apply(self, query, value, alias=None):
        return query.join(CorNomListe).join(BibListes).filter(BibListes.id_liste == value)

    # readable operation name. This appears in the middle filter line drop-down
    def operation(self):
        return "equals"

    # Override to provide the options for the filter -
    #   in this case it"s a list of the titles of the Client model
    def get_options(self, view):
        return [(list.id_liste, list.nom_liste) for list in BibListes.query.all()]


class InlineMediaForm(InlineFormAdmin):
    form_label = "Médias"

    form_extra_fields = {
        "chemin": form.ImageUploadField(
            label="Image",
            base_path=current_app.config["UPLOAD_FOLDER"],
            url_relative_path="",
            namegen=taxref_media_file_name,
            thumbnail_size=(150, 150, True),
            endpoint="media",
        )
    }

    def __init__(self):
        return super(InlineMediaForm, self).__init__(TMedias)


class TaxrefView(ModelView):

    can_create = False
    # can_edit = False
    can_delete = False
    can_view_details = True
    inline_models = (InlineMediaForm(),)

    form_excluded_columns = (
        "cd_nom",
        "id_statut",
        "id_habitat",
        "id_rang",
        "regne",
        "phylum",
        "classe",
        "regne",
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
        "nom_vern",
        "nom_valide",
        "nom_vern_eng",
        "group1_inpn",
        "group2_inpn",
        "url",
        "cnl",
        "attributs",
    )

    column_searchable_list = ["nom_complet", "cd_nom"]
    column_filters = [
        "regne",
        "group2_inpn",
        "classe",
        "ordre",
        "famille",
        FilterList(
            column="liste",
            name="Est dans la liste",
        ),
    ]

    column_auto_select_related = True
    column_hide_backrefs = False

    edit_template = "admin/edit_taxref.html"
    details_template = "admin/details_taxref.html"

    def _get_theme_attributes(self, taxon_name):
        return (
            db.session.query(BibThemes)
            .filter(or_(BibAttributs.regne == taxon_name.regne, BibAttributs.regne == None))
            .filter(
                or_(
                    BibAttributs.group2_inpn == taxon_name.group2_inpn,
                    BibAttributs.group2_inpn == None,
                )
            )
            .filter(BibAttributs.id_theme == BibThemes.id_theme)
            .order_by(BibAttributs.ordre)
            .all()
        )

    def _get_attributes_value(self, taxon_name, theme_attributs_def):
        attributes_val = {}
        for a in [a for attrs in [t.attributs for t in theme_attributs_def] for a in attrs]:
            # Désérialisation du champ liste_valeur_attribut
            attributes_val[a.id_attribut] = json.loads(a.liste_valeur_attribut)
            # Ajout des valeurs du taxon si elle existe
            taxon_att = [
                tatt for tatt in taxon_name.attributs if tatt.id_attribut == a.id_attribut
            ]
            if taxon_att:
                attributes_val[a.id_attribut]["taxon_attr_value"] = taxon_att[0].valeur_attribut
        return attributes_val

    @expose("/details/", methods=("GET",))
    def details_view(self):
        id = get_mdict_item_or_list(request.args, "id")
        taxon_name = db.session.query(Taxref).get(id)
        # Get attributes
        theme_attributs_def = self._get_theme_attributes(taxon_name)
        attributes_val = self._get_attributes_value(taxon_name, theme_attributs_def)
        self._template_args["theme_attributs_def"] = theme_attributs_def
        self._template_args["attributes_val"] = attributes_val

        return super(TaxrefView, self).details_view()

    @expose("/edit/", methods=("GET", "POST"))
    def edit_view(self):
        # Get Taxon data
        id = get_mdict_item_or_list(request.args, "id")
        taxon_name = db.session.query(Taxref).get(id)

        # Get attributes
        theme_attributs_def = self._get_theme_attributes(taxon_name)
        attributes_val = self._get_attributes_value(taxon_name, theme_attributs_def)
        if request.method == "POST":
            for f in request.form:
                if request.form[f] and f.startswith("attr."):
                    id_attr = f.split(".")[1]
                    value = request.form[f]
                    try:
                        model = (
                            db.session.query(CorTaxonAttribut)
                            .filter_by(cd_ref=taxon_name.cd_ref)
                            .filter_by(id_attribut=id_attr)
                            .one()
                        )
                    except Exception:
                        model = CorTaxonAttribut(cd_ref=taxon_name.cd_ref, id_attribut=id_attr)
                    model.valeur_attribut = value
                    db.session.add(model)
                    db.session.commit()
        self._template_args["theme_attributs_def"] = theme_attributs_def
        self._template_args["attributes_val"] = attributes_val
        return super(TaxrefView, self).edit_view()


class TaxrefAjaxModelLoader(AjaxModelLoader):
    def __init__(self, name, **options):
        super(TaxrefAjaxModelLoader, self).__init__(name, options)

    def format(self, model):
        if model:
            return (model.cd_ref, model.nom_complet)

        return None

    def get_one(self, pk):
        return Taxref.query.filter(Taxref.cd_nom == pk).first()

    def get_list(self, query, offset=0, limit=DEFAULT_PAGE_SIZE):
        results = (
            Taxref.query.filter(Taxref.nom_complet.ilike(f"{query}%"))
            .limit(limit)
            .offset(offset)
            .all()
        )

        return results


class TMediasView(ModelView):

    form_ajax_refs = {"taxon": TaxrefAjaxModelLoader("taxon")}

    form_extra_fields = {
        "chemin": form.ImageUploadField(
            label="Image",
            base_path=current_app.config["UPLOAD_FOLDER"],
            url_relative_path="",
            namegen=taxref_media_file_name,
            thumbnail_size=(150, 150, True),
            endpoint="media",
        )
    }

    def _list_thumbnail(view, context, model, name):
        path = None
        if model.chemin:
            path = url_for(
                "media",
                filename=form.thumbgen_filename(model.chemin),
                _external=True,
            )
        elif model.url:
            path = model.url

        if not path:
            return
        return markupsafe.Markup(f"<img src='{path}'>")

    column_formatters = {"chemin": _list_thumbnail}

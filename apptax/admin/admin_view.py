import os
from flask import request, json, url_for
from jinja2.utils import markupsafe

from flask_admin import form
from flask_admin.contrib.sqla import ModelView
from flask_admin.model.form import InlineFormAdmin
from flask_admin.form import ImageUploadField
from flask_admin.base import expose
from flask_admin.model.helpers import get_mdict_item_or_list

from flask_admin.model.template import  LinkRowAction
from flask_admin.contrib.sqla.filters import BaseSQLAFilter


from apptax.database import db
from apptax.taxonomie.models import (
    Taxref, BibAttributs, CorTaxonAttribut, BibListes, CorNomListe, TMedias
)

# Chemin des médias !! A CHANGER
file_path = os.path.join(os.path.dirname(__file__), "static/images")

# class TaxrefChoices(Iterator):
#     def __init__(self, first_item=None, field="regne"):
#         self.first_item = first_item
#         self.listval = None
#         self.field = field

#     def __next__(self):
#         if self.first_item is not None:
#             res = self.first_item
#             self.first_item = None
#             return res
#         if self.listval is None:
#             self.listval = (
#                 d[0] for d in db.session.query(
#                     getattr(Taxref, self.field)
#                 ).distinct(
#                 ).order_by(
#                     getattr(Taxref, self.field)
#                 ).all()
#             )
#         value = self.listval.__next__()
#         res = (value)
#         return res


class BibListesView(ModelView):

    # can_create = False
    # can_edit = False
    # can_delete = False
    can_view_details = True
    column_list = ("code_liste", "nom_liste", "picto", "regne", "group2_inpn")
    column_filters = ["regne", "group2_inpn"]
    form_excluded_columns = ("code_liste", "cnl")

    column_extra_row_actions = [
        LinkRowAction(
            "glyphicon glyphicon-play",
            "http://direct.link/?id={row_id}", title="COUCOU"
        ),
    ]

    # form_extra_fields = {
    #     "regne": SelectField(
    #         choices=TaxrefChoices(field="regne")
    #     ),
    #     "group2_inpn": SelectField(
    #         choices=TaxrefChoices(field="group2_inpn")
    #     )
    # }


class FilterList(BaseSQLAFilter):
    # Override to create an appropriate query and apply a
    # filter to said query with the passed value from the filter UI
    def apply(self, query, value, alias=None):
        return query.join(
            CorNomListe
            ).join(
                BibListes
            ).filter(BibListes.id_liste == value)

    # readable operation name. This appears in the middle filter line drop-down
    def operation(self):
        return u"equals"

    # Override to provide the options for the filter -
    #   in this case it"s a list of the titles of the Client model
    def get_options(self, view):
        return [
            (list.id_liste, list.nom_liste)
            for list in BibListes.query.all()
        ]


class InlineMediaForm(InlineFormAdmin):
    form_label = "Image"

    def __init__(self):
        return super(InlineMediaForm, self).__init__(TMedias)

    form_extra_fields = {
        "chemin": ImageUploadField("Image", base_path=file_path)
    }

class TaxrefView(ModelView):

    can_create = False
    # can_edit = False
    can_delete = False
    can_view_details = True
    inline_models = (InlineMediaForm(), )

    form_excluded_columns = (
        "cd_nom", "id_statut", "id_habitat", "id_rang", "regne", "phylum",
        "classe", "regne", "ordre", "famille", "sous_famille", "tribu",
        "cd_taxsup", "cd_sup", "cd_ref", "lb_nom", "lb_auteur", "nom_complet",
        "nom_complet_html", "nom_vern", "nom_valide", "nom_vern_eng",
        "group1_inpn", "group2_inpn", "url", "cnl"
    )

    column_searchable_list = ["nom_complet", "cd_nom"]
    column_filters = [
        "regne", "group2_inpn", "classe", "ordre", "famille",
        FilterList(
            column="liste", name="Est dans la liste",
        )
    ]

    column_auto_select_related = True
    column_hide_backrefs = False

    edit_template = "admin/edit_taxref.html"

    @expose("/edit/", methods=("GET", "POST"))
    def edit_view(self):
        # Get Taxon data
        id = get_mdict_item_or_list(request.args, "id")
        taxon_name = db.session.query(Taxref).get(id)
        taxon_attr = db.session.query(CorTaxonAttribut).filter_by(cd_ref = taxon_name.cd_ref).all()

        # Get attributes
        from sqlalchemy import or_
        attr = db.session.query(BibAttributs).filter(
            or_(
                BibAttributs.regne == taxon_name.regne,
                BibAttributs.regne == None
            )
        ).filter(
            or_(
                BibAttributs.group2_inpn == taxon_name.group2_inpn,
                BibAttributs.group2_inpn == None
                )
        ).all()

        attributes_val = {}
        for a in attr:
            attributes_val[a.id_attribut] = json.loads(a.liste_valeur_attribut)
            taxon_att = [tatt for tatt in taxon_attr if tatt.id_attribut == a.id_attribut]
            if taxon_att:
                attributes_val[a.id_attribut]["taxon_attr_value"] = taxon_att[0].valeur_attribut

        if request.method == "POST":
            for f in request.form:
                if request.form[f] and f.startswith("attr."):
                    id_attr = f.split(".")[1]
                    value = request.form[f]
                    try:
                        model = db.session.query(
                            CorTaxonAttribut
                        ).filter_by(
                            cd_ref=taxon_name.cd_ref
                        ).filter_by(
                            id_attribut=id_attr
                        ).one()
                    except Exception:
                        model = CorTaxonAttribut(
                            cd_ref=taxon_name.cd_ref,
                            id_attribut=id_attr
                        )
                    model.valeur_attribut = value
                    db.session.add(model)
                    db.session.commit()
        self._template_args["attributes"] = attr
        self._template_args["attributes_val"] = attributes_val
        return super(TaxrefView, self).edit_view()


class TMediasView(ModelView):
    def _list_thumbnail(view, context, model, name):
        path = None
        if model.chemin:
            path = url_for(
                "static",
                filename="images/" + form.thumbgen_filename(model.chemin)
            )
        elif model.url:
            path = model.url

        if not path:
            return
        return markupsafe.Markup(f"<img src='${path}' height='200px' width='300px'>")

    column_formatters = {
        "chemin": _list_thumbnail
    }

    form_extra_fields = {
        "chemin": form.ImageUploadField(
            "Image",
            base_path=file_path,
            thumbnail_size=(200, 300, True)
        )
    }

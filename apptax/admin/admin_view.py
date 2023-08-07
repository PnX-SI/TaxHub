import os
import csv

from flask import request, json, url_for, redirect, flash, g, current_app
from flask_admin.model.template import macro
from jinja2.utils import markupsafe


from flask_admin import form, BaseView
from flask_admin.contrib.sqla import ModelView
from flask_admin.model.form import InlineFormAdmin
from flask_admin.model.ajax import AjaxModelLoader, DEFAULT_PAGE_SIZE

from flask_admin.base import expose
from flask_admin.model.helpers import get_mdict_item_or_list

from flask_admin.form.upload import FileUploadField

from flask_admin.model.template import EndpointLinkRowAction

from sqlalchemy import or_, inspect

from sqlalchemy.orm import joinedload
from sqlalchemy.orm import undefer

from wtforms import Form, BooleanField, SelectField, PasswordField, StringField

from wtforms.validators import ValidationError, DataRequired, Length

from apptax.database import db
from apptax.taxonomie.models import (
    BibThemes,
    Taxref,
    BibAttributs,
    CorTaxonAttribut,
    TMedias,
)
from apptax.admin.utils import taxref_media_file_name, get_user_permission
from pypnusershub.utils import get_current_app_id
from apptax.admin.admin import adresses
from apptax.admin.utils import PopulateBibListeException, populate_bib_liste
from apptax.admin.filters import (
    TaxrefDistinctFilter,
    FilterTaxrefAttr,
    FilterBiblist,
    FilterIsValidName,
    FilterMedia,
    FilterAttributes,
)


class FlaskAdminProtectedMixin:
    # Define permission level for extra actions
    # Dict : {
    #       ".action_endpoint" : level
    #   }
    extra_actions_perm = None

    def _can_action(self, level):
        if not g.current_user:
            return False
        user_perm = get_user_permission(g.current_user.id_role)
        if not user_perm:
            return False
        return user_perm.id_droit_max >= level

    def get_list_row_actions(self):
        """
        Test permission on extra row action
        """
        actions = super().get_list_row_actions()

        if not self.extra_actions_perm:
            return actions

        for extra_action_perm in self.extra_actions_perm:
            actions = self._can_extra_action(
                actions=actions,
                extra_action_name=extra_action_perm,
                extra_action_level=self.extra_actions_perm[extra_action_perm],
            )

        return actions

    def _can_extra_action(self, actions, extra_action_name, extra_action_level):
        for id, extra_action in enumerate(actions):
            if extra_action in self.column_extra_row_actions:
                if extra_action.endpoint == extra_action_name and not self._can_action(
                    extra_action_level
                ):
                    actions.pop(id)
        return actions

    @property
    def can_export(self):
        return self._can_action(0)


class LoginForm(Form):
    identifiant = StringField("identifiant", validators=[DataRequired(), Length(1, 64)])
    password = PasswordField("Password", validators=[DataRequired()])


class LoginView(BaseView):
    def is_visible(self):
        # Hide view in navbar
        return False

    @expose("/", methods=("GET", "POST"))
    def index(self):
        form = LoginForm(request.form)
        return self.render("admin/login.html", form=form)

    def render(self, template, **kwargs):
        self.extra_js = [url_for("configs.get_config"), url_for(".static", filename="js/login.js")]
        self._template_args["RETURN_URL"] = get_mdict_item_or_list(request.args, "redirect")
        self._template_args["IP_APP"] = get_current_app_id()
        return super(LoginView, self).render(template, **kwargs)


class PopulateBibListesForm(Form):
    delimiter = SelectField(label="Delimiter", choices=[(",", ","), (";", ";")])
    with_header = BooleanField(label="With header")
    upload = FileUploadField(label="File", allowed_extensions=("csv",))


class BibThemesView(
    FlaskAdminProtectedMixin,
    ModelView,
):
    @property
    def can_create(self):
        return self._can_action(6)

    @property
    def can_edit(self):
        return self._can_action(6)

    @property
    def can_delete(self):
        return self._can_action(6)

    extra_actions_perm = None


class BibListesView(FlaskAdminProtectedMixin, ModelView):
    @property
    def can_create(self):
        return self._can_action(6)

    @property
    def can_edit(self):
        return self._can_action(6)

    @property
    def can_delete(self):
        return self._can_action(6)

    extra_actions_perm = {".import_cd_nom_view": 5}

    can_view_details = True

    column_list = ("regne", "group2_inpn", "code_liste", "nom_liste", "nb_taxons")

    column_labels = dict(nb_taxons="Nb taxons")

    form_excluded_columns = ("cnl", "noms")

    column_extra_row_actions = [
        EndpointLinkRowAction("fa fa-download", ".import_cd_nom_view", "Populate list"),
    ]

    def on_model_change(self, form, model, is_created):
        """
        Force None on empty string regne
        """
        if model.regne and not model.regne.regne:
            model.regne = None

    def render(self, template, **kwargs):
        self.extra_js = [
            url_for("configs.get_config"),
            url_for(".static", filename="js/regne_group2_inpn.js"),
        ]

        return super(BibListesView, self).render(template, **kwargs)

    @expose("/import_cd_nom/", methods=("GET", "POST"))
    def import_cd_nom_view(self, *args, **kwargs):
        form = PopulateBibListesForm(request.form)

        if request.method == "POST":
            id_list = get_mdict_item_or_list(request.args, "id")
            delimiter = request.form.get("delimiter", default=",")
            with_header = request.form.get("with_header", default=False)
            file = request.files["upload"]

            try:
                populate_bib_liste(id_list, delimiter, with_header, file)
            except PopulateBibListeException as e:
                flash(e.message, "error")
                return self.render("admin/populate_biblist.html", form=form)

            return redirect(self.get_url(".index_view"))

        return self.render("admin/populate_biblist.html", form=form)


class InlineMediaForm(InlineFormAdmin):
    form_label = "Médias"

    form_extra_fields = {
        "chemin": form.ImageUploadField(
            label="Image",
            base_path=current_app.config["MEDIA_FOLDER"],
            url_relative_path="",
            namegen=taxref_media_file_name,
            thumbnail_size=(150, 150, True),
            endpoint="media",
        )
    }

    def __init__(self):
        return super(InlineMediaForm, self).__init__(TMedias)

    def on_model_change(self, form, model, is_created):
        """
        Check if chemin or url is set
        """
        if not model.chemin and not model.url:
            raise ValidationError(f"Média {model.titre} fichier ou url obligatoire")


class TaxrefView(
    FlaskAdminProtectedMixin,
    ModelView,
):
    can_create = False
    can_export = False
    can_delete = False
    can_view_details = True

    @property
    def can_edit(self):
        return self._can_action(2)

    inline_models = (InlineMediaForm(),)

    # Exclude all fields except listes
    form_excluded_columns = [c[0] for c in inspect(Taxref).attrs.items() if not c[0] == "liste"]

    column_list = (
        "cd_nom",
        "cd_ref",
        "regne",
        "group2_inpn",
        "nom_complet",
        "nom_valide",
        "nom_vern",
        "classe",
        "ordre",
        "famille",
        "liste",
        "nb_attributs",
        "nb_medias",
    )

    def _apply_search(self, query, count_query, joins, count_joins, search):
        """
        Apply search to the autocomplete query
        """
        query = query.filter(Taxref.cd_nom == int(search))
        count_query = count_query.filter(Taxref.cd_nom == int(search))
        return query, count_query, joins, count_joins

    column_searchable_list = ["nom_complet", "cd_nom"]

    column_filters = [
        TaxrefDistinctFilter(column=Taxref.regne, name="Règne"),
        TaxrefDistinctFilter(column=Taxref.group2_inpn, name="Group2 INPN"),
        TaxrefDistinctFilter(column=Taxref.classe, name="Classe"),
        FilterBiblist(
            column="liste",
            name="Est dans la liste",
        ),
        FilterTaxrefAttr(
            column="attributs",
            name="A l'attribut",
        ),
        FilterIsValidName(
            name="Nom valide / synonyme", options=[(1, "Nom valide"), (0, "Synonyme")]
        ),
        FilterMedia(
            name="Média", options=[(1, "Possède un média"), (0, "Ne possède pas de média")]
        ),
        FilterAttributes(
            name="Attributs",
            options=[(1, "Possède un attribut"), (0, "Ne possède pas d'attribut")],
        ),
    ]
    column_formatters = {c: macro("render_nom_ref") for c in column_list}

    column_auto_select_related = True
    column_hide_backrefs = False

    list_template = "admin/list_taxref.html"
    edit_template = "admin/edit_taxref.html"
    details_template = "admin/details_taxref.html"

    def _get_theme_attributes(self, taxon):
        return (
            db.session.query(BibThemes)
            .filter(or_(BibAttributs.v_regne == taxon.regne, BibAttributs.v_regne == None))
            .filter(
                or_(
                    BibAttributs.v_group2_inpn == taxon.group2_inpn,
                    BibAttributs.v_group2_inpn == None,
                )
            )
            .order_by(BibAttributs.ordre)
            .all()
        )

    def get_query(self):
        return self.session.query(self.model).options(
            undefer("nb_attributs"), undefer("nb_medias")
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

    def render(self, template, **kwargs):
        if template == "admin/list_taxref.html":
            self.extra_js = [
                url_for("configs.get_config"),
                url_for(".static", filename="js/taxref_autocomplete.js"),
            ]

        return super(TaxrefView, self).render(template, **kwargs)

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
                if request.form.getlist(f) and f.startswith("attr."):
                    id_attr = f.split(".")[1]
                    value = "&".join(request.form.getlist(f))
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


class TMediasView(FlaskAdminProtectedMixin, ModelView):
    can_create = False

    @property
    def can_edit(self):
        return self._can_action(2)

    @property
    def can_delete(self):
        return self._can_action(2)

    form_ajax_refs = {"taxon": TaxrefAjaxModelLoader("taxon")}

    form_extra_fields = {
        "chemin": form.ImageUploadField(
            label="Image",
            base_path=current_app.config["MEDIA_FOLDER"],
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

    def on_model_change(self, form, model, is_created):
        """
        Check if chemin or url is set
        """
        if not model.chemin and not model.url:
            raise ValidationError(f"Média {model.titre} fichier ou url obligatoire")


class TaxrefDistinctAjaxModelLoader(AjaxModelLoader):
    def __init__(self, name, **options):
        super(TaxrefDistinctAjaxModelLoader, self).__init__(name, options)

    def format(self, model):
        if model:
            return model[0]
        return None

    def get_one(self, pk):
        return Taxref.query.with_entities(Taxref.regne).filter(Taxref.regne == pk).distinct().one()

    def get_list(self, query, offset=0, limit=DEFAULT_PAGE_SIZE):
        return Taxref.query.with_entities(Taxref.regne).distinct().all()


class BibAttributsView(FlaskAdminProtectedMixin, ModelView):
    @property
    def can_create(self):
        return self._can_action(6)

    @property
    def can_edit(self):
        return self._can_action(6)

    @property
    def can_delete(self):
        return self._can_action(6)

    column_hide_backrefs = False

    form_columns = (
        "nom_attribut",
        "label_attribut",
        "liste_valeur_attribut",
        "obligatoire",
        "desc_attribut",
        "type_attribut",
        "type_widget",
        "ordre",
        "theme",
        "regne",
        "group2_inpn",
    )

    def render(self, template, **kwargs):
        self.extra_js = [
            url_for("configs.get_config"),
            url_for(".static", filename="js/regne_group2_inpn.js"),
        ]

        return super(BibAttributsView, self).render(template, **kwargs)

    def on_model_change(self, form, model, is_created):
        """
        Force None on empty string regne
        """
        if model.regne and not model.regne.regne:
            model.regne = None

    form_choices = {
        "type_attribut": [
            ("int", "int"),
            ("varchar(250)", "varchar(250)"),
            ("json", "json"),
            ("text ", "text "),
        ],
        "type_widget": [
            ("select", "select"),
            ("multiselect", "multiselect"),
            ("radio", "radio"),
            ("textarea", "textarea"),
            ("text", "text"),
            ("phenology", "phenology"),
        ],
    }

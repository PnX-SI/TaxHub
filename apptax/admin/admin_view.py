import os
import csv

from flask import (
    request,
    json,
    url_for,
    current_app,
    redirect,
    flash,
    g,
    has_app_context,
)
from flask_admin.model.template import macro
from jinja2.utils import markupsafe

from werkzeug.exceptions import Unauthorized

from flask_admin import form, BaseView
from flask_admin.contrib.sqla import ModelView
from flask_admin.model.form import InlineFormAdmin
from flask_admin.model.ajax import AjaxModelLoader, DEFAULT_PAGE_SIZE


from flask_admin.base import expose
from flask_admin.model.helpers import get_mdict_item_or_list

from flask_admin.form.upload import FileUploadField
from flask_admin.form.fields import Select2Field, JSONField

from flask_admin.model.template import EndpointLinkRowAction
from flask_admin.contrib.sqla.filters import BaseSQLAFilter

from sqlalchemy import or_
from wtforms import Form, BooleanField, SelectField, PasswordField, SubmitField, StringField

from wtforms.validators import DataRequired, Email, EqualTo, Length

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
from apptax.admin.utils import taxref_media_file_name, get_user_permission


class FlaskAdminProtectedMixin:
    # Define permission level for extra actions
    # Dict : {
    #       ".action_endpoint" : level
    #   }
    extra_actions_perm = None

    def _can_action(self, level):
        if not g.current_user:
            return False
        user_perm = get_user_permission(current_app.config["ID_APP"], g.current_user.id_role)
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
    def can_create(self):
        return self._can_action(3)

    @property
    def can_edit(self):
        return self._can_action(3)

    @property
    def can_delete(self):
        return self._can_action(4)

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
        self.extra_js = [url_for("configs.get_config"), url_for("static", filename="js/login.js")]
        self._template_args["RETURN_URL"] = get_mdict_item_or_list(request.args, "redirect")
        return super(LoginView, self).render(template, **kwargs)


class PopulateBibListesForm(Form):
    delimiter = SelectField(label="Delimiter", choices=[(",", ","), (";", ";")])
    with_header = BooleanField(label="With header")
    upload = FileUploadField("File")


class BibListesView(FlaskAdminProtectedMixin, ModelView):
    extra_actions_perm = {".import_cd_nom_view": 5}

    can_view_details = True

    column_list = ("regne", "group2_inpn", "picto", "code_liste", "nom_liste", "name_count")

    column_labels = dict(name_count="Nb taxons")

    form_excluded_columns = ("cnl", "noms")

    column_extra_row_actions = [
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
                filename=f"images/pictos/{model.picto}",
                _external=True,
            )
        elif model.url:
            path = model.url

        if not path:
            return
        return markupsafe.Markup(f"<img src='{path}'>")

    column_formatters = {"picto": _list_picto}

    def render(self, template, **kwargs):
        self.extra_js = [
            url_for("configs.get_config"),
            url_for("static", filename="js/regne_group2_inpn.js"),
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

            fstring = file.read().decode()
            inputcsv = csv.reader(fstring.splitlines(), delimiter=delimiter)

            bibliste = BibListes.query.get(id_list)
            # if header skip first line
            if with_header:
                next(inputcsv, None)
            for row in inputcsv:
                try:
                    cd_nom = int(row[0])
                except (TypeError, ValueError):
                    flash(f"Invalid cd_nom value: {row[0]}")
                    return self.render("admin/populate_biblist.html", form=form)
                tax = Taxref.query.get(cd_nom)
                if tax:
                    tax.liste.append(bibliste)

            db.session.commit()
            return redirect(self.get_url(".index_view"))

        return self.render("admin/populate_biblist.html", form=form)


class FilterTaxrefAttr(BaseSQLAFilter):
    def apply(self, query, value, alias=None):
        if not has_app_context():
            return ()
        return query.join(CorTaxonAttribut).filter(CorTaxonAttribut.id_attribut == value)

    def operation(self):
        return "equals"

    def get_options(self, view):
        if not has_app_context():
            return ()
        return [(attr.id_attribut, attr.label_attribut) for attr in BibAttributs.query.all()]


class FilterBibList(BaseSQLAFilter):
    def apply(self, query, value, alias=None):
        if not has_app_context():
            return ()
        return query.join(CorNomListe).join(BibListes).filter(BibListes.id_liste == value)

    def operation(self):
        return "equals"

    def get_options(self, view):
        if not has_app_context():
            return ()
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


class TaxrefView(
    FlaskAdminProtectedMixin,
    ModelView,
):
    can_create = False
    can_export = False
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
    )

    column_searchable_list = ["nom_complet", "cd_nom"]

    column_filters = [
        "regne",
        "group2_inpn",
        "classe",
        "ordre",
        "famille",
        FilterBibList(
            column="liste",
            name="Est dans la liste",
        ),
        FilterTaxrefAttr(
            column="attributs",
            name="A l'attribut",
        ),
    ]
    column_formatters = {c: macro("render_nom_ref") for c in column_list}

    column_auto_select_related = True
    column_hide_backrefs = False

    list_template = "admin/list_taxref.html"
    edit_template = "admin/edit_taxref.html"
    details_template = "admin/details_taxref.html"

    def _get_theme_attributes(self, taxon_name):
        return (
            db.session.query(BibThemes)
            .filter(or_(BibAttributs.v_regne == taxon_name.regne, BibAttributs.v_regne == None))
            .filter(
                or_(
                    BibAttributs.v_group2_inpn == taxon_name.group2_inpn,
                    BibAttributs.v_group2_inpn == None,
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

    def render(self, template, **kwargs):
        if template == "admin/list_taxref.html":
            self.extra_js = [
                url_for("configs.get_config"),
                url_for("static", filename="js/taxref_autocomplete.js"),
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
        print(theme_attributs_def)
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
            url_for("static", filename="js/regne_group2_inpn.js"),
        ]

        return super(BibAttributsView, self).render(template, **kwargs)

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

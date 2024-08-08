import logging

from pathlib import Path

from flask import request, json, url_for, redirect, flash, g, current_app
from flask_admin.model.template import macro
from jinja2.utils import markupsafe


from flask_admin import BaseView
from .forms import ImageUploadFieldWithoutDelete, TAdditionalAttributForm
from flask_admin.contrib.sqla import ModelView
from flask_admin.model.form import InlineFormAdmin
from flask_admin.model.ajax import AjaxModelLoader, DEFAULT_PAGE_SIZE
from flask_admin.contrib.sqla.filters import FilterEqual
from flask_admin.form.widgets import Select2Widget
from flask_admin.contrib.sqla.fields import QuerySelectField

from flask_admin.base import expose
from flask_admin.model.helpers import get_mdict_item_or_list

from flask_admin.form.upload import FileUploadField

from flask_admin.model.template import EndpointLinkRowAction, TemplateLinkRowAction
from flask_admin.model.template import EndpointLinkRowAction, TemplateLinkRowAction

from sqlalchemy import or_, inspect, select, exists

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
    BibListes,
    cor_nom_liste,
)
from apptax.admin.utils import taxref_media_file_name, get_user_permission
from pypnusershub.utils import get_current_app_id
from apptax.admin.admin import adresses
from apptax.taxonomie.filemanager import FILEMANAGER
from apptax.admin.utils import PopulateBibListeException, populate_bib_liste
from apptax.admin.filters import (
    TaxrefDistinctFilter,
    FilterTaxrefAttr,
    FilterBiblist,
    FilterIsValidName,
    FilterMedia,
    FilterAttributes,
)
from apptax.admin.mixins import RegneAndGroupFormMixin

log = logging.getLogger(__name__)


class FlaskAdminProtectedMixin:
    # Define permission level for extra actions
    # Dict : {
    #       ".action_endpoint" : level
    #   }
    extra_actions_perm = None

    def _can_action(self, level):
        if not g.current_user:
            return False
        if not g.current_user.is_authenticated:
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
                if (
                    getattr(extra_action, "endpoint", None)
                    or getattr(extra_action, "template", None)
                ) == extra_action_name and not self._can_action(extra_action_level):
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
        self.extra_js = [url_for(".static", filename="js/login.js")]
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
    form_excluded_columns = ["attributs"]


class BibListesView(FlaskAdminProtectedMixin, RegneAndGroupFormMixin, ModelView):
    @property
    def can_create(self):
        return self._can_action(6)

    @property
    def can_edit(self):
        return self._can_action(6)

    @property
    def can_delete(self):
        return self._can_action(6)

    extra_actions_perm = {".import_cd_nom_view": 6}
    list_template = "admin/list_biblist.html"
    extra_actions_perm = {".import_cd_nom_view": 6, "custom_row_actions.truncate_bib_liste": 6}

    can_view_details = True

    column_list = ("regne", "group2_inpn", "code_liste", "nom_liste", "nb_taxons")

    column_labels = dict(nb_taxons="Nb taxons")

    form_excluded_columns = "noms"

    column_extra_row_actions = [
        EndpointLinkRowAction("fa fa-download", ".import_cd_nom_view", "Peupler liste"),
        TemplateLinkRowAction("custom_row_actions.truncate_bib_liste", "Effacer cd_nom liste"),
    ]

    form_columns = ["code_liste", "nom_liste", "desc_liste", "regne", "group2_inpn"]

    create_template = "admin/edit_bib_list.html"

    def render(self, template, **kwargs):
        self.extra_js = [
            url_for(".static", filename="js/regne_group2_inpn.js"),
        ]

        return super(BibListesView, self).render(template, **kwargs)

    def delete_model(self, model):
        """
        Delete model test if cd_nom in list
        """
        exist = db.session.scalar(
            exists(cor_nom_liste).where(cor_nom_liste.c.id_liste == model.id_liste).select()
        )
        if exist:
            flash(
                f"Impossible de supprimer la liste  {model.nom_liste} car il y a des noms associés",
                "error",
            )
            return False
        else:
            super().delete_model(model)

    @expose("/truncate_bib_liste", methods=("POST",))
    def truncate_bib_liste(self):
        """
        Suppression des cd_noms contenus dans la liste
        """
        try:
            id = request.form.get("id")
            liste = db.session.get(BibListes, id)
            if liste.noms:
                liste.noms = []
            db.session.add(liste)
            db.session.commit()
            flash("Liste purgée de ses noms")
            return redirect(self.get_url(".index_view"))
        except Exception as ex:
            log.error(str(ex))
            flash("Erreur, liste non purgée", "error")
            return redirect(self.get_url(".index_view"))

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

        return self.render(
            "admin/populate_biblist.html", form=form, return_url=self.get_url(".index_view")
        )


class InlineMediaForm(InlineFormAdmin):
    form_label = "Médias"
    form_extra_fields = {
        "chemin": ImageUploadFieldWithoutDelete(
            label="Image",
            namegen=taxref_media_file_name,
            endpoint="media_taxhub",
            base_path=Path(current_app.config["MEDIA_FOLDER"], "taxhub").absolute(),
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
    form_excluded_columns = [c[0] for c in inspect(Taxref).attrs.items() if not c[0] == "listes"]

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
        "listes",
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

    # ATTENTION : les tests se basent sur les indices
    # de ce tableau. Rajouter des filtres à la fin, ou changer les
    # indice des filtres dans les tests (fonction `get_list`)
    column_filters = [
        FilterEqual(Taxref.cd_nom, name="cd_nom"),
        FilterEqual(Taxref.cd_ref, name="cd_ref"),
        TaxrefDistinctFilter(column=Taxref.regne, name="Règne"),
        TaxrefDistinctFilter(column=Taxref.group2_inpn, name="Group2 INPN"),
        TaxrefDistinctFilter(column=Taxref.classe, name="Classe"),
        FilterBiblist(
            column="listes",
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
            .filter(or_(BibAttributs.regne == taxon.regne, BibAttributs.regne == None))
            .filter(
                or_(
                    BibAttributs.group2_inpn == taxon.group2_inpn,
                    BibAttributs.group2_inpn == None,
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
                url_for(".static", filename="js/taxref_autocomplete.js"),
            ]

        return super(TaxrefView, self).render(template, **kwargs)

    @expose("/details/", methods=("GET",))
    def details_view(self):
        id = get_mdict_item_or_list(request.args, "id")
        taxon_name = db.session.query(Taxref).get(id)
        if not taxon_name.cd_nom == taxon_name.cd_ref:
            taxon_valid = db.session.query(Taxref).get(taxon_name.cd_ref)
        else:
            taxon_valid = taxon_name

        # Get attributes
        theme_attributs_def = self._get_theme_attributes(taxon_valid)
        attributes_val = self._get_attributes_value(taxon_valid, theme_attributs_def)
        self._template_args["theme_attributs_def"] = theme_attributs_def
        self._template_args["attributes_val"] = attributes_val

        # Get media
        self._template_args["medias"] = taxon_valid.medias
        return super(TaxrefView, self).details_view()

    @expose("/edit/", methods=("GET", "POST"))
    def edit_view(self):
        # Get Taxon data
        id = get_mdict_item_or_list(request.args, "id")
        taxon_name = db.session.query(Taxref).get(id)

        # Get attributes only if cd_nom is cd_ref
        if taxon_name.cd_nom == taxon_name.cd_ref:
            theme_attributs_def = self._get_theme_attributes(taxon_name)
            attributes_val = self._get_attributes_value(taxon_name, theme_attributs_def)
            self._template_args["theme_attributs_def"] = theme_attributs_def
            self._template_args["attributes_val"] = attributes_val
            if request.method == "POST":
                for f in request.form:
                    if request.form.getlist(f) and f.startswith("attr."):
                        id_attr = f.split(".")[1]
                        value = "&".join(request.form.getlist(f))
                        query = (
                            db.select(CorTaxonAttribut)
                            .filter_by(cd_ref=taxon_name.cd_ref)
                            .filter_by(id_attribut=id_attr)
                        )
                        model = db.session.scalars(query).one_or_none()
                        if model:
                            if value == "":
                                db.session.delete(model)
                            else:
                                model.valeur_attribut = value
                                db.session.add(model)
                        elif value != "":
                            model = CorTaxonAttribut(
                                cd_ref=taxon_name.cd_ref,
                                id_attribut=id_attr,
                                valeur_attribut=value,
                            )
                            db.session.add(model)
                        db.session.commit()
        self._template_args["url_cancel"] = request.referrer or url_for("taxons.index_view")

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

    column_exclude_list = ("url",)
    form_extra_fields = {
        "chemin": ImageUploadFieldWithoutDelete(
            label="Image",
            base_path=Path(current_app.config["MEDIA_FOLDER"], "taxhub").absolute(),
            namegen=taxref_media_file_name,
            thumbnail_size=(150, 150, True),
            endpoint="media_taxhub",
        )
    }

    def _list_titre(view, context, model, name):
        return markupsafe.Markup(model.titre)

    def _list_thumbnail(view, context, model, name):
        # format html
        html = ""
        if model.types.nom_type_media in ("Photo", "Photo_principale"):
            html = f"""
            <a target='_blank' href='{ url_for("t_media.getThumbnail_tmedias", id_media=model.id_media)}'>
                <img width="100" src='{ url_for("t_media.getThumbnail_tmedias", id_media=model.id_media)}'  alt="Taxon image">
            </a>
            """
        elif model.types.nom_type_media in ("Audio"):
            html = f"<audio controls src='{model.media_url}'>"
        else:
            html = f"<a  target='_blank' href='{model.media_url}'>Lien média</a>"

        return markupsafe.Markup(html)

    column_formatters = {"chemin": _list_thumbnail, "titre": _list_titre}

    def on_model_change(self, form, model, is_created):
        """
        Check if chemin or url is set
        """
        if not model.chemin and not model.url:
            raise ValidationError(f"Média {model.titre} fichier ou url obligatoire")
        FILEMANAGER.create_thumb(model, (300, 400), regenerate=True)


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


class BibAttributsView(FlaskAdminProtectedMixin, RegneAndGroupFormMixin, ModelView):

    form_base_class = TAdditionalAttributForm

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

    column_labels = {
        "desc_attribut": "Description",
        "regne": "Règne",
        "group2_inpn": "Group2 INPN",
        "theme": "Théme",
        "liste_valeur_attribut": "Valeurs disponibles",
    }

    column_descriptions = {
        "liste_valeur_attribut": """Doit suivre le format suivant: {"values":[valeur1, valeur2, valeur3]}"""
    }

    def liste_valeur_attribut_formater(v, c, m, p):
        if m.liste_valeur_attribut:
            data = json.loads(m.liste_valeur_attribut)
            if "values" in data:
                return ", ".join(data["values"])
        return ""

    column_formatters = {
        "liste_valeur_attribut": liste_valeur_attribut_formater,
    }
    create_template = "admin/edit_attr.html"

    def render(self, template, **kwargs):
        self.extra_js = [
            url_for(".static", filename="js/regne_group2_inpn.js"),
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
        ],
    }

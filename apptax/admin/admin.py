import os

from flask import redirect, url_for, Blueprint
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from werkzeug.exceptions import Unauthorized

from apptax.database import db
from apptax.taxonomie.models import Taxref, BibListes, TMedias, BibAttributs, BibThemes


# Create blueprint for template and static
adresses = Blueprint("apptax-admin", __name__, template_folder="templates")
adresses.static_folder = os.path.join(adresses.root_path, "static")


class TaxhubView(AdminIndexView):
    def is_visible(self):
        # This view won't appear in the menu structure
        return False

    @expose("/")
    def index(self):
        return redirect(url_for("taxons.index_view"))


taxhub_admin = Admin(
    template_mode="bootstrap4", name="Administration Taxhub", index_view=TaxhubView()
)


def taxhub_admin_addview(app, admin, category=None):
    with app.app_context():
        from apptax.admin.admin_view import (
            TaxrefView,
            BibListesView,
            TMediasView,
            BibAttributsView,
            LoginView,
            FlaskAdminProtectedMixin,
        )

        class BibThemesView(
            FlaskAdminProtectedMixin,
            ModelView,
        ):
            extra_actions_perm = None

        static_folder = os.path.join(adresses.root_path, "static")
        admin.add_view(
            LoginView(
                name="Login", endpoint="loginview", category=category, static_folder=static_folder
            )
        )
        admin.add_view(
            TaxrefView(
                Taxref,
                db.session,
                name="Taxref",
                endpoint="taxons",
                category=category,
                static_folder=static_folder,
            )
        )
        admin.add_view(
            BibListesView(
                BibListes,
                db.session,
                name="Listes",
                category=category,
                static_folder=static_folder,
            )
        )
        admin.add_view(
            TMediasView(
                TMedias, db.session, name="Médias", category=category, static_folder=static_folder
            )
        )
        admin.add_view(
            BibAttributsView(
                BibAttributs,
                db.session,
                name="Attributs",
                category=category,
                static_folder=static_folder,
            )
        )
        admin.add_view(
            BibThemesView(
                BibThemes,
                db.session,
                name="Thèmes",
                category=category,
                static_folder=static_folder,
            )
        )

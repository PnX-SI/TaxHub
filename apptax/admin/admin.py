from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView

from apptax.database import db
from apptax.taxonomie.models import Taxref, BibListes, TMedias, BibAttributs

taxhub_admin = Admin(
    template_mode="bootstrap3",
    name="Administration Taxhub",
)


def taxhub_admin_addview(app, admin):

    with app.app_context():

        from apptax.admin.admin_view import TaxrefView, BibListesView, TMediasView

        admin.add_view(TaxrefView(Taxref, db.session, endpoint="taxons"))
        admin.add_view(BibListesView(BibListes, db.session))
        admin.add_view(ModelView(BibAttributs, db.session))
        admin.add_view(TMediasView(TMedias, db.session))

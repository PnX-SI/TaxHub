import pytest

from flask import url_for, current_app, jsonify
from schema import Schema, Optional, Or

from apptax.database import db

from pypnusershub.db.models import (
    User,
    Organisme,
    Application,
    Profils,
    UserApplicationRight,
    AppUser,
)
from apptax.taxonomie.models import BibNoms

from pypnusershub.tests.utils import set_logged_user_cookie
from .fixtures import noms_without_listexample


@pytest.fixture
def user():
    a = Application.query.filter_by(code_application=current_app.config["CODE_APPLICATION"]).one()
    p = (
        Profils.query.filter(Profils.applications.contains(a))
        .filter(Profils.id_profil >= 4)  # level >= 2
        .first()
    )
    with db.session.begin_nested():
        o = Organisme(nom_organisme="Organisme")
        db.session.add(o)
        u = User(groupe=False, active=True, identifiant="taxhubadmin", organisme=o)
        db.session.add(u)
    with db.session.begin_nested():
        uar = UserApplicationRight(role=u, profil=p, application=a)
        db.session.add(uar)
    return u


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestAPITaxhub:
    def test_post_addnoms_routes(self, user, noms_without_listexample):
        set_logged_user_cookie(self.client, user)
        noms = BibNoms.query.all()
        ids = [n.id_nom for n in noms]
        response = self.client.post(
            url_for("bib_listes.add_cornomliste", idliste="100"),
            json=ids,
        )
        assert response.status_code == 200
        data = response.json
        assert ids == data

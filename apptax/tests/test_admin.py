import json
import os

import pytest
from flask import url_for, current_app

from apptax.database import db

from apptax.taxonomie.models import BibListes, BibAttributs, Taxref, BibAttributs
from pypnusershub.tests.utils import set_logged_user_cookie

from .fixtures import noms_example, users, attribut_example

form_bibliste = {
    "regne": "Animalia",
    "group2_inpn": "Autres",
    "nom_liste": "test",
    "code_liste": "test code",
    "desc_liste": "test desc",
}

form_attributs = {
    "nom_attribut": "test_attr",
    "label_attribut": "Attribut test",
    "desc_attribut": "Description attribut test",
    "type_attribut": "varchar(250)",
    "liste_valeur_attribut": "{'values':['val1','val2','val3']}",
    "type_widget": "select",
    "ordre": 1,
    "theme": 1,
    "regne": None,
    "group2_inpn": None,
}


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestAdminView:
    def test_insert_bibliste(self, users):
        set_logged_user_cookie(self.client, users["admin"])
        req = self.client.post(
            "admin/biblistes/new/?url=/admin/biblistes/",
            data=form_bibliste,
            content_type="multipart/form-data",
        )
        assert req.status_code == 302

        assert db.session.query(
            db.session.query(BibListes).filter_by(nom_liste="test").exists()
        ).scalar()

    def test_insert_attr(self, users):
        set_logged_user_cookie(self.client, users["admin"])
        req = self.client.post(
            "admin/bibattributs/new/?url=/admin/bibattributs/",
            data=form_attributs,
            content_type="multipart/form-data",
        )
        assert req.status_code == 302

        assert db.session.query(
            db.session.query(BibAttributs).filter_by(nom_attribut="test_attr").exists()
        ).scalar()

    def test_insert_taxref(self, users, attribut_example):
        set_logged_user_cookie(self.client, users["admin"])

        attr_key = f"attr.{attribut_example.id_attribut}"

        with open(os.path.join("apptax/tests", "coccinelle.jpg"), "rb") as f:
            form_taxref = {
                attr_key: "val1",
                "liste": 100,
                "medias-0-types": 1,
                "medias-0-titre": "test",
                "medias-0-auteur": "test",
                "medias-0-desc_media": "test",
                "medias-0-source": "test",
                "medias-0-is_public": "test",
                "medias-0-chemin": (f, "coccinelle.jpg"),
            }
            req = self.client.post(
                "admin/taxons/edit/?id=117526&url=/admin/taxons/",
                data=form_taxref,
                content_type="multipart/form-data",
            )

        assert req.status_code == 302

        tax = db.session.query(Taxref).filter_by(cd_nom=117526).scalar()

        assert tax.attributs[0].valeur_attribut == form_taxref[attr_key]
        assert tax.liste[0].id_liste == form_taxref["liste"]
        assert tax.medias[0].chemin == "117526_coccinelle.jpg"

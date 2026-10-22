import pytest
from flask import url_for
from sqlalchemy import select

from apptax.database import db
from apptax.taxonomie.models import BibAttributs

from apptax.tests.fixtures import attribut_example


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestApiBibAttributs:
    def test_get_bibattributs(self, attribut_example):
        response = self.client.get(url_for("bib_attribut.get_bibattributs"))
        assert response.status_code == 200
        data = response.json
        print(data)
        assert {a["id_attribut"] for a in data} == set(
            db.session.scalars(select(BibAttributs.id_attribut))
        )
        assert attribut_example.id_attribut in {a["id_attribut"] for a in data}

    def test_get_bibattribut(self, attribut_example):
        response = self.client.get(
            url_for("bib_attribut.get_bibattributs", id=attribut_example.id_attribut)
        )
        assert response.status_code == 200
        data = response.json
        assert data["id_attribut"] == attribut_example.id_attribut
        assert data["nom_attribut"] == "migrateur"
        assert data["label_attribut"] == "Migrateur"
        assert data["type_widget"] == "select"
        assert data["regne"] == "Animalia"
        assert data["group2_inpn"] == "Oiseaux"
        assert data["id_theme"] == attribut_example.id_theme

    def test_get_bibattribut_unknown(self):
        unknown_id = (db.session.scalar(select(db.func.max(BibAttributs.id_attribut))) or 0) + 1
        response = self.client.get(url_for("bib_attribut.get_bibattributs", id=unknown_id))
        assert response.status_code == 404

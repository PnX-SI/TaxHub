import pytest

from flask import url_for

from .fixtures import *
from schema import Schema, Optional, Or


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestApiBibListe:
    schema_cor_nom_liste = Schema(
        {
            "items": [{"cd_nom": int, "id_liste": int}],
            "total": int,
            "limit": int,
            "page": int,
        }
    )

    def test_cor_nom_liste(self, noms_example):
        response = self.client.get(
            url_for("bib_listes.get_cor_nom_liste"),
        )
        assert response.status_code == 200
        data = response.json
        assert len(data["items"]) > 0
        self.schema_cor_nom_liste.validate(data)

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

    schema_allnamebyListe = Schema(
        [
            {
                "id_liste": int,
                "code_liste": str,
                "nom_liste": str,
                "desc_liste": str,
                "regne": Or(str, None),
                "group2_inpn": Or(str, None),
                "nb_taxons": int,
            }
        ]
    )

    def test_get_biblistes(self):
        query_string = {"limit": 10}
        response = self.client.get(
            url_for(
                "bib_listes.get_biblistes",
            ),
            query_string=query_string,
        )
        assert response.status_code == 200
        data = response.json
        print(data["data"])
        if data:
            assert self.schema_allnamebyListe.is_valid(data["data"])

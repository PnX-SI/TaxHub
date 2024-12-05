import pytest

from flask import url_for

from .fixtures import *
from schema import Schema, Optional, Or


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestApiBibListe:
    schema_allnamebyListe = Schema(
        [
            {
                "id_liste": int,
                "code_liste": str,
                "nom_liste": str,
                "desc_liste": Or(str, None),
                "regne": Or(str, None),
                "group2_inpn": Or(str, None),
                "nb_taxons": int,
            }
        ]
    )

    def test_get_biblistes(self, listes):
        query_string = {"limit": 10}
        response = self.client.get(
            url_for(
                "bib_listes.get_biblistes",
            ),
            query_string=query_string,
        )
        assert response.status_code == 200
        data = response.json
        if data:
            assert self.schema_allnamebyListe.is_valid(data["data"])

    def test_get_biblistesbyTaxref(self, listes):
        response = self.client.get(
            url_for("bib_listes.get_biblistesbyTaxref", regne="Animalia", group2_inpn=None),
        )
        # Filter test list only
        data = [d for d in response.json if d["desc_liste"] == "Liste description"]
        self.schema_allnamebyListe.validate(data)
        assert len(data) == 1

        response = self.client.get(
            url_for("bib_listes.get_biblistesbyTaxref", regne="Plantae", group2_inpn="Mousses"),
        )
        # Filter test list only
        data = [d for d in response.json if d["desc_liste"] == "Liste description"]
        self.schema_allnamebyListe.validate(data)
        assert len(data) == 1

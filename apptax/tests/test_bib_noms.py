import pytest
from flask import url_for

from .fixtures import noms_example, attribut_example, liste


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestAPIBibNoms:
    def test_getOne_bibtaxonsInfo(self, noms_example, attribut_example):
        resp = self.client.get(
            url_for(
                "bib_noms.getOne_bibtaxonsInfo",
                cd_nom=67111,
                id_attribut=attribut_example.id_attribut,
            )
        )
        assert resp.status_code == 200
        data = resp.json
        assert "attributs" in data
        attr = next(
            attr
            for attr in data["attributs"]
            if attr["id_attribut"] == attribut_example.id_attribut
        )
        assert attr["valeur_attribut"] == "migrateur"

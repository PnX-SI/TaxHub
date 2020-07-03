
import os
import tempfile

import pytest
from flask import url_for


import server

@pytest.mark.usefixtures('client_class')
class TestAPITaxref:


    def test_get_allnamebyListe_routes(self):

        query_string = {"limit": 500}
        response = self.client.get(
            url_for("taxref.get_AllTaxrefNameByListe", id_liste=100),
            query_string=query_string
        )
        assert response.status_code == 200


    def test_get_distinct_routes(self):
        response = self.client.get(
            url_for("taxref.getDistinctField", field="regne")
        )
        assert response.status_code == 200

    def test_get_hierarchy_routes(self):

        query_string = {"ilike": "pla"}
        response = self.client.get(
            url_for("taxref.getTaxrefHierarchie", rang="KD"),
            query_string=query_string
        )
        assert response.status_code == 200
        response = self.client.get(
            url_for("taxref.getTaxrefHierarchieBibNoms", rang="FM"),
            query_string=query_string
        )
        assert response.status_code == 200

        query_string = {"ilike": "pl", "regne": "Plantae"}
        response = self.client.get(
            url_for("taxref.getTaxrefHierarchie", rang="FM"),
            query_string=query_string
        )
        assert response.status_code == 200
        response = self.client.get(
            url_for("taxref.getTaxrefHierarchieBibNoms", rang="FM"),
            query_string=query_string
        )
        assert response.status_code == 200

        query_string = {"ilike": "pl", "regne": "Plantae"}

    def test_searchfield_routes(self):

        query_string = {"ilike": "pla"}
        response = self.client.get(
            url_for("taxref.getSearchInField", field="lb_nom", ilike="poa"),
            query_string=query_string
        )
        assert response.status_code == 200

    def test_taxrefDetail_routes(self):
        response = self.client.get(
            url_for("taxref.getTaxrefDetail", id=29708)
        )
        assert response.status_code == 200

    def test_searchTaxref_routes(self):
        query_string = {
            "ilike-classe": "hex",
            "page": 1,
            "limit": 10
        }
        response = self.client.get(
            url_for("taxref.getTaxrefList"),
            query_string=query_string
        )
        assert response.status_code == 200
        response = self.client.get(
            url_for("taxref.getTaxrefBibtaxonList"),
            query_string=query_string
        )
        assert response.status_code == 200

    def test_regneGroup2Inpn_routes(self):
        response = self.client.get(
            url_for("taxref.get_regneGroup2Inpn_taxref")
        )
        assert response.status_code == 200

    def test_bib_routes(self):
        response = self.client.get(
            url_for("taxref.get_bib_lr")
        )
        assert response.status_code == 200

        response = self.client.get(
            url_for("taxref.get_bib_hab")
        )
        assert response.status_code == 200

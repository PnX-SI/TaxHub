import pytest
import json

from flask import url_for
from schema import Schema, Optional, Or

from .fixtures import attribut_example, noms_example


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestAPITaxref:
    schema_allnamebyListe = Schema(
        [
            {
                "cd_nom": int,
                "cd_ref": int,
                "search_name": str,
                "gid": int,
                "nom_valide": str,
                "nom_vern": Or(None, str),
                "lb_nom": str,
                "regne": str,
                "group2_inpn": str,
                "group3_inpn": str,
            }
        ]
    )
    schema_names = Schema(
        [
            {
                "cd_nom": int,
                "id_statut": Or(None, str),
                "id_habitat": Or(None, int),
                "id_rang": str,
                "phylum": Or(None, str),
                "classe": Or(None, str),
                "regne": Or(None, str),
                "ordre": Or(None, str),
                "famille": Or(None, str),
                "sous_famille": Or(None, str),
                "tribu": Or(None, str),
                "cd_taxsup": Or(None, int),
                "cd_sup": Or(None, int),
                "cd_ref": int,
                "lb_nom": str,
                "lb_auteur": str,
                "nom_complet": str,
                "nom_complet_html": str,
                "nom_vern": Or(None, str),
                "nom_valide": str,
                "nom_vern_eng": Or(None, str),
                "group1_inpn": str,
                "group2_inpn": str,
                "group3_inpn": Or(None, str),
                "url": Or(None, str),
                "listes": [int],
                "id_nom": Or(None, int),
            }
        ]
    )
    schema_taxref_detail = Schema(
        {
            "cd_nom": int,
            "cd_ref": int,
            "cd_sup": int,
            "cd_taxsup": int,
            "phylum": str,
            "regne": str,
            Optional("classe"): str,
            "ordre": str,
            "famille": str,
            "group1_inpn": str,
            "group2_inpn": str,
            "group3_inpn": str,
            "id_rang": str,
            "nom_complet": str,
            "nom_habitat": str,
            "nom_rang": str,
            "nom_statut": str,
            "nom_valide": str,
            "nom_vern": str,
            "status": dict,
            "synonymes": [
                {
                    "cd_nom": int,
                    "nom_complet": str,
                }
            ],
        }
    )

    def test_get_allnamebyListe_routes(self):
        query_string = {"limit": 10}
        response = self.client.get(
            url_for("taxref.get_AllTaxrefNameByListe", id_liste=100), query_string=query_string
        )
        assert response.status_code == 200
        data = response.json
        if data:
            assert self.schema_allnamebyListe.is_valid(data)

    def test_get_allnamebyListe_routes_without_list(self):
        query_string = {
            "limit": 10,
            "search_name": "poa",
            "regne": "Plantae",
            "group2_inpn": "Angiospermes",
        }
        response = self.client.get(
            url_for("taxref.get_AllTaxrefNameByListe", id_liste=-1), query_string=query_string
        )
        assert response.status_code == 200
        data = response.json
        if data:
            assert self.schema_allnamebyListe.is_valid(data)

    def test_get_allnamebyListe_routes_with_code(self):
        query_string = {"limit": 10, "code_list": "100"}
        response = self.client.get(
            url_for("taxref.get_AllTaxrefNameByListe", id_liste=None), query_string=query_string
        )
        assert response.status_code == 200
        data = response.json
        if data:
            assert self.schema_allnamebyListe.is_valid(data)

    def test_get_allnamebyListe_routes_without_list_filter_group3(self):
        query_string = {
            "limit": 10,
            "search_name": "poa",
            "regne": "Plantae",
            "group2_inpn": "Angiospermes",
            "group3_inpn": "Autres",
        }
        response = self.client.get(
            url_for("taxref.get_AllTaxrefNameByListe", id_liste=-1), query_string=query_string
        )
        assert response.status_code == 200
        data = response.json
        if data:
            assert self.schema_allnamebyListe.is_valid(data)

    def test_getTaxrefList_routes(self):
        query_string = {"limit": 10}
        response = self.client.get(url_for("taxref.getTaxrefList"), query_string=query_string)
        assert response.status_code == 200
        data = response.json
        if data:
            assert self.schema_names.is_valid(data["items"])

    def test_getTaxrefList_routes_limit_fields(self):
        query_string = {"limit": 10, "fields": "cd_nom,cd_ref,listes"}
        response = self.client.get(url_for("taxref.getTaxrefList"), query_string=query_string)
        current_schema = Schema([{"cd_nom": int, "cd_ref": int, "listes": [int]}])
        assert response.status_code == 200
        data = response.json

        if data:
            assert current_schema.is_valid(data["items"])

    def test_getTaxrefList_routes_order_by(self):
        query_string = {"limit": 10, "orderby": "cd_nom"}
        response = self.client.get(url_for("taxref.getTaxrefList"), query_string=query_string)

        assert response.status_code == 200
        data = response.json

        if data:
            assert self.schema_names.is_valid(data["items"])

        query_string = {"limit": 10, "orderby": "unkwnow_field", "order": "asc"}
        response = self.client.get(url_for("taxref.getTaxrefList"), query_string=query_string)

        assert response.status_code == 200

    def test_getTaxrefList_routes_limit_filter_id_liste(self, noms_example):
        query_string = {"id_liste": 100, "fields": "cd_nom"}
        response = self.client.get(url_for("taxref.getTaxrefList"), query_string=query_string)
        current_schema = Schema([{"cd_nom": int}])
        assert response.status_code == 200
        data = response.json

        if data:
            assert current_schema.is_valid(data["items"])
            assert len(data["items"]) == 9

    def test_get_distinct_routes(self):
        response = self.client.get(url_for("taxref.getDistinctField", field="regne"))
        assert response.status_code == 200

    def test_get_hierarchy_routes(self):
        query_string = {"ilike": "pla"}
        response = self.client.get(
            url_for("taxref.getTaxrefHierarchie", rang="KD"), query_string=query_string
        )
        assert response.status_code == 200
        response = self.client.get(
            url_for("taxref.getTaxrefHierarchieBibNoms", rang="FM"), query_string=query_string
        )
        assert response.status_code == 200

        query_string = {"ilike": "pl", "regne": "Plantae"}
        response = self.client.get(
            url_for("taxref.getTaxrefHierarchie", rang="FM"), query_string=query_string
        )
        assert response.status_code == 200
        response = self.client.get(
            url_for("taxref.getTaxrefHierarchieBibNoms", rang="FM"), query_string=query_string
        )
        assert response.status_code == 200

        query_string = {"ilike": "pl", "regne": "Plantae"}

    def test_searchfield_routes(self):
        query_string = {"ilike": "pla"}
        response = self.client.get(
            url_for("taxref.getSearchInField", field="lb_nom", ilike="poa"),
            query_string=query_string,
        )
        assert response.status_code == 200

    def test_taxrefDetail_routes(self):
        response = self.client.get(url_for("taxref.getTaxrefDetail", id=29708))
        assert response.status_code == 200
        data = response.json
        if data:
            assert self.schema_taxref_detail.is_valid(data)

    def test_searchTaxref_routes(self):
        query_string = {"ilike-classe": "hex", "page": 1, "limit": 10}
        response = self.client.get(url_for("taxref.getTaxrefList"), query_string=query_string)
        assert response.status_code == 200
        response = self.client.get(
            url_for("taxref.getTaxrefBibtaxonList"), query_string=query_string
        )
        assert response.status_code == 200

    def test_regneGroup2Inpn_routes(self):
        response = self.client.get(url_for("taxref.get_regneGroup2Inpn_taxref"))
        assert response.status_code == 200

    def test_bib_routes(self):
        response = self.client.get(url_for("taxref.get_bib_hab"))
        assert response.status_code == 200

    def test_taxrefversion_routes(self):
        response = self.client.get(url_for("taxref.getTaxrefVersion"))
        assert response.status_code == 200
        assert json.loads(response.data)["version"] == 16

    def test_get_groupe3_inpn(self):
        response = self.client.get(url_for("taxref.get_group3_inpn_taxref"))

        assert response.status_code == 200
        response_json = response.json
        assert "Coléoptères" in response_json
        assert "Autres" in response_json

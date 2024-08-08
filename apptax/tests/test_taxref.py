import pytest
import json

from flask import url_for
from schema import Schema, Optional, Or

from .fixtures import liste, liste_with_names, noms_without_listexample


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
    taxref_schema = Schema(
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

    schema_response = Schema(
        {"items": list, "limit": int, "page": int, "total": int, "total_filtered": int}
    )

    def test_get_allnamebyListe_routes(self, liste):
        response = self.client.get(
            url_for("taxref.get_AllTaxrefNameByListe", code_liste=liste.code_liste, limit=10),
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

    def test_regneGroup2Inpn_routes(self):
        response = self.client.get(url_for("taxref.get_regneGroup2Inpn_taxref"))
        assert response.status_code == 200

    def test_bib_routes(self):
        response = self.client.get(url_for("taxref.get_bib_hab"))
        assert response.status_code == 200

    def test_taxrefversion_routes(self):
        response = self.client.get(url_for("taxref.getTaxrefVersion"))
        assert response.status_code == 200
        assert (
            json.loads(response.data)["version"] == 17
        )  # FIXME: Comment faire si quelqu'un a besoin de taxref dans une différente version...

    def test_get_groupe3_inpn(self):
        response = self.client.get(url_for("taxref.get_group3_inpn_taxref"))

        assert response.status_code == 200
        response_json = response.json
        assert "Coléoptères" in response_json
        assert "Autres" in response_json

    def test_get_taxref_list(self, liste_with_names):
        response = self.client.get(url_for("taxref.get_taxref_list"))
        assert response.status_code == 200
        response_json = response.json
        assert len(response_json["items"]) == 20
        # filtre par id_list
        response = self.client.get(
            url_for("taxref.get_taxref_list"),
            query_string={"id_liste": f"{liste_with_names.id_liste}, 150", "limit": 500},
        )
        assert response.status_code == 200
        response_json = response.json
        assert self.schema_response.is_valid(response_json)
        assert self.taxref_schema.is_valid(response_json["items"])
        # marche tant que la liste liste_with_names n'est pas superieur à la limite !
        assert len(response_json["items"]) == len(liste_with_names.noms)

        # filtre par id_list -1 + par "liste_with_names" -> doit retourner tout taxref
        limit = 500
        response = self.client.get(
            url_for("taxref.get_taxref_list"),
            query_string={"id_liste": f"{liste_with_names.id_liste},-1", "limit": limit},
        )
        assert response.status_code == 200
        response_json = response.json
        assert len(response_json["items"]) == limit

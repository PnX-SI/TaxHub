import pytest
import json
import io
import os
from flask import url_for
from .utils import json_of_response
from schema import Schema, Optional, Or


@pytest.mark.usefixtures("client_class")
class TestAPIMedia:
    def test_get_tmediasbyTaxon(self):
        response = self.client.get(url_for("t_media.get_tmediasbyTaxon", cdref=67111))
        assert response.status_code == 200
        # data = json_of_response(response)
        # print(data)

    def test_get_tmedias(self):
        response = self.client.get(url_for("t_media.get_tmedias"))
        assert response.status_code == 200
        response = self.client.get(url_for("t_media.get_tmedias", id=1))
        assert response.status_code == 200

    def test_insert_tmedias_url(self):
        # LOGIN
        response = self.client.post(
            url_for("auth.login"),
            data=json.dumps(
                {"login": "admin", "password": "admin", "id_application": 2},
            ),
            headers={"Content-Type": "application/json"},
        )

        data = {
            "is_public": True,
            "auteur": "Luc Viatour",
            "url": "https://upload.wikimedia.org/wikipedia/commons/7/77/Coccinella_septempunctata_Luc_Viatour.JPG",
            "id_type": 2,
            "nom_type_media": "Photo",
            "titre": "Coccinelle test url",
            "desc_media": "CC",
            "cd_ref": 11165,
            "isFile": False,
        }
        response = self.client.post(
            url_for("t_media.insertUpdate_tmedias"),
            data=json.dumps(data),
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 200

    def test_insert_tmedias_file(self):
        response = self.client.post(
            url_for("auth.login"),
            data=json.dumps(
                {"login": "admin", "password": "admin", "id_application": 2},
            ),
            headers={"Content-Type": "application/json"},
        )
        # Test send file
        file = os.path.join("coccinelle.jpg")
        data = {
            "is_public": True,
            "auteur": "???",
            "id_type": 2,
            "nom_type_media": "Photo",
            "titre": "Coccinelle test fichier",
            "desc_media": "CC",
            "cd_ref": 11165,
            "isFile": True,
        }
        data["file"] = (file, "coccinelle.jpg")
        print(data)
        response = self.client.post(
            url_for("t_media.insertUpdate_tmedias"),
            data=data,
            content_type="multipart/form-data",
        )

        assert response.status_code == 200

import pytest
import json
import os
from flask import url_for
from .conftest import login

@pytest.mark.usefixtures("client_class")
class TestAPIMedia:
    def test_get_tmediasbyTaxon(self):
        response = self.client.get(url_for("t_media.get_tmediasbyTaxon", cdref=67111))
        assert response.status_code == 200

    def test_get_tmedias(self):
        response = self.client.get(url_for("t_media.get_tmedias"))
        assert response.status_code == 200
        response = self.client.get(url_for("t_media.get_tmedias", id=1))
        assert response.status_code == 200

    def test_insert_tmedias_url(self):
        # LOGIN
        login(self.client)

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

        id_media = json.loads(response.data)["id_media"]
        self.get_thumbnail(id_media)

    def test_insert_tmedias_file(self):
        # LOGIN
        login(self.client)
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

        response = self.client.post(
            url_for("t_media.insertUpdate_tmedias"),
            data=data,
            content_type="multipart/form-data",
        )

        assert response.status_code == 200

        id_media = json.loads(response.data)["id_media"]
        self.get_thumbnail(id_media)

    def get_thumbnail(self, id_media):

        response = self.client.get(
            url_for("t_media.getThumbnail_tmedias", id_media=id_media),

        )
        assert response.status_code == 200

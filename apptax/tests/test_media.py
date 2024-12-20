import json
import os

from apptax.taxonomie.models import BibTypesMedia, TMedias
import pytest
from flask import url_for, current_app, Response

from apptax.database import db

from pypnusershub.db.models import (
    User,
    Organisme,
    Application,
    Profils,
    UserApplicationRight,
    AppUser,
)
from pypnusershub.tests.utils import set_logged_user_cookie
from schema import Schema, Optional, Or

from .fixtures import noms_example, attribut_example, liste


@pytest.fixture
def user():
    a = Application.query.filter_by(code_application=current_app.config["CODE_APPLICATION"]).one()
    p = (
        Profils.query.filter(Profils.applications.contains(a))
        .filter(Profils.id_profil >= 2)  # level >= 2
        .first()
    )
    with db.session.begin_nested():
        o = Organisme(nom_organisme="Organisme")
        db.session.add(o)
        u = User(groupe=False, active=True, identifiant="taxhubadmin", organisme=o)
        db.session.add(u)
    with db.session.begin_nested():
        uar = UserApplicationRight(role=u, profil=p, application=a)
        db.session.add(uar)
    return u


@pytest.fixture
def media():
    test_dir_absolute_path = os.path.dirname(os.path.abspath(__file__))
    with db.session.begin_nested():
        media = TMedias(
            titre="test",
            chemin=os.path.join(test_dir_absolute_path, "assets", "coccinelle.jpg"),
            is_public=True,
            types=BibTypesMedia.query.first(),
        )
        db.session.add(media)
    db.session.commit()
    return media


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestAPIMedia:

    type_media_schema = Schema(
        [{"desc_type_media": Or(None, str), "id_type": int, "nom_type_media": str}]
    )

    def test_get_type_tmedias(self):
        response = self.client.get(url_for("t_media.get_type_tmedias"))
        assert response.status_code == 200
        assert self.type_media_schema.is_valid(response.json)

    def test_get_type_tmedias_one(self):
        response = self.client.get(url_for("t_media.get_type_tmedias", id=1))
        assert response.status_code == 200
        assert response.json["nom_type_media"] == "Photo_principale"

    def test_get_tmediasbyTaxon(self, noms_example):
        response = self.client.get(url_for("t_media.get_tmediasbyTaxon", cd_ref=67111))
        assert response.status_code == 200

    def test_get_tmedias(self):
        response = self.client.get(url_for("t_media.get_tmedias"))
        assert response.status_code == 200
        response = self.client.get(url_for("t_media.get_tmedias", id=1))
        assert response.status_code == 200

    # def test_insert_tmedias_url(self, user, noms_example):
    #     set_logged_user_cookie(self.client, user)

    #     data = {
    #         "is_public": True,
    #         "auteur": "GeoNature team",
    #         "url": "https://geonature.fr/documents/logo-geonature.jpg",
    #         "id_type": 2,
    #         "nom_type_media": "Photo",
    #         "titre": "Logo GeoNature",
    #         "desc_media": "CC",
    #         "cd_ref": 11165,
    #         "isFile": False,
    #     }
    #     response = self.client.post(
    #         url_for("t_media.insertUpdate_tmedias"),
    #         data=data,
    #     )

    #     assert response.status_code == 200

    #     id_media = json.loads(response.data)["id_media"]
    #     self.get_thumbnail(id_media)

    # def test_insert_tmedias_file(self, user, noms_example):
    #     set_logged_user_cookie(self.client, user)

    #     # Test send file
    #     with open(os.path.join("apptax/tests", "coccinelle.jpg"), "rb") as f:
    #         data = {
    #             "is_public": True,
    #             "auteur": "???",
    #             "id_type": 2,
    #             "nom_type_media": "Photo",
    #             "titre": "Coccinelle test fichier",
    #             "desc_media": "CC",
    #             "cd_ref": 11165,
    #             "isFile": True,
    #             "file": (f, "coccinelle.jpg"),
    #         }
    #         response = self.client.post(
    #             url_for("t_media.insertUpdate_tmedias"),
    #             data=data,
    #             content_type="multipart/form-data",
    #         )

    #     assert response.status_code == 200

    #     id_media = json.loads(response.data)["id_media"]
    #     self.get_thumbnail(id_media)

    @pytest.mark.parametrize(
        "get_params,expected_status_code",
        [
            ({}, 200),
            (dict(w=100), 200),
            (dict(h=100), 200),
            (dict(w=100, h=100), 200),
            (dict(w=100, h=-1), 403),
            (dict(w="a", h="b"), 403),
            (dict(h="b"), 403),
        ],
    )
    def test_get_thumbnail(self, media, get_params, expected_status_code):
        id_media = media.id_media

        response: Response = self.client.get(
            url_for(
                "t_media.getThumbnail_tmedias", id_media=id_media, **get_params, regenerate="true"
            ),
        )
        assert response.status_code == expected_status_code

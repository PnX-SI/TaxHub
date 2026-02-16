import json
import os
import io
from pathlib import Path


from apptax.taxonomie.models import BibTypesMedia, TMedias
import pytest
from sqlalchemy import select
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
from PIL import Image


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
def medias():
    test_dir_absolute_path = os.path.dirname(os.path.abspath(__file__))
    medias = {}

    medias_fixtures = [
        (
            "media_local_img",
            "test",
            "coccinelle.jpg",
            None,
            True,
            "Photo_principale",
        ),
        (
            "media_local_pdf",
            "test",
            "Thea_vigintiduopunctata_7231.pdf",
            None,
            True,
            "Photo_principale",
        ),
        (
            "media_remote_timeout",
            "test",
            None,
            "https://tools-httpstatus.pickup-services.com/200?sleep=10000",
            True,
            "Photo_principale",
        ),
        (
            "media_remote_image",
            "test",
            None,
            "https://upload.wikimedia.org/wikipedia/commons/f/f0/Taxa-4x35-tagskilt.jpg",
            True,
            "Photo_principale",
        ),
        (
            "media_remote_pdf",
            "test",
            None,
            "https://upload.wikimedia.org/wikipedia/commons/1/1a/Karte_von_Albanien_%281928%29.pdf",
            True,
            "PDF",
        ),
    ]
    with db.session.begin_nested():
        for key, titre, nom_fichier, url, is_public, types in medias_fixtures:
            media_types = {
                t.nom_type_media: t for t in db.session.scalars(select(BibTypesMedia)).all()
            }
            if nom_fichier:
                chemin = os.path.join(test_dir_absolute_path, "assets", nom_fichier)
            else:
                chemin = None
            medias[key] = TMedias(
                titre=titre,
                chemin=chemin,
                url=url,
                is_public=is_public,
                types=media_types[types],
            )
            db.session.add(medias[key])

    db.session.commit()
    return medias


def mock_remove_file(self, filepath: str):
    """
    Mock method to remove a media file.

    Parameters
    ----------
    filepath : str
        file path

    Returns
    -------
    bool
        True
    """
    return True


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

    def test_update_media(self, medias, monkeypatch):
        from apptax.taxonomie.filemanager import LocalFileManagerService

        # Ajout d'un monkeypatch pour la fonction remove_file
        monkeypatch.setattr(LocalFileManagerService, "remove_file", mock_remove_file)

        for media in medias.values():
            media.desc_media = "test updated"
            db.session.add(media)
        db.session.commit()

    @pytest.mark.parametrize(
        "key,get_params,expected_status_code",
        [
            ("media_local_img", dict(w=100), 200),
            ("media_local_pdf", dict(h=100), 404),
            ("media_remote_timeout", dict(h=100), 404),
            ("media_remote_image", dict(h=100), 200),
            ("media_remote_pdf", dict(h=100), 404),
        ],
    )
    def test_get_thumbnails(self, medias, key, get_params, expected_status_code, monkeypatch):

        from apptax.taxonomie.filemanager import LocalFileManagerService

        # Ajout d'un monkeypatch pour la fonction remove_file
        monkeypatch.setattr(LocalFileManagerService, "remove_file", mock_remove_file)

        media = medias[key]
        id_media = media.id_media
        response: Response = self.client.get(
            url_for(
                "t_media.getThumbnail_tmedias", id_media=id_media, **get_params, regenerate="true"
            ),
        )
        assert response.status_code == expected_status_code

    def test_get_thumbnail_regenerate(self, medias):
        """
        Test de régénération du thumbail
        Check si le fichier thumbnail n'est pas mis à jour lorsque regenerate est a False
        Check si le fichier thumbnail est mis à jour lorsque regenerate est a True

        PATCH
            Lancé uniquement localement car erreur sur la github action
        """
        id_media = medias["media_local_img"].id_media

        dir_thumb_base = Path(current_app.config["MEDIA_FOLDER"], "taxhub", "thumb").absolute()
        thumb_file_name = f"100x100.png"
        thumbpath_full = dir_thumb_base / str(id_media) / thumb_file_name

        # Génération du thumbnail une première fois
        response: Response = self.client.get(
            url_for("t_media.getThumbnail_tmedias", id_media=id_media, **dict(w=100, h=100)),
        )
        assert response.status_code == 200
        first_create_time = os.path.getmtime(thumbpath_full)

        # Appel au thumbnail une seconde fois sans regenerate
        response: Response = self.client.get(
            url_for("t_media.getThumbnail_tmedias", id_media=id_media, **dict(w=100, h=100)),
        )
        newmtime = os.path.getmtime(thumbpath_full)
        # La date de création du fichier ne doit pas avoir changé
        assert first_create_time == newmtime

        # Appel au thumbnail une troisième fois avec regenerate
        response: Response = self.client.get(
            url_for(
                "t_media.getThumbnail_tmedias",
                id_media=id_media,
                **dict(w=100, h=100),
                regenerate="true",
            ),
        )
        newmtime = os.path.getmtime(thumbpath_full)
        # La date de création du fichier doit avoir changé
        assert first_create_time < newmtime

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
    def test_get_thumbnail(self, medias, get_params, expected_status_code, monkeypatch):
        from apptax.taxonomie.filemanager import LocalFileManagerService

        # Ajout d'un monkeypatch pour la fonction remove_file
        monkeypatch.setattr(LocalFileManagerService, "remove_file", mock_remove_file)

        id_media = medias["media_local_img"].id_media

        response: Response = self.client.get(
            url_for(
                "t_media.getThumbnail_tmedias", id_media=id_media, **get_params, regenerate="true"
            ),
        )
        assert response.status_code == expected_status_code

        if expected_status_code == 200:
            image_data = response.data
            image = Image.open(io.BytesIO(image_data))
            actual_width, actual_height = image.size

            # Check dimensions if specified in get_params
            if "w" in get_params:
                expected_width = get_params["w"]
                assert (
                    expected_width - 1 <= actual_width <= expected_width + 1
                ), f"Expected width {get_params['w']}, got {actual_width}"
            if "h" in get_params:
                expected_height = get_params["h"]
                assert (
                    expected_height - 1 <= actual_height <= expected_height + 1
                ), f"Expected height {get_params['h']}, got {actual_height}"

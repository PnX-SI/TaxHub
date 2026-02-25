import json
import os
import io
import pytest
from pathlib import Path

from sqlalchemy import select
from flask import url_for, current_app, Response
from apptax.database import db, get_media_folder, get_media_thumb_folder

from apptax.taxonomie.models import BibTypesMedia, TMedias

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
from apptax.taxonomie.models import Taxref
from .fixtures import noms_example, attribut_example, liste, users

from PIL import Image


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestConfigS3Media:
    def test_get_media_subfolder(self, monkeypatch, users):
        set_logged_user_cookie(self.client, users["admin"])

        thumb_file_name = f"100x100.png"

        # --- Détermination des répertoires attendus selon la configuration ---
        # Lorsque MEDIA_FOLDER vaut "media", on utilise l'arborescence standard.
        # Sinon, le code utilise des sous-répertoires spécifiques (sub_medias/sub_thumb).
        if current_app.config["MEDIA_FOLDER"] == "media":
            dir_media_test = Path(current_app.config["MEDIA_FOLDER"], "taxhub")
            dir_thumb_test = Path(current_app.config["MEDIA_FOLDER"], "taxhub", "thumb")
        else:
            dir_media_test = Path(current_app.config["MEDIA_FOLDER"], "taxhub", "sub_medias")
            dir_thumb_test = Path(current_app.config["MEDIA_FOLDER"], "taxhub", "sub_thumb")

        dir_thumb_fct = get_media_thumb_folder()
        dir_media_fct = get_media_folder()
        # Vérifie que les chemins calculés correspondent bien à ceux attendus
        assert dir_thumb_fct.absolute() == dir_thumb_test.absolute()
        assert dir_media_fct.absolute() == dir_media_test.absolute()

        # Upload media
        f_jpg = open(os.path.join("apptax/tests/assets", "coccinelle.jpg"), "rb")
        form_taxref = {
            "medias-0-types": 1,
            "medias-0-titre": "test",
            "medias-0-auteur": "test",
            "medias-0-desc_media": "test",
            "medias-0-source": "test",
            "medias-0-is_public": True,
            "medias-0-chemin": (f_jpg, "coccinelle.jpg"),
        }
        req = self.client.post(
            "taxons/edit/?id=97947&url=/taxons/",
            data=form_taxref,
            content_type="multipart/form-data",
        )
        f_jpg.close()
        assert req.status_code == 302

        # --- Vérification côté base de données ---

        # Récupère le taxon et son média nouvellement créé

        tax = db.session.query(Taxref).filter_by(cd_nom=97947).scalar()
        media = tax.medias[0]
        media_file = Path(dir_media_fct, "97947_coccinelle.jpg").absolute()
        # Vérifie que le fichier a bien été créé physiquement
        assert media_file.is_file() == True

        # --- Test de génération du thumbnail (miniature) ---
        response: Response = self.client.get(
            url_for(
                "t_media.getThumbnail_tmedias", id_media=media.id_media, w=100, regenerate="true"
            ),
        )
        assert response.status_code == 200
        # Chemin attendu du thumbnail généré (dans dossier/id_media)
        thumb_file = Path(dir_thumb_fct, str(media.id_media), "100x-1.png").absolute()
        # Vérifie que la miniature existe bien
        assert thumb_file.is_file() == True

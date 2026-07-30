import json
import os
import csv
from io import BytesIO

import pytest
from pathlib import Path

from flask import url_for, current_app
from flask_admin.contrib.sqla import ModelView
from sqlalchemy import event, select
from werkzeug.datastructures import FileStorage
from apptax.database import db
from apptax.taxonomie.models import BibListes, BibAttributs, Taxref, BibAttributs
from apptax.admin.utils import populate_bib_liste
from pypnusershub.tests.utils import set_logged_user_cookie

from .fixtures import (
    noms_example,
    users,
    attribut_example,
    nom_with_media,
    liste,
)

form_bibliste = {
    "regne": "Animalia",
    "group2_inpn": "Autres",
    "nom_liste": "test",
    "code_liste": "test code",
    "desc_liste": "test desc",
}

form_attributs = {
    "nom_attribut": "test_attr",
    "label_attribut": "Attribut test",
    "desc_attribut": "Description attribut test",
    "type_attribut": "varchar(250)",
    "liste_valeur_attribut": '{"values":["val1","val2","val3"]}',
    "type_widget": "select",
    "ordre": 1,
    "theme": 1,
    "regne": "",
    "group2_inpn": "",
}


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestAdminView:

    def _get_filter_index(self, model_view: ModelView, filter_name: str) -> int:
        """
        Récupération de l'index d'un filtre
        nécessaire lors du requetage des données
        """
        for i, f in enumerate(model_view.get_filters()):
            if getattr(f, "name", None) == filter_name:
                return i
        return None

    def test_insert_bibliste(self, users):
        set_logged_user_cookie(self.client, users["admin"])
        req = self.client.post(
            "biblistes/new/?url=/biblistes/",
            data=form_bibliste,
            content_type="multipart/form-data",
        )
        assert req.status_code == 302

        assert db.session.query(
            db.session.query(BibListes).filter_by(nom_liste="test").exists()
        ).scalar()

    def test_insert_delete_attr(self, users):
        set_logged_user_cookie(self.client, users["admin"])
        query = select(BibAttributs).where(BibAttributs.nom_attribut == "test_attr").limit(1)

        req = self.client.post(
            "bibattributs/new/?url=/bibattributs/",
            data=form_attributs,
            content_type="multipart/form-data",
        )
        assert req.status_code == 302

        attr = db.session.scalar(query)
        assert not attr is None

        req = self.client.post(f"bibattributs/delete/?id={attr.id_attribut}")
        assert req.status_code == 302

        del_attr = db.session.scalar(query)
        assert del_attr is None

    def test_insert_taxref(self, users, attribut_example, liste):
        set_logged_user_cookie(self.client, users["admin"])

        attr_key = f"attr.{attribut_example.id_attribut}"
        f_pdf = open(os.path.join("apptax/tests/assets", "Thea_vigintiduopunctata_7231.pdf"), "rb")
        f_jpg = open(os.path.join("apptax/tests/assets", "coccinelle.jpg"), "rb")
        form_taxref = {
            attr_key: "val1",
            "listes": liste.id_liste,
            "medias-0-types": 1,
            "medias-0-titre": "test",
            "medias-0-auteur": "test",
            "medias-0-desc_media": "test",
            "medias-0-source": "test",
            "medias-0-is_public": True,
            "medias-0-chemin": (f_jpg, "coccinelle.jpg"),
            "medias-1-types": 1,
            "medias-1-titre": "test pdf",
            "medias-1-auteur": "test pdf",
            "medias-1-desc_media": "test pdf",
            "medias-1-source": "test",
            "medias-1-is_public": True,
            "medias-1-chemin": (f_pdf, "Thea_vigintiduopunctata_7231.pdf"),
        }
        req = self.client.post(
            "taxons/edit/?id=117526&url=/taxons/",
            data=form_taxref,
            content_type="multipart/form-data",
        )
        f_pdf.close()
        f_jpg.close()
        assert req.status_code == 302

        tax = db.session.query(Taxref).filter_by(cd_nom=117526).scalar()

        assert tax.attributs[0].valeur_attribut == form_taxref[attr_key]
        assert tax.listes[0].id_liste == form_taxref["listes"]
        assert tax.medias[0].chemin == "117526_coccinelle.jpg"
        assert tax.medias[1].chemin == "117526_Thea_vigintiduopunctata_7231.pdf"

    def test_insert_taxref_attributes(self, users, attribut_example):
        set_logged_user_cookie(self.client, users["admin"])

        attr_key = f"attr.{attribut_example.id_attribut}"

        form_taxref = {
            attr_key: "valère 1 ' avec des ? caract spéciô #?",
        }
        req = self.client.post(
            "taxons/edit/?id=534750&url=/taxons/",
            data=form_taxref,
            content_type="multipart/form-data",
        )
        assert req.status_code == 302
        tax = db.session.query(Taxref).filter_by(cd_nom=534750).scalar()

        assert tax.attributs[0].valeur_attribut == form_taxref[attr_key]

        # Edit taxref
        req = self.client.get("taxons/edit/?id=534750&url=/taxons/")
        assert req.status_code == 200

    def test_filter_synonyme(self):
        from apptax.admin.admin_view import TaxrefView

        taxref_view = TaxrefView(model=Taxref, session=db.session)

        filter_name = "Nom valide / synonyme"
        filter_id = self._get_filter_index(taxref_view, filter_name)
        count, results = taxref_view.get_list(
            page=0,
            sort_column=None,
            sort_desc=None,
            search=None,
            filters=[(filter_id, filter_name, "1")],
        )
        for tax in results:
            assert tax.cd_nom == tax.cd_ref
        count, results = taxref_view.get_list(
            page=0,
            sort_column=None,
            sort_desc=None,
            search=None,
            filters=[(filter_id, filter_name, "0")],
        )
        for tax in results:
            assert tax.cd_nom != tax.cd_ref

    def test_filter_media(self, nom_with_media):
        from apptax.admin.admin_view import TaxrefView

        taxref_view = TaxrefView(model=Taxref, session=db.session)
        filter_name = "Média"
        filter_id = self._get_filter_index(taxref_view, filter_name)
        count, results = taxref_view.get_list(
            page=0,
            sort_column=None,
            sort_desc=None,
            search=None,
            filters=[(filter_id, filter_name, "1")],
        )
        for tax in results:
            assert tax.medias

        taxref_view = TaxrefView(model=Taxref, session=db.session)
        count, results = taxref_view.get_list(
            page=0,
            sort_column=None,
            sort_desc=None,
            search=None,
            filters=[(filter_id, filter_name, "0")],
        )
        for tax in results:
            assert not tax.medias

    def test_filter_has_attr(self, noms_example):
        from apptax.admin.admin_view import TaxrefView

        taxref_view = TaxrefView(model=Taxref, session=db.session)
        filter_name = "Attributs"
        filter_id = self._get_filter_index(taxref_view, filter_name)
        # has attr
        count, results = taxref_view.get_list(
            page=0,
            sort_column=None,
            sort_desc=None,
            search=None,
            filters=[(filter_id, filter_name, "1")],
        )
        nom_with_attr = set([tax.cd_nom for tax in noms_example if tax.attributs])
        set_results = set([tax.cd_nom for tax in results])
        assert nom_with_attr.issubset(set_results)

        # does not have attr
        count, results = taxref_view.get_list(
            page=0,
            sort_column=None,
            sort_desc=None,
            search=None,
            filters=[(filter_id, filter_name, "0")],
        )
        nom_with_attr = set([tax.cd_nom for tax in noms_example if tax.attributs])
        set_results = set([tax.cd_nom for tax in results])
        assert nom_with_attr.isdisjoint(set_results)

    def test_filter_has_one_attr(self, noms_example):
        from apptax.admin.admin_view import TaxrefView

        id_attribut = noms_example[0].attributs[0].id_attribut
        taxref_view = TaxrefView(model=Taxref, session=db.session)
        filter_name = "A l'attribut"
        filter_id = self._get_filter_index(taxref_view, filter_name)
        # has attr
        count, results = taxref_view.get_list(
            page=0,
            sort_column=None,
            sort_desc=None,
            search=None,
            filters=[(filter_id, filter_name, id_attribut)],
        )
        nom_with_attr = set([tax.cd_nom for tax in noms_example if tax.attributs])
        set_results = set([tax.cd_nom for tax in results])
        assert nom_with_attr.issubset(set_results)

    def test_filter_list(self, noms_example, liste):
        from apptax.admin.admin_view import TaxrefView

        taxref_view = TaxrefView(model=Taxref, session=db.session)
        filter_name = "Est dans la liste"
        filter_id = self._get_filter_index(taxref_view, filter_name)
        # is in liste
        count, results = taxref_view.get_list(
            page=0,
            sort_column=None,
            sort_desc=None,
            search=None,
            filters=[(filter_id, filter_name, str(liste.id_liste))],
        )
        cd_nom_in_list = set([tax.cd_nom for tax in noms_example])
        cd_nom_results = set([tax.cd_nom for tax in results])
        assert cd_nom_in_list == cd_nom_results

    def test_filter_animalia(self):
        from apptax.admin.admin_view import TaxrefView

        taxref_view = TaxrefView(model=Taxref, session=db.session)
        filter_name = "Règne"
        filter_id = self._get_filter_index(taxref_view, filter_name)
        count, results = taxref_view.get_list(
            page=0,
            sort_column=None,
            sort_desc=None,
            search=None,
            filters=[(filter_id, filter_name, "Animalia")],
        )
        for tax in results:
            assert tax.regne == "Animalia"

    def test_filter_familly(self):
        from apptax.admin.admin_view import TaxrefView

        taxref_view = TaxrefView(model=Taxref, session=db.session)
        filter_name = "Famille"
        filter_id = self._get_filter_index(taxref_view, filter_name)
        count, results = taxref_view.get_list(
            page=0,
            sort_column=None,
            sort_desc=None,
            search=None,
            filters=[(filter_id, filter_name, "Arachnidiidae")],
        )
        for tax in results:
            assert tax.famille == "Arachnidiidae"

    def test_filter_order(self):
        from apptax.admin.admin_view import TaxrefView

        taxref_view = TaxrefView(model=Taxref, session=db.session)
        filter_name = "Ordre"
        filter_id = self._get_filter_index(taxref_view, filter_name)
        count, results = taxref_view.get_list(
            page=0,
            sort_column=None,
            sort_desc=None,
            search=None,
            filters=[(filter_id, filter_name, "Mobilida")],
        )
        for tax in results:
            assert tax.ordre == "Mobilida"

    def test_insert_list(self, users, liste):
        set_logged_user_cookie(self.client, users["admin"])
        with open(Path("apptax/tests/assets/cd_nom_list_valid.csv"), "rb") as f:
            req = self.client.post(
                f"biblistes/import_cd_nom/?id={liste.id_liste}",
                data={
                    "delimiter": ";",
                    "with_header": True,
                    "upload": (f, "cd_nom_list_valid.csv"),
                },
                content_type="multipart/form-data",
            )
            assert req.status_code == 302

        updated_liste = db.session.get(BibListes, liste.id_liste)
        # must reopen th file to read it ...
        with open(Path("apptax/tests/assets/cd_nom_list_valid.csv"), "r") as f:
            reader = csv.DictReader(f, delimiter=";")
            # test the csv cd_nom imported = cd_nom in liste
            {nom.cd_nom for nom in updated_liste.noms} == {row["cd_nom"] for row in reader}

        with open(Path("apptax/tests/assets/cd_nom_list_valid_extra_cols.csv"), "rb") as f:
            req = self.client.post(
                f"biblistes/import_cd_nom/?id={liste.id_liste}",
                data={
                    "delimiter": ";",
                    "with_header": True,
                    "upload": (f, "cd_nom_list_valid.csv"),
                },
                content_type="multipart/form-data",
            )
            assert req.status_code == 302

        with open(Path("apptax/tests/assets/cd_nom_list_with_error.csv"), "rb") as f:
            req = self.client.post(
                f"biblistes/import_cd_nom/?id={liste.id_liste}",
                data={
                    "delimiter": ";",
                    "with_header": True,
                    "upload": (f, "cd_nom_list_valid.csv"),
                },
                content_type="multipart/form-data",
            )
            assert req.status_code == 200

    def test_populate_bib_liste_runs_batch_insert_pipeline(self, liste):
        statements = []

        def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            statements.append(statement)

        event.listen(db.engine, "before_cursor_execute", before_cursor_execute)
        try:
            file = FileStorage(
                stream=BytesIO(b"cd_nom\n67111\n67111\n60612\n-1\n"),
                filename="cd_nom_test.csv",
            )

            result = populate_bib_liste(liste.id_liste, ";", True, file)
        finally:
            event.remove(db.engine, "before_cursor_execute", before_cursor_execute)

        taxref_selects = [s for s in statements if "FROM taxonomie.taxref" in s]
        cor_nom_liste_inserts = [
            s for s in statements if "INSERT INTO taxonomie.cor_nom_liste" in s
        ]

        assert result["unique_cd_nom_count"] == 3
        assert result["valid_cd_nom_count"] == 2
        assert result["not_found_count"] == 1
        assert result["inserted_count"] == 2
        assert result["already_in_list_count"] == 0
        assert result["rows_read"] == 4
        assert result["duration_ms"] >= 0

        assert len(taxref_selects) == 1
        assert " IN (" in taxref_selects[0]
        assert len(cor_nom_liste_inserts) == 1
        assert "ON CONFLICT" in cor_nom_liste_inserts[0]

    def test_import_cd_nom_view_redirects_with_success_flash(self, app, liste, monkeypatch):
        with app.app_context():
            import apptax.admin.admin_view as admin_view_module
            from apptax.admin.admin_view import BibListesView

            flashed_messages = []
            populate_calls = []

            def fake_populate_bib_liste(id_list, delimiter, with_header, file):
                populate_calls.append(
                    {
                        "id_list": id_list,
                        "delimiter": delimiter,
                        "with_header": with_header,
                        "filename": file.filename,
                    }
                )
                return {
                    "inserted_count": 3,
                    "already_in_list_count": 1,
                    "not_found_count": 2,
                    "rows_read": 6,
                    "duration_ms": 1234.0,
                }

            monkeypatch.setattr(admin_view_module, "populate_bib_liste", fake_populate_bib_liste)
            monkeypatch.setattr(
                admin_view_module,
                "flash",
                lambda message, category=None: flashed_messages.append((message, category)),
            )

            view = BibListesView(BibListes, db.session)
            monkeypatch.setattr(view, "get_url", lambda endpoint: "/biblistes/")

            with app.test_request_context(
                f"/biblistes/import_cd_nom/?id={liste.id_liste}",
                method="POST",
                data={
                    "delimiter": ";",
                    "with_header": "y",
                    "upload": (BytesIO(b"cd_nom\n"), "input.csv"),
                },
                content_type="multipart/form-data",
            ):
                response = view.import_cd_nom_view()

        assert response.status_code == 302
        assert response.location == "/biblistes/"
        assert populate_calls == [
            {
                "id_list": str(liste.id_liste),
                "delimiter": ";",
                "with_header": "y",
                "filename": "input.csv",
            }
        ]
        assert len(flashed_messages) == 1
        message, category = flashed_messages[0]
        assert isinstance(message, str)
        assert message
        assert category == "success"

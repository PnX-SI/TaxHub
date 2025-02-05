import json
import os
import csv

import pytest
from pathlib import Path

from flask import url_for, current_app

from apptax.database import db
from apptax.taxonomie.models import BibListes, BibAttributs, Taxref, BibAttributs
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

    def test_insert_attr(self, users):
        set_logged_user_cookie(self.client, users["admin"])
        req = self.client.post(
            "bibattributs/new/?url=/bibattributs/",
            data=form_attributs,
            content_type="multipart/form-data",
        )
        assert req.status_code == 302

        assert db.session.query(
            db.session.query(BibAttributs).filter_by(nom_attribut="test_attr").exists()
        ).scalar()

    def test_insert_taxref(self, users, attribut_example, liste):
        set_logged_user_cookie(self.client, users["admin"])

        attr_key = f"attr.{attribut_example.id_attribut}"

        with open(os.path.join("apptax/tests/assets", "coccinelle.jpg"), "rb") as f:
            form_taxref = {
                attr_key: "val1",
                "listes": liste.id_liste,
                "medias-0-types": 1,
                "medias-0-titre": "test",
                "medias-0-auteur": "test",
                "medias-0-desc_media": "test",
                "medias-0-source": "test",
                "medias-0-is_public": "test",
                "medias-0-chemin": (f, "coccinelle.jpg"),
            }
            req = self.client.post(
                "taxons/edit/?id=117526&url=/taxons/",
                data=form_taxref,
                content_type="multipart/form-data",
            )

        assert req.status_code == 302

        tax = db.session.query(Taxref).filter_by(cd_nom=117526).scalar()

        assert tax.attributs[0].valeur_attribut == form_taxref[attr_key]
        assert tax.listes[0].id_liste == form_taxref["listes"]
        assert tax.medias[0].chemin == "117526_coccinelle.jpg"

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
        count, results = taxref_view.get_list(
            page=0,
            sort_column=None,
            sort_desc=None,
            search=None,
            # 5 is the index of the list of column filters
            filters=[(5, "Nom valide / synonyme", "1")],
        )
        for tax in results:
            assert tax.cd_nom == tax.cd_ref
        count, results = taxref_view.get_list(
            page=0,
            sort_column=None,
            sort_desc=None,
            search=None,
            # 5 is the index of the list of column filters
            filters=[(5, "Nom valide / synonyme", "0")],
        )
        for tax in results:
            assert tax.cd_nom != tax.cd_ref

    def test_filter_media(self, nom_with_media):
        from apptax.admin.admin_view import TaxrefView

        taxref_view = TaxrefView(model=Taxref, session=db.session)
        count, results = taxref_view.get_list(
            page=0,
            sort_column=None,
            sort_desc=None,
            search=None,
            filters=[(6, "Média", "1")],
        )
        for tax in results:
            assert tax.medias

        taxref_view = TaxrefView(model=Taxref, session=db.session)
        count, results = taxref_view.get_list(
            page=0,
            sort_column=None,
            sort_desc=None,
            search=None,
            filters=[(6, "Média", "0")],
        )
        for tax in results:
            assert not tax.medias

    def test_filter_has_attr(self, noms_example):
        from apptax.admin.admin_view import TaxrefView

        taxref_view = TaxrefView(model=Taxref, session=db.session)
        # has attr
        count, results = taxref_view.get_list(
            page=0,
            sort_column=None,
            sort_desc=None,
            search=None,
            filters=[
                (9, "Attributs", "1")
            ],  # WARNING : le premier element du tuple est l'indice du tableau `column_filters` de la class Admin -> volatile !
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
            filters=[(7, "Attributs", "0")],
        )
        nom_with_attr = set([tax.cd_nom for tax in noms_example if tax.attributs])
        set_results = set([tax.cd_nom for tax in results])
        assert nom_with_attr.isdisjoint(set_results)

    def test_filter_list(self, noms_example, liste):
        from apptax.admin.admin_view import TaxrefView

        taxref_view = TaxrefView(model=Taxref, session=db.session)
        # is in liste
        count, results = taxref_view.get_list(
            page=0,
            sort_column=None,
            sort_desc=None,
            search=None,
            filters=[
                (5, "Est dans la liste", str(liste.id_liste))
            ],  # WARNING : le premier element du tuple est l'indice du tableau `column_filters` de la class Admin -> volatile !
        )
        cd_nom_in_list = set([tax.cd_nom for tax in noms_example])
        cd_nom_results = set([tax.cd_nom for tax in results])
        assert cd_nom_in_list == cd_nom_results

    def test_filter_animalia(self):
        from apptax.admin.admin_view import TaxrefView

        taxref_view = TaxrefView(model=Taxref, session=db.session)
        count, results = taxref_view.get_list(
            page=0,
            sort_column=None,
            sort_desc=None,
            search=None,
            filters=[(2, "Règne", "Animalia")],
        )
        for tax in results:
            assert tax.regne == "Animalia"

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

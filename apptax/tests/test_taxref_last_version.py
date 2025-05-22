import pytest
import os
import logging

pytestmark = pytest.mark.skipif(os.environ.get("CI") != "true", reason="Test for CI only")

from sqlalchemy import select, func
from apptax.database import db
from apptax.taxonomie.models import Taxref, TaxrefBdcStatutText, TMetaTaxref, TaxrefLiens
from apptax.taxonomie.commands.utils import populate_enable_bdc_statut_text


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestPopulateTaxref:
    """Test if taxref data are correctly populated"""

    def test_count_taxref(self):
        nb_taxref = db.session.scalar(select(func.count()).select_from(Taxref))
        assert nb_taxref == 708685

    def test_count_bdc_status(self):
        nb_bdc_texts = db.session.scalar(select(func.count()).select_from(TaxrefBdcStatutText))
        assert nb_bdc_texts == 912

    def test_link_bdc_statut_to_areas(self):
        text_barc = db.session.scalar(
            select(TaxrefBdcStatutText)
            .where(TaxrefBdcStatutText.cd_type_statut == "BARC")
            .limit(1)
        )
        assert len(text_barc.areas) == 96

    def test_enable_bdc_statut(self):
        logger = logging.getLogger()
        nb_bdc_texts_query = select(func.count()).select_from(
            select(TaxrefBdcStatutText).where(TaxrefBdcStatutText.enable == True)
        )
        # Par défaut tous les textes sont activés
        nb_bdc_texts = db.session.scalar(nb_bdc_texts_query)
        assert nb_bdc_texts == 912
        # Activation des textes d'un département
        populate_enable_bdc_statut_text(logger, True, ("01",))
        nb_bdc_texts = db.session.scalar(nb_bdc_texts_query)
        assert nb_bdc_texts == 180
        # Activation des textes de deux départements
        populate_enable_bdc_statut_text(logger, True, ("01", "78"))
        nb_bdc_texts = db.session.scalar(nb_bdc_texts_query)
        assert nb_bdc_texts == 195

    def test_taxref_version(self):
        taxref_version = db.session.scalar(
            select(TMetaTaxref).order_by(TMetaTaxref.update_date.desc()).limit(1)
        )
        assert taxref_version.version == 18

    def test_count_link(self):
        nb_taxref_liens = db.session.scalar(select(func.count()).select_from(TaxrefLiens))
        assert nb_taxref_liens == 2016747

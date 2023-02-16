import pytest
import os
import logging

pytestmark = pytest.mark.skipif(os.environ.get("CI") != "true", reason="Test for CI only")

from apptax.taxonomie.models import Taxref, TaxrefBdcStatutText
from apptax.taxonomie.commands.utils import populate_enable_bdc_statut_text


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestPopulateTaxref:
    """Test if taxref data are correctly populated"""

    def test_count_taxref(self):
        nb_taxref = Taxref.query.count()
        assert nb_taxref == 670946

    def test_count_bdc_status(self):
        nb_bdc_texts = TaxrefBdcStatutText.query.count()
        assert nb_bdc_texts == 915

    def test_link_bdc_statut_to_areas(self):
        text_barc = TaxrefBdcStatutText.query.filter(
            TaxrefBdcStatutText.cd_type_statut == "BARC"
        ).scalar()
        assert len(text_barc.areas) == 96

    def test_enable_bdc_statut(self):
        logger = logging.getLogger()
        # Par défaut tous les textes sont activés
        nb_bdc_texts = TaxrefBdcStatutText.query.filter(TaxrefBdcStatutText.enable == True).count()
        assert nb_bdc_texts == 915
        # Activation des textes d'un département
        populate_enable_bdc_statut_text(logger, True, ("01",))
        nb_bdc_texts = TaxrefBdcStatutText.query.filter(TaxrefBdcStatutText.enable == True).count()
        assert nb_bdc_texts == 183
        # Activation des textes de deux départements
        populate_enable_bdc_statut_text(logger, True, ("01", "78"))
        nb_bdc_texts = TaxrefBdcStatutText.query.filter(TaxrefBdcStatutText.enable == True).count()
        assert nb_bdc_texts == 194

    def test_link_bdc_statut_to_areas(self):
        text_barc = TaxrefBdcStatutText.query.filter(
            TaxrefBdcStatutText.cd_type_statut == "BARC"
        ).scalar()
        assert len(text_barc.areas) == 96

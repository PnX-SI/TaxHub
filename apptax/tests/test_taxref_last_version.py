import pytest
import os

pytestmark = pytest.mark.skipif(os.environ.get("CI") != "true", reason="Test for CI only")

from apptax.taxonomie.models import Taxref, TaxrefBdcStatutText


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestPopulateTaxref:
    """Test if taxref data are correctly populated"""

    def test_count_taxref(self):
        nb_taxref = Taxref.query.count()
        assert nb_taxref == 657609

    def test_count_bdc_status(self):
        nb_bdc_texts = TaxrefBdcStatutText.query.count()
        assert nb_bdc_texts == 873

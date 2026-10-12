import pytest
import csv
import click
from sqlalchemy import select
from pathlib import Path
from click.testing import CliRunner

from apptax.database import db
from apptax.taxonomie.models import BibTypesMedia, TMedias

from apptax.utils.external_apis import get_wikimedia_info, query_api_wikimedia


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestUtils:
    def test_get_wikimedia_info(self):
        results = get_wikimedia_info("Fissidens_taxifolius.jpeg")
        assert results == {
            "titre": "Fissidens taxifolius",
            "url": "https://upload.wikimedia.org/wikipedia/commons/2/27/Fissidens_taxifolius.jpeg",
            "auteur": ("Kristian Peters -- Fabelfroh 13:04, 28 May 2007 (UTC)",),
            "licence": "CC BY-SA 3.0",
            "desc_media": 'Eibenblättrige Spaltzahnmoos (<i><a href="//commons.wikimedia.org/wiki/Fissidens_taxifolius" title="Fissidens taxifolius">Fissidens taxifolius</a></i>)',
        }

    def test_get_wikimedia_info_false_file(self):
        results = get_wikimedia_info("FICHIER_INCONNU.jpeg")
        assert results == None

    def test_query_api_wikimedia_no_results(self):
        results = query_api_wikimedia(5986, "P18", 1)
        assert results == []

    def test_query_api_wikimedia(self):
        results = query_api_wikimedia(6181, "P18", 1)
        assert len(results) > 0

    def test_query_api_wikimedia_error(self):
        results = query_api_wikimedia(6181, "PRORITE_INCONNUE", 1)
        assert results == []

        results = query_api_wikimedia("faux_cd_nom", "P18", 1)
        assert results == []

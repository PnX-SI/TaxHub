import pytest
import csv
from sqlalchemy import select
from pathlib import Path
from click.testing import CliRunner

from apptax.database import db
from apptax.taxonomie.commands.taxref import import_wikidata_media
from apptax.taxonomie.models import BibTypesMedia, TMedias


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestCommand:
    def test_import_wikidata(self):
        runner = CliRunner()
        file = Path("apptax/tests/assets/wikidata_media.csv").absolute()
        #  Migration de taxref
        runner.invoke(import_wikidata_media, [str(file)])

        with open(Path("apptax/tests/assets/wikidata_media.csv"), "r") as f:
            reader = csv.DictReader(f, delimiter=",")
            # test the csv cd_nom imported = cd_nom in liste
            cd_refs = [row["cd_ref"] for row in reader if not row["cd_ref"] == "invalid"]

        medias = db.session.scalars(select(TMedias).where(TMedias.cd_ref.in_(cd_refs))).all()
        # Test if results
        assert medias
        for m in medias:
            # Test if source media is Wikimedia Commons
            assert m.source == "Wikimedia Commons"

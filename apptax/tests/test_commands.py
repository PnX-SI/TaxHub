import pytest
import csv
import click
from sqlalchemy import select
from pathlib import Path
from click.testing import CliRunner

from apptax.database import db
from apptax.taxonomie.commands.taxref import import_gbif_media, import_wikidata_media
from apptax.taxonomie.models import BibTypesMedia, TMedias


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestCommand:
    def test_import_wikidata(self):
        runner = CliRunner()
        file = Path("apptax/tests/assets/import_media.csv").absolute()
        #  Import de media de wikidata
        runner.invoke(import_wikidata_media, [str(file)])

        with open(Path("apptax/tests/assets/import_media.csv"), "r") as f:
            reader = csv.DictReader(f, delimiter=",")
            # test the csv cd_nom imported = cd_nom in liste
            cd_refs = [row["cd_ref"] for row in reader if not row["cd_ref"] == "invalid"]

        medias = db.session.scalars(select(TMedias).where(TMedias.cd_ref.in_(cd_refs))).all()
        # Test if results
        assert medias
        for m in medias:
            # Test if source media is Wikimedia Commons
            assert m.source == "Wikimedia Commons"

    def test_wrong_media_type(self):
        runner = CliRunner()
        file = Path("apptax/tests/assets/import_media.csv").absolute()

        #  Test wrong media_type wikidata
        result = runner.invoke(
            import_wikidata_media,
            [str(file), "--media-type-id", "9999"],
        )
        assert result.exit_code != 0
        assert isinstance(result.exception, SystemExit)
        assert "Invalid media type" in (result.output or "") or "Invalid media type" in str(
            result.exception
        )

        #  Test wrong media_type gbif
        result = runner.invoke(
            import_gbif_media,
            [str(file), "--media-type-id", "9999"],
        )
        assert result.exit_code != 0
        assert isinstance(result.exception, SystemExit)
        assert "Invalid media type" in (result.output or "") or "Invalid media type" in str(
            result.exception
        )

    def test_import_gbif(self):
        runner = CliRunner()
        file = Path("apptax/tests/assets/import_media.csv").absolute()

        #  Test wrong media_type
        result = runner.invoke(
            import_gbif_media,
            [str(file), "--media-type-id", "9999"],
        )
        assert result.exit_code != 0
        assert isinstance(result.exception, SystemExit)
        assert "Invalid media type" in (result.output or "") or "Invalid media type" in str(
            result.exception
        )

        # #  Import des médias depuis l'API gbif
        runner.invoke(import_gbif_media, [str(file)])

        with open(Path("apptax/tests/assets/import_media.csv"), "r") as f:
            reader = csv.DictReader(f, delimiter=",")
            # test the csv cd_nom imported = cd_nom in liste
            cd_refs = [row["cd_ref"] for row in reader if not row["cd_ref"] == "invalid"]

        medias = db.session.scalars(select(TMedias).where(TMedias.cd_ref.in_(cd_refs))).all()
        # Test if results
        assert medias
        for m in medias:
            # Test if source media is Via GBIF API
            assert m.source.endswith("Via GBIF API")

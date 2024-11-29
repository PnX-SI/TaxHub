import pytest
import sqlalchemy as sa

from .fixtures import *
from apptax.taxonomie.models import Taxref


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestModels:

    def test_tmedias_media_url_url(self, nom_with_media):
        taxon = db.session.execute(sa.select(Taxref).where(Taxref.cd_nom == 60577)).scalar_one()
        assert len(taxon.medias) == 1
        assert taxon.medias[0].media_url == "http://photo.com"

    def test_tmedias_media_url_chemin(self, nom_with_media_chemin):
        taxon = db.session.execute(sa.select(Taxref).where(Taxref.cd_nom == 60577)).scalar_one()
        assert len(taxon.medias) == 1
        assert taxon.medias[0].media_url.endswith("media/taxhub/mon_image.jpg")

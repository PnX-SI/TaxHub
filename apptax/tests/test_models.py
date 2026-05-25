import pytest
import sqlalchemy as sa

from .fixtures import *
from apptax.taxonomie.models import Taxref, TaxrefTree


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestModels:
    def test_taxref_tree_comparison(self):
        animalia = db.session.execute(
            sa.select(TaxrefTree).where(TaxrefTree.cd_nom == 183716)
        ).scalar_one()
        capra_ibex = db.session.execute(
            sa.select(TaxrefTree).where(TaxrefTree.cd_nom == 61098)
        ).scalar_one()
        cinnamon = db.session.execute(
            sa.select(TaxrefTree).where(TaxrefTree.cd_nom == 706584)
        ).scalar_one()

        # test ==
        assert animalia == 183716
        assert 183716 == animalia
        assert capra_ibex != animalia
        assert capra_ibex != 183716
        # test <
        assert not animalia < animalia
        assert not animalia < 183716
        with pytest.raises(TypeError):  # not supported
            assert not 183716 < animalia
        assert capra_ibex < animalia
        assert capra_ibex < 183716
        assert not animalia < capra_ibex
        assert not cinnamon < capra_ibex
        assert not capra_ibex < cinnamon
        assert not cinnamon < 61098
        # test <=
        assert animalia <= animalia
        assert animalia <= 183716
        with pytest.raises(TypeError):  # not supported
            assert 183716 <= animalia
        assert capra_ibex <= animalia
        assert capra_ibex <= 183716
        assert not animalia <= capra_ibex
        assert not cinnamon <= capra_ibex
        assert not capra_ibex <= cinnamon
        assert not cinnamon <= 61098
        # test >
        assert not animalia > animalia
        assert not 183716 > animalia
        with pytest.raises(TypeError):  # not supported
            assert not animalia > 183716
        assert 183716 > capra_ibex
        assert animalia > capra_ibex
        assert not capra_ibex > animalia
        assert not cinnamon > capra_ibex
        assert not capra_ibex > cinnamon
        assert not 61098 > cinnamon
        # test >=
        assert animalia >= animalia
        assert 183716 >= animalia
        with pytest.raises(TypeError):  # not supported
            assert animalia >= 183716
        assert 183716 >= capra_ibex
        assert animalia >= capra_ibex
        assert not capra_ibex >= animalia
        assert not cinnamon >= capra_ibex
        assert not capra_ibex >= cinnamon
        assert not 61098 >= cinnamon

    def test_taxref_comparison(self):
        animalia = db.session.execute(
            sa.select(Taxref).where(Taxref.cd_nom == 183716)
        ).scalar_one()
        capra_ibex = db.session.execute(
            sa.select(Taxref).where(Taxref.cd_nom == 61098)
        ).scalar_one()
        cinnamon = db.session.execute(
            sa.select(Taxref).where(Taxref.cd_nom == 706584)
        ).scalar_one()

        assert animalia <= animalia
        assert capra_ibex <= animalia
        assert not animalia <= capra_ibex
        assert not cinnamon <= animalia
        assert not animalia <= cinnamon
        assert not cinnamon <= capra_ibex
        assert not capra_ibex <= cinnamon

    def test_tmedias_media_url_url(self, nom_with_media):
        taxon = db.session.execute(sa.select(Taxref).where(Taxref.cd_nom == 60577)).scalar_one()
        assert len(taxon.medias) == 1
        assert taxon.medias[0].media_url == "http://photo.com"

    def test_tmedias_media_url_chemin(self, nom_with_media_chemin):
        taxon = db.session.execute(sa.select(Taxref).where(Taxref.cd_nom == 60577)).scalar_one()
        assert len(taxon.medias) == 1
        assert taxon.medias[0].media_url.endswith("media/taxhub/mon_image.jpg")

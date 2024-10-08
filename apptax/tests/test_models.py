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

        assert animalia <= animalia
        assert capra_ibex <= animalia
        assert not animalia <= capra_ibex
        assert not cinnamon <= animalia
        assert not animalia <= cinnamon
        assert not cinnamon <= capra_ibex
        assert not capra_ibex <= cinnamon

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

import pytest
from sqlalchemy import select

from apptax.database import db
from apptax.utils.wikidata_api import import_inpn_wikimedia

from apptax.taxonomie.models import BibTypesMedia, TMedias, Taxref


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestExternalAPI:
    def test_wikidata(self):

        cd_ref = 281
        # test media type
        media_type = db.session.scalar(
            select(BibTypesMedia).where(BibTypesMedia.nom_type_media == "Photo").limit(1)
        )
        import_inpn_wikimedia(cd_ref, "P18", media_type.id_type)

        medias = db.session.scalars(select(TMedias).where(TMedias.cd_ref == cd_ref)).all()
        # Test if results
        assert medias
        for m in medias:
            # Test if source media is Wikimedia Commons
            assert m.source == "Wikimedia Commons"

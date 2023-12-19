import requests

from sqlalchemy.orm.exc import NoResultFound

from apptax.database import db

from apptax.taxonomie.models import TMedias, BibTypesMedia, BibNoms


API_URL = "https://taxref.mnhn.fr/api"


def get_inpn_media(cd_ref, cd_nom, logger=None):
    """
    Fonction qui interroge l'api média de taxref
    et qui peuple la table média

    """
    url = f"{API_URL}/taxa/{cd_ref}/media"
    inpn_response = requests.get(url)

    if inpn_response.status_code != 200:
        if logger:
            logger.warning(
                f"{cd_ref} : l'URL {url} retourne le code HTTP {inpn_response.status_code} !"
            )
        return

    data = inpn_response.json()
    if "_embedded" not in data:
        if logger:
            logger.warning(f"{cd_ref} : l'URL {url} ne retourne aucune réponse!")
        return

    if not data["_embedded"]["media"]:
        if logger:
            logger.warning(f"{cd_ref} : l'URL {url}  ne retourne aucun media !")
        return

    medias = data["_embedded"]["media"]

    # Get media type
    type = BibTypesMedia.query.get(1)
    for m_inpn in medias:
        # Check is in bib_noms else create bib_noms
        try:
            bib_noms = BibNoms.query.filter_by(cd_nom=cd_ref).one()
        except NoResultFound:
            bib_noms = BibNoms(cd_ref=cd_ref, cd_nom=cd_nom)
            db.session.add(bib_noms)

        # Check if media exists
        try:
            m_obj = TMedias.query.filter_by(url=m_inpn["_links"]["file"]["href"]).one()
        except NoResultFound:
            m_obj = TMedias(
                url=m_inpn["_links"]["file"]["href"],
            )
        m_obj.cd_ref = cd_nom
        m_obj.titre = m_inpn["taxon"]["referenceNameHtml"]
        m_obj.nom = m_inpn["taxon"]["scientificName"]
        m_obj.auteur = m_inpn["copyright"]
        m_obj.desc_media = m_inpn["title"]
        m_obj.licence = m_inpn["licence"]
        m_obj.is_public = True
        m_obj.supprime = False
        m_obj.source = "INPN"
        m_obj.id_type = type.id_type

        db.session.add(m_obj)
        db.session.commit()

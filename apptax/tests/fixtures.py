import pytest

from flask_admin import Admin

from apptax.database import db
from apptax.taxonomie.models import (
    BibListes,
    BibThemes,
    BibAttributs,
    CorTaxonAttribut,
    Taxref,
    TMedias,
    BibTypesMedia,
)
from pypnusershub.db.models import User


bibnom_exemple = [
    (67111, 67111, "Ablette", None, "migrateur"),
    (60612, 60612, "Lynx boréal", None, "sédentaire"),
    (351, 351, "Grenouille rousse", None, "migrateur partiel"),
    (8326, 8326, "Cicindèle hybride", None, None),
    (11165, 11165, "Coccinelle à 7 points", None, None),
    (18437, 18437, "Ecrevisse à pieds blancs", None, None),
    (81065, 81065, "Alchémille rampante", None, None),
    (95186, 95186, "Inule fétide", None, None),
    (713776, 209902, "-", "un synonyme", None),
]


@pytest.fixture
def noms_without_listexample():
    noms = []
    with db.session.begin_nested():
        for cd_nom, cd_ref, nom_francais, comments, attr in bibnom_exemple:
            nom = Taxref.query.get(cd_nom)
            noms.append(nom)
    return noms


@pytest.fixture
def attribut_example():
    theme = BibThemes.query.filter_by(nom_theme="Mon territoire").one()
    with db.session.begin_nested():
        attribut = BibAttributs(
            nom_attribut="migrateur",
            label_attribut="Migrateur",
            liste_valeur_attribut='{"values":["migrateur","migrateur partiel","sédentaire", "valère 1 \' avec des ? caract spéciô #?"]}',
            obligatoire=False,
            desc_attribut="Défini le statut de migration pour le territoire",
            type_attribut="varchar(50)",
            type_widget="select",
            id_theme=theme.id_theme,
            regne="Animalia",
            group2_inpn="Oiseaux",
            ordre=1,
        )
        db.session.add(attribut)
    return attribut


@pytest.fixture(scope="function")
def liste():
    # Ajout d'une requete pour éviter une erreur d'intégrité reférentiel
    #  Résolution NON COMPRISE
    # sqlalchemy.exc.IntegrityError: (psycopg2.errors.UniqueViolation)
    #       duplicate key value violates unique constraint "unique_bib_listes_nom_liste"
    dumyselect = BibThemes.query.filter_by(nom_theme="Mon territoire").one()
    with db.session.begin_nested():
        _liste = BibListes.query.filter_by(code_liste="TEST_LIST").scalar()
        if _liste:
            return _liste

        _liste = BibListes(
            code_liste="TEST_LIST", nom_liste="Liste test", desc_liste="Liste description"
        )
        db.session.add(_liste)
    return _liste


def_liste = [
    {
        "code_liste": "TEST_LIST_NO_REGNE",
        "nom_liste": "Liste test no regne",
        "desc_liste": "Liste description",
    },
    {
        "code_liste": "TEST_LIST_Animalia",
        "nom_liste": "Liste test Animalia",
        "desc_liste": "Liste description",
        "regne": "Animalia",
    },
    {
        "code_liste": "TEST_LIST_Plantae",
        "nom_liste": "Liste test Plantae",
        "desc_liste": "Liste description",
        "regne": "Plantae",
    },
    {
        "code_liste": "TEST_LIST_Mousses",
        "nom_liste": "Liste test Mousses",
        "desc_liste": "Liste description",
        "regne": "Plantae",
        "group2_inpn": "Mousses",
    },
]


@pytest.fixture()
def liste_with_names(liste, noms_without_listexample):
    for nom in noms_without_listexample:
        liste.noms.append(nom)
    db.session.commit()
    return liste


@pytest.fixture()
def listes():
    with db.session.begin_nested():
        _listes = []
        for l in def_liste:
            _liste = BibListes(**l)
            db.session.add(_liste)
            _listes.append(_liste)
    return _listes


@pytest.fixture
def noms_example(attribut_example, liste):
    taxref_obj = []
    with db.session.begin_nested():
        for cd_nom, cd_ref, nom_francais, comments, attr in bibnom_exemple:
            nom = Taxref.query.get(cd_nom)
            if attr:
                cor_attr = CorTaxonAttribut(
                    id_attribut=attribut_example.id_attribut, cd_ref=cd_ref, valeur_attribut=attr
                )
                nom.attributs.append(cor_attr)
            db.session.add(nom)
            liste.noms.append(nom)
            taxref_obj.append(nom)
    return taxref_obj


@pytest.fixture
def nom_with_media():
    with db.session.begin_nested():
        taxon = Taxref.query.get(60577)
        media = TMedias(
            titre="test",
            url="http://photo.com",
            is_public=True,
            types=BibTypesMedia.query.first(),
        )
        taxon.medias.append(media)


@pytest.fixture
def nom_with_media_chemin():
    with db.session.begin_nested():
        taxon = Taxref.query.get(60577)
        media = TMedias(
            titre="test",
            chemin="mon_image.jpg",
            is_public=True,
            types=BibTypesMedia.query.first(),
        )
        taxon.medias.append(media)


@pytest.fixture(scope="session")
def users(app):
    users = {}
    dbusers = db.session.query(User).filter(User.groupe == False).all()
    for user in dbusers:
        users[user.identifiant] = user

    return users

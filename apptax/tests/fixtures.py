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
    with db.session.begin_nested():
        for cd_nom, cd_ref, nom_francais, comments in bibnom_exemple:
            nom = Taxref.query.get(cd_nom)
            db.session.add(nom)


@pytest.fixture
def attribut_example():
    theme = BibThemes.query.filter_by(nom_theme="Mon territoire").one()
    with db.session.begin_nested():
        attribut = BibAttributs(
            nom_attribut="migrateur",
            label_attribut="Migrateur",
            liste_valeur_attribut='{"values":["migrateur","migrateur partiel","sédentaire"]}',
            obligatoire=False,
            desc_attribut="Défini le statut de migration pour le territoire",
            type_attribut="varchar(50)",
            type_widget="select",
            id_theme=theme.id_theme,
            # regne="Animalia",
            # group2_inpn="Oiseaux",
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
        "v_regne": "Animalia",
    },
    {
        "code_liste": "TEST_LIST_Plantae",
        "nom_liste": "Liste test Plantae",
        "desc_liste": "Liste description",
        "v_regne": "Plantea",
    },
]


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
            supprime=False,
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


# test migration taxref détection des différents cas
# cd_nom, cd_ref, new_cd_ref, nom_complet, attr_value
data_migration_taxref_v15_to_v16 = [
    (106344, 106344, None, "Linum suffruticosum L., 1753", None),  # cd_nom sans substition
    (850859, 658167, 658167, "Navicula accomoda Hust., 1950", None),  # cd_nom avec substition
    (961306, 961306, 3945, "Motacilla yarrellii Gould, 1837", "A"),  # update cd_ref
    (459099, 459099, 6754, "Sphagnum denticulatum f. crassicladum", "A"),  # merge
    (6754, 6754, 6754, "Sphagnum auriculatum Schimp., 1857", "A"),  # merge
    (443766, 443766, 443766, "Dasyprocta leporina (Linnaeus, 1758)", "A"),  # merge with conflict
    (956958, 956958, 443766, "Mus aguti Linnaeus, 1766", "B"),  # merge with conflict
    (1900, 1900, 1898, "Alopecosa accentuata (Latreille, 1817)", "A"),  # split
    (233868, 1900, 233868, "Alopecosa barbipes (Sundevall, 1833)", None),  # split
]


# test migration taxref détection des différents cas
data_migration_taxref_v16_to_v17 = [
    (1018952, 1018952, None, "Fraxinus chinensis Roxb., 1820", None),  # cd_nom sans substition
    (974522, 461978, 36159, "Hebeloma repandum Bruchet, 1970", None),  # cd_nom avec substition
    (112285, 112285, 117874, "Papaver argemone L., 1753", "A"),  # update cd_ref
    (134113, 134113, 1019304, "Epilobium dodonaei subsp. dodonaei Vill., 1779", "A"),  # merge
    (96163, 96163, 1019304, "Epilobium dodonaei Vill., 1779", "A"),  # merge
    (112574, 112574, 112574, "Pedicularis comosa L., 1753", "A"),  # merge with conflict
    (
        138628,
        138628,
        112574,
        "Pedicularis comosa subsp. comosa L., 1753",
        "B",
    ),  # merge with conflict
    (54376, 54376, 54376, "Leptidea sinapis (Linnaeus, 1758)", "A"),  # split
    (713870, 54376, 713870, "Leptidea sinapis sinapis (Linnaeus, 1758)", None),  # split
]

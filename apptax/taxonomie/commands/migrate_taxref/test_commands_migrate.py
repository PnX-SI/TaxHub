import click

from click.testing import CliRunner
from flask.cli import with_appcontext

from sqlalchemy import select, delete, func
from sqlalchemy.orm.exc import NoResultFound

from apptax.database import db

from apptax.taxonomie.models import (
    CorTaxonAttribut,
    cor_nom_liste,
    TMedias,
    BibListes,
    Taxref,
    BibAttributs,
    BibThemes,
)

from apptax.database import db


@click.group(help="Test migrate")
def test_migrate_taxref():
    pass


# test migration de taxref 15 vers 16 détection des différents cas
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


# test migration taxref 16 vers 17 détection des différents cas
# cd_nom, cd_ref, new_cd_ref, nom_complet, attr_value
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

# test migration taxref 17 vers 18 détection des différents cas
# cd_nom, cd_ref, new_cd_ref, nom_complet, attr_value
data_migration_taxref_v17_to_v18 = [
    (997791, 997791, None, "Poropila dubia J.Schiller, 1925", None),  # cd_nom sans substition
    (608162, 608162, 104384, "Juncus x langei Erdner, 1906", None),  # cd_nom avec substition
    (54502, 54502, 1042429, "Parnassius mnemosyne (Linnaeus, 1758)", "A"),  # update cd_ref
    (103749, 103749, 103749, "Iris lutescens Lam., 1789", "A"),  # merge
    (136857, 136857, 103749, "Iris lutescens subsp. lutescens Lam., 1789", "A"),  # merge
    (116456, 116456, 116456, "Pulsatilla rubra (Lam.) Delarbre, 1800", "A"),  # merge with conflict
    (
        150342,
        150342,
        116456,
        "Pulsatilla rubra var. rubra (Lam.) Delarbre, 1800",
        "B",
    ),  # merge with conflict
    (29552, 29574, 29552, "Leccinum brunneogriseolum Lannoy & Estadès, 1991", "A"),  # split
    (
        29553,
        29574,
        29574,
        "Leccinum brunneogriseolum f. chlorinum Lannoy & Estadès, 1993",
        None,
    ),  # split
]


def populate_data(sample_data):
    liste = db.session.scalar(select(BibListes).where(BibListes.code_liste == "100"))
    theme = db.session.scalar(select(BibThemes).where(BibThemes.nom_theme == "Mon territoire"))

    attribut = BibAttributs(
        nom_attribut="test",
        label_attribut="Test",
        liste_valeur_attribut='{"values":["A","B","C"]}',
        obligatoire=False,
        type_attribut="varchar(50)",
        type_widget="select",
        id_theme=theme.id_theme,
        # regne="Animalia",
        # group2_inpn="Oiseaux",
        ordre=1,
    )
    db.session.add(attribut)

    for cd_nom, cd_ref, new_cd_ref, nom_complet, attr_value in sample_data:
        # cor_nom_liste
        nom = db.session.scalar(select(Taxref).where(Taxref.cd_nom == cd_nom))
        nom.listes.append(liste)
        db.session.add(nom)

        # medias
        media = TMedias(
            cd_ref=cd_ref,
            titre=nom_complet,
            url="https://upload.wikimedia.org/wikipedia/commons/f/f0/Taxa-4x35-tagskilt.jpg",
            id_type=1,
            is_public=True,
        )
        db.session.add(media)

        # attributs
        if attr_value:
            attr = CorTaxonAttribut(
                id_attribut=attribut.id_attribut, cd_ref=cd_ref, valeur_attribut=attr_value
            )
            db.session.add(attr)


def clean_data(sample_data):
    # Ménage
    for cd_nom, cd_ref, new_cd_ref, nom_complet, attr_value in sample_data:
        nom = db.session.scalar(select(Taxref).where(Taxref.cd_nom == new_cd_ref))
        if nom:
            nom.listes = []
            db.session.add(nom)
        db.session.execute(delete(CorTaxonAttribut).where(CorTaxonAttribut.cd_ref == new_cd_ref))
        db.session.execute(delete(CorTaxonAttribut).where(CorTaxonAttribut.cd_ref == cd_ref))
        db.session.execute(delete(cor_nom_liste).where(cor_nom_liste.c.cd_nom == cd_nom))
        db.session.execute(delete(TMedias).where(TMedias.cd_ref == new_cd_ref))
        db.session.execute(delete(TMedias).where(TMedias.cd_ref == cd_ref))

    # Suppression attribut
    db.session.execute(delete(BibAttributs).where(BibAttributs.nom_attribut == "test"))

    # Commit
    db.session.commit()


def open_csv_file(file_name):
    export_dir = "tmp"
    import csv

    with open(export_dir + "/" + file_name, "r") as file:
        csv_reader = csv.DictReader(file)
        data = [row for row in csv_reader]
        return data


def test_import_taxref_v16():
    from apptax.taxonomie.commands.migrate_taxref.commands_v16 import (
        import_taxref_v16,
        test_changes_detection,
        apply_changes,
    )

    """Test des commandes de migration de taxref v15 vers taxref v16

    Etapes :
      - données de test migration_example :
        - Erreur : merge de taxon avec attributs contradictoire
        - Erreur : cd_nom disparu sans cd_nom de remplacement
      - import de taxref v16
      - correction des erreurs

    """
    runner = CliRunner()

    runner.invoke(import_taxref_v16, [])

    # Test generated files
    data = open_csv_file("liste_changements.csv")
    # Test 2 conflicts
    conflict = [d for d in data if d["action"] == "Conflicts with attributes : test: A, test: B"]
    assert len(conflict) == 2
    # Test 4 merge
    merge = [d for d in data if d["cas"] == "merge"]
    assert len(merge) == 4
    # Test 2 update cd_ref
    update_cd_ref = [d for d in data if d["cas"] == "update cd_ref"]
    assert len(update_cd_ref) == 2

    # Résolution des conflits : Erreur liée à la fusion des noms
    db.session.execute(delete(CorTaxonAttribut).where(CorTaxonAttribut.cd_ref == 956958))
    db.session.commit()

    runner.invoke(test_changes_detection, [])
    data = open_csv_file("liste_changements.csv")
    # Test plus de conflits
    conflict = [d for d in data if d["action"] == "Conflicts with attributes : test: A, test: B"]
    assert len(conflict) == 0

    # test nom avec ou sans substition
    data = open_csv_file("missing_cd_nom_into_database.csv")
    sans_substitution = [d for d in data if d["cd_nom_remplacement"] == ""]
    assert len(sans_substitution) == 2
    sans_substitution = [d for d in data if not d["cd_nom_remplacement"] == ""]
    assert len(sans_substitution) == 1

    # Erreur liée au taxon sans substition
    # (106344, 106344, "Linum suffruticosum L., 1753", None), # cd_nom sans substition
    res = db.session.scalar(select(Taxref).where(Taxref.cd_nom == 106344))
    res.listes = []

    db.session.execute(delete(TMedias).where(TMedias.cd_ref == 106344))
    db.session.commit()

    runner.invoke(test_changes_detection, [])
    data = open_csv_file("missing_cd_nom_into_database.csv")
    sans_substitution = [d for d in data if d["cd_nom_remplacement"] == ""]
    assert len(sans_substitution) == 0

    #  Migration de taxref
    runner.invoke(apply_changes, ["--keep-oldtaxref"])

    # Analyse de la migration
    # cor_nom_liste : nb enregistrements initial = 9 ; final = 8
    #   perte de 1 du à la suppression du cd_nom 106344
    nb_cor_liste = db.session.scalar(select(func.count()).select_from(cor_nom_liste))
    assert nb_cor_liste == 8

    # cor_taxon_attribut : nb enregistrements initial = 6 ; final = 4
    #  perte de 2 du au merge des taxons 459099 + 6754 et 443766 + 956958
    results = db.session.scalar(select(func.count()).select_from(CorTaxonAttribut))
    assert results == 4

    # t_medias :
    # nb media initial = 9 ; final = 8
    # nb de taxon  initial = 8 ; final = 5
    # perte de 3 taxons :
    #       - 2 du au merge des taxons 459099 + 6754 et 443766 + 956958
    #       - 1 du à la suppression du cd_nom 106344
    # perte de 1 média du à la suppression sans remplacement de 106344
    results = db.session.scalar(select(func.count()).select_from(TMedias))
    assert results == 8

    nb_media_taxa = db.session.scalar(
        select(func.count(TMedias.cd_ref.distinct())).select_from(TMedias)
    )
    assert nb_media_taxa == 5


def test_import_taxref_v17():
    from apptax.taxonomie.commands.migrate_taxref.commands_v17 import (
        import_taxref_v17,
        test_changes_detection,
        apply_changes,
    )

    """Test des commandes de migration de taxref v16 vers taxref v17

    Etapes :
      - données de test migration_example :
        - Erreur : merge de taxon avec attributs contradictoire
        - Erreur : cd_nom disparu sans cd_nom de remplacement
      - import de taxref v17
      - correction des erreurs
      - migration des données
      - vérification des modifications réalisées lors de l'import
    """
    runner = CliRunner()

    runner.invoke(import_taxref_v17, [])

    # Test generated files
    data = open_csv_file("liste_changements.csv")
    # Test 2 conflicts
    conflict = [d for d in data if d["action"] == "Conflicts with attributes : test: A, test: B"]
    assert len(conflict) == 2
    # Test 4 merge
    merge = [d for d in data if d["cas"] == "merge"]
    assert len(merge) == 4
    # Test 2 update cd_ref
    update_cd_ref = [d for d in data if d["cas"] == "update cd_ref"]
    assert len(update_cd_ref) == 2

    # Résolution des conflits : Erreur liée à la fusion des noms
    db.session.execute(delete(CorTaxonAttribut).where(CorTaxonAttribut.cd_ref == 138628))
    db.session.commit()

    runner.invoke(test_changes_detection, [])
    data = open_csv_file("liste_changements.csv")
    # Test plus de conflits
    conflict = [d for d in data if d["action"] == "Conflicts with attributes : test: A, test: B"]
    assert len(conflict) == 0

    # test nom avec ou sans substition
    data = open_csv_file("missing_cd_nom_into_database.csv")
    sans_substitution = [d for d in data if d["cd_nom_remplacement"] == ""]
    assert len(sans_substitution) == 2
    sans_substitution = [d for d in data if not d["cd_nom_remplacement"] == ""]
    assert len(sans_substitution) == 1

    # Erreur liée au taxon sans substition
    # (1018952, 1018952, None, "Fraxinus chinensis Roxb., 1820", None),  # cd_nom sans substition
    res = db.session.scalar(select(Taxref).where(Taxref.cd_nom == 1018952))
    res.listes = []

    db.session.execute(delete(TMedias).where(TMedias.cd_ref == 1018952))
    db.session.commit()

    runner.invoke(test_changes_detection, [])
    data = open_csv_file("missing_cd_nom_into_database.csv")
    sans_substitution = [d for d in data if d["cd_nom_remplacement"] == ""]
    assert len(sans_substitution) == 0

    #  Migration de taxref
    runner.invoke(apply_changes, ["--keep-oldtaxref"])

    # Analyse de la migration
    # cor_nom_liste : nb enregistrements initial = 9 ; final = 8
    #   perte de 1 du à la suppression du cd_nom 106344
    results = db.session.scalar(select(func.count()).select_from(cor_nom_liste))
    assert results == 8

    # cor_taxon_attribut : nb enregistrements initial = 6 ; final = 4
    #  perte de 2 du au merge des taxons 112574 + 138628 et 96163 + 134113
    results = db.session.scalar(select(func.count()).select_from(CorTaxonAttribut))
    assert results == 4

    # t_medias :
    # nb media initial = 9 ; final = 8
    # nb de taxon  initial = 8 ; final = 5
    # perte de 3 taxons :
    #       - 2 du au merge des taxons 112574 + 138628 et 96163 + 134113
    #       - 1 du à la suppression du cd_nom 1018952
    # perte de 1 média du à la suppression sans remplacement de 1018952
    results = db.session.scalar(select(func.count()).select_from(TMedias))
    assert results == 8

    nb_media_taxa = db.session.scalar(
        select(func.count(TMedias.cd_ref.distinct())).select_from(TMedias)
    )
    assert nb_media_taxa == 5


def test_import_taxref_v18():
    from apptax.taxonomie.commands.migrate_taxref.commands_v18 import (
        import_taxref_v18,
        test_changes_detection,
        apply_changes,
    )

    """Test des commandes de migration de taxref v16 vers taxref v18

    Etapes :
      - données de test migration_example :
        - Erreur : merge de taxon avec attributs contradictoire
        - Erreur : cd_nom disparu sans cd_nom de remplacement
      - import de taxref v18
      - correction des erreurs
      - migration des données
      - vérification des modifications réalisées lors de l'import
    """
    runner = CliRunner()
    runner.invoke(import_taxref_v18, [])

    # Test generated files
    data = open_csv_file("liste_changements.csv")
    # Test 2 conflicts
    conflict = [d for d in data if d["action"] == "Conflicts with attributes : test: A, test: B"]
    assert len(conflict) == 2

    # Test 4 merge
    merge = [d for d in data if d["cas"] == "merge"]
    assert len(merge) == 4
    # Test 2 update cd_ref
    update_cd_ref = [d for d in data if d["cas"] == "update cd_ref"]
    assert len(update_cd_ref) == 1

    # Résolution des conflits : Erreur liée à la fusion des noms Pulsatilla rubra
    # (150342, 150342, 116456, "Pulsatilla rubra var. rubra (Lam.) Delarbre, 1800", "B"), # merge with conflict
    db.session.execute(delete(CorTaxonAttribut).where(CorTaxonAttribut.cd_ref == 150342))
    db.session.commit()

    runner.invoke(test_changes_detection, [])
    data = open_csv_file("liste_changements.csv")
    # Test plus de conflits
    conflict = [d for d in data if d["action"] == "Conflicts with attributes : test: A, test: B"]
    assert len(conflict) == 0

    # test nom avec ou sans substition
    # Missing 2 : cor_nom_liste et t_medias
    data = open_csv_file("missing_cd_nom_into_database.csv")

    sans_substitution = [d for d in data if d["cd_nom_remplacement"] == ""]
    assert len(sans_substitution) == 2
    avec_substitution = [d for d in data if not d["cd_nom_remplacement"] == ""]
    assert len(avec_substitution) == 2

    # Erreur liée au taxon sans substition
    # (997791, 997791, None, "Poropila dubia J.Schiller, 1925", None),  # cd_nom sans substition
    tax_sans_substitution = db.session.scalar(select(Taxref).where(Taxref.cd_nom == 997791))
    tax_sans_substitution.listes = []

    db.session.execute(delete(TMedias).where(TMedias.cd_ref == 997791))
    db.session.commit()

    runner.invoke(test_changes_detection, [])
    data = open_csv_file("missing_cd_nom_into_database.csv")
    sans_substitution = [d for d in data if d["cd_nom_remplacement"] == ""]
    assert len(sans_substitution) == 0

    #  Migration de taxref
    runner.invoke(apply_changes, ["--keep-oldtaxref"])

    # Analyse de la migration
    # cor_nom_liste : nb enregistrements initial = 9 ; final = 8
    #   perte de 1 du à la suppression du cd_nom 997791
    nb_cor_liste = db.session.scalar(select(func.count()).select_from(cor_nom_liste))
    assert nb_cor_liste == 8

    # cor_taxon_attribut : nb enregistrements initial = 6 ; final = 4
    #  perte de 2 du au merge des taxons 103749 + 136857 et 116456 + 150342
    nb_attr = db.session.scalar(select(func.count()).select_from(CorTaxonAttribut))
    assert nb_attr == 4

    # t_medias :
    # nb media initial = 9 ; final = 8
    # nb de taxon  initial = 8 ; final = 5
    # perte de 3 taxons :
    #       - 2 du au merge des taxons 103749 + 136857 et 116456 + 150342
    #       - 1 du à la suppression du cd_nom 997791
    # perte de 1 média du à la suppression sans remplacement de 997791
    nb_media = db.session.scalar(select(func.count()).select_from(TMedias))
    assert nb_media == 8

    nb_media_taxa = db.session.scalar(
        select(func.count(TMedias.cd_ref.distinct())).select_from(TMedias)
    )
    assert nb_media_taxa == 5


@test_migrate_taxref.command()
@with_appcontext
def test_taxref_v16_migration():
    """Test des commandes de migration de taxref v15 vers taxref v16"""
    populate_data(data_migration_taxref_v15_to_v16)
    try:
        test_import_taxref_v16()
    except AssertionError as e:
        raise (e)
    finally:
        clean_data(data_migration_taxref_v15_to_v16)


@test_migrate_taxref.command()
@with_appcontext
def test_taxref_v17_migration():
    """Test des commandes de migration de taxref v16 vers taxref v17"""
    populate_data(data_migration_taxref_v16_to_v17)
    try:
        test_import_taxref_v17()
    except AssertionError as e:
        raise (e)
    finally:
        clean_data(data_migration_taxref_v16_to_v17)


@test_migrate_taxref.command()
@with_appcontext
def test_taxref_v18_migration():
    """Test des commandes de migration de taxref v17 vers taxref v18"""
    populate_data(data_migration_taxref_v17_to_v18)
    try:
        test_import_taxref_v18()
    except AssertionError as e:
        raise (e)
    finally:
        clean_data(data_migration_taxref_v17_to_v18)

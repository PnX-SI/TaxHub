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

from apptax.tests.fixtures import data_migration_taxref_v15_to_v16

from apptax.database import db

from click.testing import CliRunner


def populate_data():
    liste = BibListes.query.filter_by(code_liste="100").one()

    theme = BibThemes.query.filter_by(nom_theme="Mon territoire").one()
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

    for cd_nom, cd_ref, new_cd_ref, nom_complet, attr_value in data_migration_taxref_v15_to_v16:
        # cor_nom_liste
        nom = Taxref.query.get(cd_nom)
        db.session.add(nom)
        liste.noms.append(nom)

        # medias
        media = TMedias(
            cd_ref=cd_ref,
            titre=nom_complet,
            url="https://upload.wikimedia.org/wikipedia/commons/f/f0/Taxa-4x35-tagskilt.jpg",
            id_type=1,
            is_public=True,
            supprime=False,
        )
        db.session.add(media)

        # attributs
        if attr_value:
            attr = CorTaxonAttribut(
                id_attribut=attribut.id_attribut, cd_ref=cd_ref, valeur_attribut=attr_value
            )
            db.session.add(attr)


def clean_data():
    # Ménage
    for cd_nom, cd_ref, new_cd_ref, nom_complet, attr_value in data_migration_taxref_v15_to_v16:
        nom = Taxref.query.filter(Taxref.cd_nom == new_cd_ref).first()
        if nom:
            nom.listes = []
            db.session.add(nom)
        res = CorTaxonAttribut.query.filter(CorTaxonAttribut.cd_ref == new_cd_ref).all()
        for c in res:
            db.session.delete(c)
        res = TMedias.query.filter(TMedias.cd_ref == new_cd_ref).all()
        for c in res:
            db.session.delete(c)

    try:
        attr = BibAttributs.query.filter(BibAttributs.nom_attribut == "test").one()

        db.session.delete(attr)
    except NoResultFound:
        pass
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
    res = CorTaxonAttribut.query.filter(CorTaxonAttribut.cd_ref == 956958)
    for c in res:
        db.session.delete(c)
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
    res = db.session.query(Taxref).filter(Taxref.cd_nom == 106344)
    for c in res:
        c.listes = []

    res = TMedias.query.filter(TMedias.cd_ref == 106344)
    for c in res:
        db.session.delete(c)
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
    results = db.session.query(cor_nom_liste).count()
    assert results == 8

    # cor_taxon_attribut : nb enregistrements initial = 6 ; final = 4
    #  perte de 2 du au merge des taxons 459099 + 6754 et 443766 + 956958
    results = CorTaxonAttribut.query.all()
    assert len(results) == 4

    # t_medias :
    # nb media initial = 9 ; final = 8
    # nb de taxon  initial = 8 ; final = 5
    # perte de 3 taxons :
    #       - 2 du au merge des taxons 459099 + 6754 et 443766 + 956958
    #       - 1 du à la suppression du cd_nom 106344
    # perte de 1 média du à la suppression sans remplacement de 106344
    results = TMedias.query.count()
    assert results == 8

    results = db.session.query(TMedias.cd_ref).distinct().count()
    assert results == 5

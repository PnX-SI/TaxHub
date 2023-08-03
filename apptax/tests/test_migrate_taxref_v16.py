import json
import os

import pytest
from flask import url_for, current_app

from apptax.database import db

from apptax.taxonomie.models import CorTaxonAttribut, CorNomListe, TMedias, BibListes

from .fixtures import migration_example

import importlib
from sqlalchemy import text


from apptax.database import db
from apptax.taxonomie.commands.migrate_taxref.commands_v16 import (
    import_taxref_v16,
    test_changes_detection,
    apply_changes,
)


from click.testing import CliRunner


pytestmark = pytest.mark.skipif(
    os.environ.get("CI") == "true", reason="Test for custom database installation"
)


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestMigrateTaxrefV16:
    def analyse_cli_log(self, init_dict, result_logs):
        """Analyse des logs
        compare les résultats obtenus et ceux attendus
        """
        assert len(result_logs) == len(init_dict)
        for msg, level in result_logs.items():
            try:
                if level == init_dict[msg]:
                    assert True
                else:
                    assert False
            except KeyError:
                assert False

    def test_import_taxref_v16(self, caplog, migration_example):
        """Test des commandes de migration de taxref v15 vers taxref v16

        Etapes :
         - données de test migration_example :
            - Erreur : merge de taxon avec attributs contradictoire
            - Erreur : cd_nom disparu sans cd_nom de remplacement
         - import de taxref v16
         - correction des erreurs

        """
        runner = CliRunner()

        import_taxref_v16_log_messages = {
            "Import TAXREFv16 into tmp table…": "INFO",
            "Insert TAXREFv16 into taxonomie.import_taxref table…": "INFO",
            "Insert missing cd_nom into taxonomie.cdnom_disparu table…": "INFO",
        }

        import_taxref_v16_test_conflicts = {
            "List of taxref changes done in tmp": "INFO",
            "There is 2 unresolved conflits. You can't continue migration": "ERROR",
        }

        import_taxref_v16_test_ok = {
            "List of taxref changes done in tmp": "INFO",
            "Some cd_nom referencing in data where missing from taxref v15 -> see file missing_cd_nom_into_database.csv": "WARNING",
        }

        import_taxref_v16_test_missing_cd_nom = {
            "No substitition for cd_nom Linum suffruticosum L., 1753 in table taxonomie.cor_nom_liste": "ERROR",
            "No substitition for cd_nom Linum suffruticosum L., 1753 in table taxonomie.t_medias": "ERROR",
            "Some cd_nom will disappear without substitute. You can't continue migration. Analyse exports files": "ERROR",
        }

        migrate_taxref_v16 = {
            "Migration of taxref ...": "INFO",
            "it's done": "INFO",
            "Insert BDC statuts types…": "INFO",
            "Insert BDC statuts…": "INFO",
            "Populate BDC statuts…": "INFO",
            "Populate Link BDC statuts with Areas…": "INFO",
            "Clean DB": "INFO",
            "Refresh materialized views…": "INFO",
        }

        runner.invoke(import_taxref_v16, [])
        self.analyse_cli_log(
            init_dict={**import_taxref_v16_log_messages, **import_taxref_v16_test_conflicts},
            result_logs={c.msg: c.levelname for c in caplog.records},
        )

        caplog.clear()
        runner.invoke(test_changes_detection, [])
        self.analyse_cli_log(
            init_dict=import_taxref_v16_test_conflicts,
            result_logs={c.msg: c.levelname for c in caplog.records},
        )

        # Résolution des conflits : Erreur liée à la fusion des noms
        res = CorTaxonAttribut.query.filter(CorTaxonAttribut.cd_ref == 956958)
        for c in res:
            db.session.delete(c)
        db.session.commit()

        caplog.clear()
        runner.invoke(test_changes_detection, [])
        # Analyse Log
        self.analyse_cli_log(
            init_dict={**import_taxref_v16_test_ok, **import_taxref_v16_test_missing_cd_nom},
            result_logs={c.msg: c.levelname for c in caplog.records},
        )

        # Erreur liée au taxon sans substition
        # (106344, 106344, "Linum suffruticosum L., 1753", None), # cd_nom sans substition
        res = CorNomListe.query.filter(CorNomListe.cd_nom == 106344)
        for c in res:
            db.session.delete(c)
        res = TMedias.query.filter(TMedias.cd_ref == 106344)
        for c in res:
            db.session.delete(c)
        db.session.commit()

        caplog.clear()
        runner.invoke(test_changes_detection, [])
        # Analyse Log
        self.analyse_cli_log(
            init_dict=import_taxref_v16_test_ok,
            result_logs={c.msg: c.levelname for c in caplog.records},
        )

        #  Migration de taxref
        runner.invoke(apply_changes, ["--keep-oldtaxref"])
        self.analyse_cli_log(
            init_dict={**import_taxref_v16_test_ok, **migrate_taxref_v16},
            result_logs={c.msg: c.levelname for c in caplog.records},
        )

        # # Analyse de la migration
        # # cor_nom_liste : 6 enregistrements
        results = CorNomListe.query.count()
        assert results == 6

        # cor_taxon_attribut :3 attributs
        results = CorTaxonAttribut.query.all()
        assert len(results) == 3

        # t_medias : 5 medias sur 3 taxons
        results = TMedias.query.count()
        assert results == 6

        results = db.session.query(TMedias.cd_ref).distinct().count()
        assert results == 4

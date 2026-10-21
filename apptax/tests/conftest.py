import os

import pytest
from apptax.database import db
from apptax.app import create_app
from utils_flask_sqla.tests.utils import JSONClient, TestSession
from apptax.tests.fixtures import *

db.session = db._make_scoped_session({"class_": TestSession})


@pytest.fixture(scope="session", autouse=True)
def _app():
    # Préfixe des routes de l'API comme en production (cf. taxhub_config.toml.default) :
    # sans préfixe, les routes /bibattributs/, /biblistes/ et /tmedias/ de l'API
    # sont masquées par les vues admin de même url
    os.environ.setdefault("TAXHUB_API_PREFIX", "/api")
    app = create_app()
    app.testing = True
    app.test_client_class = JSONClient
    app.config["SERVER_NAME"] = "taxhub.geonature.fr"  # required by url_for

    with app.app_context():
        yield app


@pytest.fixture(scope="session")
def _session(_app):
    return db.session


@pytest.fixture(scope="session", autouse=True)
def app(_app, _session):
    return _app

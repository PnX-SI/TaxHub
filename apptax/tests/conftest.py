import pytest

from apptax.database import db
from apptax.app import create_app
from utils_flask_sqla.tests.utils import JSONClient


@pytest.fixture(scope="session", autouse=True)
def app():
    app = create_app()
    app.testing = True
    app.test_client_class = JSONClient
    app.config["SERVER_NAME"] = "taxhub.geonature.fr"  # required by url_for
    with app.app_context():
        transaction = db.session.begin_nested()
        yield app
        transaction.rollback()


@pytest.fixture
def _session(app):
    return db.session

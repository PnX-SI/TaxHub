import pytest

from apptax.database import db
from apptax.app import create_app
from utils_flask_sqla.tests.utils import JSONClient


@pytest.fixture(scope="session", autouse=True)
def _app():
    app = create_app()
    app.testing = True
    app.test_client_class = JSONClient
    app.config["SERVER_NAME"] = "taxhub.geonature.fr"  # required by url_for
    app.config["MEDIA_FOLDER"] = "medias/"  # required by url_for
    with app.app_context():
        yield app


@pytest.fixture(scope="session")
def _session(_app):
    return db.session


@pytest.fixture(scope="session", autouse=True)
def app(_app, _session):
    return _app

import os, logging
import pytest
import psycopg2

import server


def pytest_sessionstart(session):
    """ before session.main() is called. """
    app = server.init_app()
    app.config["TESTING"] = True
    # push the app_context
    ctx = app.app_context()
    ctx.push()
    logging.disable(logging.DEBUG)

    # # setup test data
    # execute_script("delete_sample_data.sql")
    # execute_script("sample_data.sql")


@pytest.fixture
def app():
    app = server.init_app()
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    return app


@pytest.fixture
def client(app):
    return app.test_client()

import sys
from os import environ
from importlib import import_module
from pathlib import Path

import requests
from flask_sqlalchemy import SQLAlchemy

if sys.version_info < (3, 9):
    from importlib_metadata import version, PackageNotFoundError
else:
    from importlib.metadata import version, PackageNotFoundError


db_path = environ.get("FLASK_SQLALCHEMY_DB")
if db_path and db_path != f"{__name__}.db":
    db_module_name, db_object_name = db_path.rsplit(".", 1)
    db_module = import_module(db_module_name)
    db = getattr(db_module, db_object_name)
else:
    db = SQLAlchemy()
    environ["FLASK_SQLALCHEMY_DB"] = f"{__name__}.db"


ROOT_DIR = Path(__file__).absolute().parent.parent
try:
    TAXHUB_VERSION = version("taxhub")
except PackageNotFoundError:
    with open(str((ROOT_DIR / "VERSION"))) as v:
        TAXHUB_VERSION = v.read()


def generate_user_agent() -> str:
    """Generate a generic user-agent description for requests
    Returns:
        str: generic user-agent
    """
    user_agent = f"TaxHub/{TAXHUB_VERSION} (https://github.com/PnX-SI/TaxHub) python-requests/{requests.__version__}"
    return user_agent

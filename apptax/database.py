from os import environ
from importlib import import_module

from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.model import Model
from sqlalchemy.sql.expression import Select

from utils_flask_sqla.models import SelectModelMixin
from utils_flask_sqla.sqlalchemy import CustomSQLAlchemy

db_path = environ.get("FLASK_SQLALCHEMY_DB")
if db_path and db_path != f"{__name__}.db":
    db_module_name, db_object_name = db_path.rsplit(".", 1)
    db_module = import_module(db_module_name)
    db = getattr(db_module, db_object_name)
else:
    db = CustomSQLAlchemy(model_class=SelectModelMixin)
    environ["FLASK_SQLALCHEMY_DB"] = f"{__name__}.db"

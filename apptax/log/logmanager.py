# coding: utf8
from flask_sqlalchemy import SQLAlchemy
from .models import TaxhubAdminLog

from . import db


def log_action(id_role, object_type, object_id, object_repr, change_type, change_message):
    log = TaxhubAdminLog(
        id_role=id_role,
        object_type=object_type,
        object_id=object_id,
        object_repr=object_repr,
        change_type=change_type,
        change_message=change_message,
    )
    db.session.add(log)
    db.session.commit()

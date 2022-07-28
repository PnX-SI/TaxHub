# coding: utf8
from flask_sqlalchemy import SQLAlchemy

from utils_flask_sqla.serializers import serializable

from . import db


@serializable
class TaxhubAdminLog(db.Model):
    __tablename__ = "taxhub_admin_log"
    __table_args__ = {"schema": "taxonomie"}
    id = db.Column(db.Integer, primary_key=True)
    action_time = db.Column(db.DateTime, default=db.func.now(), nullable=False)
    id_role = db.Column(db.Integer, primary_key=True)
    object_type = db.Column(db.Unicode)
    object_id = db.Column(db.Integer, primary_key=True)
    object_repr = db.Column(db.Unicode)
    change_type = db.Column(db.Unicode)
    change_message = db.Column(db.Unicode)

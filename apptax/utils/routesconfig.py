import os
from flask import jsonify, json, Blueprint, request, Response, g, current_app, send_file

from ..utils.utilssqlalchemy import json_resp


adresses = Blueprint("configs", __name__)

from pypnusershub.db.models import Application

from ..database import db


@adresses.route("", methods=["GET"])
@json_resp
def get_config(id=None):
    """
    Route générant la configuration utile au frontend
    """

    data = (
        db.session.query(Application)
        .filter_by(code_application=current_app.config["CODE_APPLICATION"])
        .first()
    )

    return {"id_application": data.id_application}

import os
from flask import jsonify, json, Blueprint, current_app, Response
from ..utils.utilssqlalchemy import json_resp


adresses = Blueprint("configs", __name__)



@adresses.route("", methods=["GET"])
def get_config():
    """
    Route générant la configuration utile au frontend
    """

    js = f"const APPLICATION_ROOT='{current_app.config.get('APPLICATION_ROOT')}'"

    resp = Response(
        response=js, status=200,  mimetype="text/plain")
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp
from flask import Blueprint, current_app, Response

adresses = Blueprint("configs", __name__)


@adresses.route("", methods=["GET"])
def get_config():
    """
    Route générant la configuration utile au frontend
    """

    js = f"const APPLICATION_ROOT='{current_app.config.get('APPLICATION_ROOT')}'"

    resp = Response(response=js, status=200, mimetype="application/javascript")
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp

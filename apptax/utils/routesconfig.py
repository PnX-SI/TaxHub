from flask import Blueprint, current_app, Response, url_for

adresses = Blueprint("configs", __name__)


@adresses.route("<variable_name>/<str_endpoint>", methods=["GET"])
def get_config(variable_name, str_endpoint):
    """
    Route générant la configuration utile au frontend
    """
    url = url_for(str_endpoint, _external=True)
    js = f"const {variable_name}='{url}'"

    resp = Response(response=js, status=200, mimetype="application/javascript")
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp

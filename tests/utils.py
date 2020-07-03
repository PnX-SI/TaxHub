"""
    Fonctions utilitaires pour les tests
"""
import json

def post_json(client, url, json_dict, query_string=None):
    """Send dictionary json_dict as a json to the specified url """
    return client.post(
        url,
        data=json.dumps(json_dict),
        content_type="application/json",
        query_string=query_string,
    )


def json_of_response(response):
    """Decode json from response"""
    return json.loads(response.data.decode("utf8"))


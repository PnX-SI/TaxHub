import pytest
from flask import url_for
from .utils import json_of_response
from schema import Schema, Optional, Or


@pytest.mark.usefixtures("client_class")
class TestAPIMedia:
    def test_get_tmediasbyTaxon(self):
        response = self.client.get(url_for("t_media.get_tmediasbyTaxon", cdref=67111))
        assert response.status_code == 200
        data = json_of_response(response)
        print(data)

    def test_get_tmediasbyType(self):
        response = self.client.get(url_for("t_media.get_tmediasbyType", type=1))
        assert response.status_code == 200
        data = json_of_response(response)
        print(data)

        response = self.client.get(url_for("t_media.get_tmediasbyType", type=2))
        assert response.status_code == 200
        data = json_of_response(response)
        print(data)

    def test_get_get_tmedias(self):
        response = self.client.get(url_for("t_media.get_tmedias"))
        assert response.status_code == 200
        response = self.client.get(url_for("t_media.get_tmedias", id=1))
        assert response.status_code == 200
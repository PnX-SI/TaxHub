import pytest
from flask import url_for

DEFAULT_STATUS_SYMBOLOGY = {
    "symbologies": [
        {
            "types": ["LRM", "LRE", "LRN", "LRR"],
            "values": {
                "EX": {"color": "#000000"},
                "EW": {"color": "#3d1951"},
                "RE": {"color": "#5a1a63"},
                "CR": {"color": "#d3001b"},
                "EN": {"color": "#fbbf00"},
                "VU": {"color": "#ffed00"},
                "NT": {"color": "#fbf2ca"},
                "LC": {"color": "#78b74a"},
                "DD": {"color": "#d3d4d5"},
                "NA": {"color": "#919291"},
                "NE": {"color": "#ffffff"},
            },
        }
    ]
}


@pytest.mark.usefixtures("client_class")
class TestApiBdcStatus:
    def test_status_symbologies(self):
        response = self.client.get(
            url_for("bdc_status.get_status_symbologies"),
        )
        assert response.status_code == 200
        assert response.json == DEFAULT_STATUS_SYMBOLOGY

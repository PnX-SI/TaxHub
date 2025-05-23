taxhub_api_routes = [
    ("apptax.taxonomie.routesbibnoms:adresses", "/bibnoms"),
    ("apptax.taxonomie.routestaxref:adresses", "/taxref"),
    ("apptax.taxonomie.routesbibattributs:adresses", "/bibattributs"),
    ("apptax.taxonomie.routesbiblistes:adresses", "/biblistes"),
    ("apptax.taxonomie.routestmedias:adresses", "/tmedias"),
    ("apptax.taxonomie.routesbdcstatuts:adresses", "/bdc_statuts"),
]

from PIL import Image, __version__
from pkg_resources import parse_version

if parse_version(__version__) >= parse_version("10.0.0"):
    Image.ANTIALIAS = Image.LANCZOS

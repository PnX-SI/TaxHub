from PIL import Image, __version__
from packaging.version import Version

taxhub_api_routes = [
    ("apptax.taxonomie.routesbibnoms:adresses", "/bibnoms"),
    ("apptax.taxonomie.routestaxref:adresses", "/taxref"),
    ("apptax.taxonomie.routesbibattributs:adresses", "/bibattributs"),
    ("apptax.taxonomie.routesbiblistes:adresses", "/biblistes"),
    ("apptax.taxonomie.routestmedias:adresses", "/tmedias"),
    ("apptax.taxonomie.routesbdcstatuts:adresses", "/bdc_statuts"),
]

# HACK: Remove when the new release of flask-admin is out
# Source: https://stackoverflow.com/a/77236546/5807438
if Version(__version__) >= Version("9.50.0"):
    Image.ANTIALIAS = Image.LANCZOS

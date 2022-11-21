import setuptools
from pathlib import Path


root_dir = Path(__file__).absolute().parent
with (root_dir / "VERSION").open() as f:
    version = f.read()
with (root_dir / "README.rst").open() as f:
    long_description = f.read()


setuptools.setup(
    name="taxhub",
    description="Application web de gestion centralisée des taxons basée sur le référentiel TAXREF",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    maintainer="Parcs nationaux des Écrins et des Cévennes",
    maintainer_email="geonature@ecrins-parcnational.fr",
    url="https://github.com/PnX-SI/TaxHub",
    version=version,
    packages=setuptools.find_packages(where=".", include=["apptax*"]),
    package_data={
        "apptax": ["templates/*.html"],
        "apptax.migrations": ["alembic.ini", "script.py.mako", "data/*.sql"],
        "apptax.taxonomie.commands.migrate_to_v15": ["data/*.sql"],
    },
    install_requires=(
        list(open("requirements-common.in", "r")) + list(open("requirements-dependencies.in", "r"))
    ),
    entry_points={
        "alembic": [
            "migrations = apptax.migrations:versions",
        ],
        "flask.commands": [
            "taxref = apptax.taxonomie.commands.taxref:taxref",
        ],
    },
    extras_require={
        "tests": [
            "pytest",
            "pytest-flask",
            "pytest-cov",
            "schema",
        ],
    },
)

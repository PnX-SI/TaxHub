import setuptools
from pathlib import Path


root_dir = Path(__file__).absolute().parent
with (root_dir / 'VERSION').open() as f:
    version = f.read()
with (root_dir / 'README.rst').open() as f:
    long_description = f.read()
with (root_dir / 'requirements.in').open() as f:
    requirements = f.read().splitlines()


setuptools.setup(
    name='taxhub',
    description='Application web de gestion centralisée des taxons basée sur le référentiel TAXREF',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    maintainer='Parcs nationaux des Écrins et des Cévennes',
    maintainer_email='geonature@ecrins-parcnational.fr',
    url='https://github.com/PnX-SI/TaxHub',
    version=version,
    packages=setuptools.find_packages(where='.', include=['apptax*']),
    package_data={'apptax.migrations': ['data/*.sql']},
    install_requires=requirements,
    entry_points={
        'alembic': [
            'migrations = apptax.migrations:versions',
        ],
    },
)

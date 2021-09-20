"""taxonomie schema 1.8.1

Revision ID: 9c2c0254aadc
Revises: fa35dfe5ff27
Create Date: 2021-08-24 16:02:01.413557

"""

import importlib.resources
from alembic import op


# revision identifiers, used by Alembic.
revision = '9c2c0254aadc'
down_revision = None
branch_labels = ('taxonomie',)
depends_on = (
    '72f227e37bdf',  # utilisateurs schema 1.4.7 avec données exemple
)

SELECT_TH_ID_APP = "SELECT id_application FROM utilisateurs.t_applications WHERE code_application = 'TH'"

def upgrade():

    # Création du schéma taxonomie et de sa strucutre
    # Ajout des données de userhub nécéssaire au fonctionnement
    op.execute(importlib.resources.read_text('apptax.migrations.data', 'taxhubdb.sql'))
    op.execute(f"""
        -- Insérer les applications de base liées à TaxHub
        INSERT INTO utilisateurs.t_applications (code_application, nom_application, desc_application, id_parent) VALUES
        ('TH', 'TaxHub', 'Application permettant d''administrer les taxons.', NULL)
        ;

        --Définir les profils utilisables pour TaxHub
        INSERT INTO utilisateurs.cor_profil_for_app (id_profil, id_application) VALUES
        (
            (SELECT id_profil FROM utilisateurs.t_profils WHERE code_profil = '2'),
            ({SELECT_TH_ID_APP})
        ),(
            (SELECT id_profil FROM utilisateurs.t_profils WHERE code_profil = '3'),
            ({SELECT_TH_ID_APP})
        ),(
            (SELECT id_profil FROM utilisateurs.t_profils WHERE code_profil = '4'),
            ({SELECT_TH_ID_APP})
        ),(
            (SELECT id_profil FROM utilisateurs.t_profils WHERE code_profil = '6'),
            ({SELECT_TH_ID_APP})
        )
        ;

        INSERT INTO utilisateurs.cor_role_app_profil (id_role, id_application, id_profil) VALUES
        (
            (SELECT id_role FROM utilisateurs.t_roles WHERE nom_role = 'Grp_admin'),
            ({SELECT_TH_ID_APP}),
            (SELECT id_profil FROM utilisateurs.t_profils WHERE code_profil = '6')
        )
        ;

    """)

def downgrade():
    # Suppression données applications dans usershubs
    op.execute(f"""
        DELETE FROM utilisateurs.cor_profil_for_app
            WHERE id_application = ({SELECT_TH_ID_APP});

        DELETE FROM utilisateurs.cor_role_app_profil
            WHERE id_application = ({SELECT_TH_ID_APP});

        DELETE FROM utilisateurs.t_applications WHERE code_application = 'TH';
    """)
    # Suppression schéma taxonomie
    op.execute("""
    DROP SCHEMA taxonomie CASCADE;
    """)
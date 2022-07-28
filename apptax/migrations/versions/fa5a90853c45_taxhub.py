"""taxhub

Revision ID: fa5a90853c45
Create Date: 2021-09-21 17:12:54.787812

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "fa5a90853c45"
down_revision = None
branch_labels = ("taxhub",)
depends_on = ("fa35dfe5ff27",)  # schema utilisateurs


def upgrade():
    op.execute(
        """
    INSERT INTO utilisateurs.t_applications (
        code_application,
        nom_application,
        desc_application,
        id_parent)
    VALUES (
        'TH',
        'TaxHub',
        'Application permettant d''administrer les taxons.',
        NULL)
    """
    )
    op.execute(
        """
    INSERT INTO utilisateurs.cor_profil_for_app
        (id_profil, id_application)
    VALUES
        (
            (SELECT id_profil FROM utilisateurs.t_profils WHERE code_profil = '2'),
            (SELECT id_application FROM utilisateurs.t_applications WHERE code_application = 'TH')
        ), (
            (SELECT id_profil FROM utilisateurs.t_profils WHERE code_profil = '3'),
            (SELECT id_application FROM utilisateurs.t_applications WHERE code_application = 'TH')
        ), (
            (SELECT id_profil FROM utilisateurs.t_profils WHERE code_profil = '4'),
            (SELECT id_application FROM utilisateurs.t_applications WHERE code_application = 'TH')
        ), (
            (SELECT id_profil FROM utilisateurs.t_profils WHERE code_profil = '6'),
            (SELECT id_application FROM utilisateurs.t_applications WHERE code_application = 'TH')
        )
    """
    )


def downgrade():
    op.execute(
        """
    DELETE FROM utilisateurs.cor_profil_for_app cor
    USING utilisateurs.t_applications app
    WHERE cor.id_application = app.id_application
    AND app.code_application = 'TH'
    """
    )
    op.execute("DELETE FROM utilisateurs.t_applications WHERE code_application = 'TH'")

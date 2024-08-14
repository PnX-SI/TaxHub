"""Remove code_profil 3, 4

Revision ID: 1f7b958108ed
Revises: 64d38dbe7739
Create Date: 2024-08-14 12:13:46.319115

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "1f7b958108ed"
down_revision = "64d38dbe7739"
branch_labels = None
depends_on = None


def upgrade():
    # Mise à jour des droits utilisateurs
    op.execute(
        """
        UPDATE utilisateurs.cor_role_app_profil cor SET id_profil = (SELECT id_profil FROM utilisateurs.t_profils WHERE code_profil = '2' LIMIT 1)
        FROM utilisateurs.t_applications app
        WHERE cor.id_application = app.id_application AND app.code_application = 'TH'
            AND id_profil IN (SELECT id_profil FROM utilisateurs.t_profils WHERE code_profil IN ('3', '4')) 
            AND NOT EXISTS (
                SELECT 1 
                FROM utilisateurs.cor_role_app_profil cor, utilisateurs.t_applications app
                WHERE cor.id_application = app.id_application AND app.code_application = 'TH'
                AND id_profil = (SELECT id_profil FROM utilisateurs.t_profils WHERE code_profil = '2' LIMIT 1)
            )
        """
    )
    # Suppression des profils
    op.execute(
        """
        DELETE FROM utilisateurs.cor_profil_for_app cor
        USING utilisateurs.t_applications app
        WHERE cor.id_application = app.id_application
            AND app.code_application = 'TH'
            AND id_profil IN (SELECT id_profil FROM utilisateurs.t_profils WHERE code_profil IN ('3', '4'));
        """
    )


def downgrade():

    op.execute(
        """
        INSERT INTO utilisateurs.cor_profil_for_app
                (id_profil, id_application)
            VALUES
                (
                    (SELECT id_profil FROM utilisateurs.t_profils WHERE code_profil = '3'),
                    (SELECT id_application FROM utilisateurs.t_applications WHERE code_application = 'TH')
                ), (
                    (SELECT id_profil FROM utilisateurs.t_profils WHERE code_profil = '4'),
                    (SELECT id_application FROM utilisateurs.t_applications WHERE code_application = 'TH')
                ) 
        """
    )

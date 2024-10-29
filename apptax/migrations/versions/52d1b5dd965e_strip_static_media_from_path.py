"""strip static/media from path

Revision ID: 52d1b5dd965e
Revises: 8f3256f60915
Create Date: 2023-11-16 11:05:15.752660

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "52d1b5dd965e"
down_revision = "a982df406ae8"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        UPDATE
            taxonomie.t_medias
        SET
            chemin = regexp_replace(chemin, '^static/medias/', '')
        WHERE
            NULLIF(chemin, '') IS NOT NULL AND  NULLIF(url, '') IS NULL
        """
    )


def downgrade():
    pass
    op.execute(
        """
        UPDATE
            taxonomie.t_medias
        SET
            chemin = 'static/medias/' || chemin
        WHERE
            chemin IS NOT NULL AND url IS NULL
        """
    )

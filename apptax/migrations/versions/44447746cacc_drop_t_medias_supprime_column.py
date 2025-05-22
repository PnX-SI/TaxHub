"""drop t_medias.supprime column

Revision ID: 44447746cacc
Revises: b250cfcaab64
Create Date: 2023-08-04 14:04:28.235799

"""

import os
import shutil
from pathlib import Path
from flask import current_app
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import false


# revision identifiers, used by Alembic.
revision = "44447746cacc"
down_revision = "b250cfcaab64"
branch_labels = None
depends_on = None


def upgrade():
    # Suppression des fichiers médias
    conn = op.get_bind()
    res = conn.execute(
        """SELECT id_media, chemin 
        FROM taxonomie.t_medias
        WHERE NOT NULLIF(chemin , '') IS NULL AND  supprime = TRUE;"""
    )

    if "MEDIA_FOLDER" in current_app.config:
        media_path = Path(current_app.config["MEDIA_FOLDER"], "taxhub").absolute()
        for m in res:
            # Fichier principal
            try:
                os.remove(media_path / Path(m[1]))
            except FileNotFoundError:
                pass
            # Thumbnail
            try:
                shutil.rmtree(f"{media_path}/thumb/{m[0]}")
            except FileNotFoundError:
                pass

    # Suppression des enregistrements médias supprimés logiquement
    op.execute("DELETE FROM taxonomie.t_medias AS tm WHERE supprime = TRUE;")
    op.drop_column(table_name="t_medias", column_name="supprime", schema="taxonomie")


def downgrade():
    op.add_column(
        table_name="t_medias",
        column=sa.Column("supprime", sa.Boolean, nullable=False, server_default=false()),
        schema="taxonomie",
    )

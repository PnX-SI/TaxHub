"""drop t_medias.supprime column

Revision ID: 44447746cacc
Revises: 0db13d65cb27
Create Date: 2023-08-04 14:04:28.235799

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import false


# revision identifiers, used by Alembic.
revision = "44447746cacc"
down_revision = "0db13d65cb27"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("DELETE FROM taxonomie.t_medias AS tm WHERE supprime = TRUE;")
    op.drop_column(table_name="t_medias", column_name="supprime", schema="taxonomie")


def downgrade():
    op.add_column(
        table_name="t_medias",
        column=sa.Column("supprime", sa.Boolean, nullable=False, server_default=false()),
        schema="taxonomie",
    )

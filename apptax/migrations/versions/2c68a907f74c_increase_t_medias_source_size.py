"""increase t_medias.source size

Revision ID: 2c68a907f74c
Revises: 3c4762751898
Create Date: 2024-12-19 10:31:05.778720

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2c68a907f74c"
down_revision = "3c4762751898"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "t_medias", "source", type_=sa.Unicode(), existing_nullable=True, schema="taxonomie"
    )


def downgrade():
    op.alter_column(
        "t_medias",
        "source",
        type_=sa.VARCHAR(length=25),
        existing_nullable=True,
        schema="taxonomie",
    )

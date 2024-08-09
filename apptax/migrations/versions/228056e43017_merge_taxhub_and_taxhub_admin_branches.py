"""Merge taxhub and taxhub-admin branches

Revision ID: 228056e43017
Revises: 3fe8c07741be, 64d38dbe7739
Create Date: 2024-08-09 09:57:39.436982

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "228056e43017"
down_revision = ("3fe8c07741be", "64d38dbe7739")
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass

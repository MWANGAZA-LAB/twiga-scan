"""merge_heads

Revision ID: e02fecec72f6
Revises: add_performance_indexes, dfe1e478d48e
Create Date: 2025-11-24 09:09:46.545646+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e02fecec72f6'
down_revision = ('add_performance_indexes', 'dfe1e478d48e')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

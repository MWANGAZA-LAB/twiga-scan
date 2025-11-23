"""add duplicate detection fields

Revision ID: add_duplicate_detection
Revises: d498c24e9f66
Create Date: 2025-11-23

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_duplicate_detection'
down_revision = 'd498c24e9f66'
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns for duplicate detection
    op.add_column(
        'scan_logs',
        sa.Column('normalized_identifier', sa.String(500), nullable=True)
    )
    op.add_column(
        'scan_logs',
        sa.Column(
            'first_seen',
            sa.DateTime(timezone=True),
            nullable=True
        )
    )
    op.add_column(
        'scan_logs',
        sa.Column(
            'usage_count',
            sa.Integer(),
            nullable=False,
            server_default='1'
        )
    )
    
    # Create index on normalized_identifier for faster lookups
    op.create_index(
        'ix_scan_logs_normalized_identifier',
        'scan_logs',
        ['normalized_identifier']
    )


def downgrade():
    # Remove index
    op.drop_index('ix_scan_logs_normalized_identifier', 'scan_logs')
    
    # Remove columns
    op.drop_column('scan_logs', 'usage_count')
    op.drop_column('scan_logs', 'first_seen')
    op.drop_column('scan_logs', 'normalized_identifier')

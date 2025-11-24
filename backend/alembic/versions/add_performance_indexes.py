"""add performance indexes

Revision ID: add_performance_indexes
Revises: add_duplicate_detection
Create Date: 2025-11-24

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_performance_indexes'
down_revision = 'add_duplicate_detection'
branch_labels = None
depends_on = None


def upgrade():
    # Create indexes for scan_logs table to improve query performance
    op.create_index(
        'idx_scan_logs_timestamp',
        'scan_logs',
        ['timestamp'],
        postgresql_using='btree',
        postgresql_ops={'timestamp': 'DESC'}
    )
    op.create_index(
        'idx_scan_logs_content_type',
        'scan_logs',
        ['content_type']
    )
    op.create_index(
        'idx_scan_logs_auth_status',
        'scan_logs',
        ['auth_status']
    )
    op.create_index(
        'idx_scan_logs_device_id',
        'scan_logs',
        ['device_id'],
        postgresql_where=sa.text('device_id IS NOT NULL')
    )
    op.create_index(
        'idx_scan_logs_ip_address',
        'scan_logs',
        ['ip_address'],
        postgresql_where=sa.text('ip_address IS NOT NULL')
    )
    
    # Create indexes for providers table
    op.create_index(
        'idx_providers_provider_type',
        'providers',
        ['provider_type']
    )
    op.create_index(
        'idx_providers_status_active',
        'providers',
        ['status'],
        postgresql_where=sa.text('is_active = TRUE')
    )
    
    # Composite index for common queries
    op.create_index(
        'idx_scan_logs_timestamp_type',
        'scan_logs',
        ['timestamp', 'content_type']
    )


def downgrade():
    # Remove composite index
    op.drop_index('idx_scan_logs_timestamp_type', 'scan_logs')
    
    # Remove providers indexes
    op.drop_index('idx_providers_status_active', 'providers')
    op.drop_index('idx_providers_provider_type', 'providers')
    
    # Remove scan_logs indexes
    op.drop_index('idx_scan_logs_ip_address', 'scan_logs')
    op.drop_index('idx_scan_logs_device_id', 'scan_logs')
    op.drop_index('idx_scan_logs_auth_status', 'scan_logs')
    op.drop_index('idx_scan_logs_content_type', 'scan_logs')
    op.drop_index('idx_scan_logs_timestamp', 'scan_logs')

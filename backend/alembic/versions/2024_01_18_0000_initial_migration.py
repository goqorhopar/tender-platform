"""Initial migration - create all tables

Revision ID: 2024_01_18_0000
Revises: 
Create Date: 2024-01-18 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2024_01_18_0000'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enums
    user_role = postgresql.ENUM('admin', 'manager', 'user', 'viewer', name='userrole')
    user_role.create(op.get_bind())
    
    tender_status = postgresql.ENUM('draft', 'published', 'in_progress', 'completed', 'cancelled', 'archived', name='tenderstatus')
    tender_status.create(op.get_bind())
    
    tender_type = postgresql.ENUM('government', 'commercial', 'international', name='tendertype')
    tender_type.create(op.get_bind())
    
    document_type = postgresql.ENUM('technical_spec', 'commercial_proposal', 'contract', 'addendum', 'other', name='documenttype')
    document_type.create(op.get_bind())

    # Users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, default=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('company_name', sa.String(length=255), nullable=True),
        sa.Column('inn', sa.String(length=12), nullable=True),
        sa.Column('role', postgresql.ENUM(name='userrole'), nullable=False, default='user'),
        sa.Column('preferences', postgresql.JSONB(astext_type=sa.Text()), nullable=True, default=dict),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('failed_login_attempts', sa.Integer(), nullable=False, default=0),
        sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, default=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_users_email', 'users', ['email'], unique=True)
    op.create_index('idx_users_email_active', 'users', ['email', 'is_active'])
    op.create_index('idx_users_role', 'users', ['role'])

    # Tenders table
    op.create_table('tenders',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('tender_number', sa.String(length=100), nullable=False),
        sa.Column('type', postgresql.ENUM(name='tendertype'), nullable=False, default='commercial'),
        sa.Column('status', postgresql.ENUM(name='tenderstatus'), nullable=False, default='draft'),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('okpd2_codes', postgresql.JSONB(astext_type=sa.Text()), nullable=True, default=list),
        sa.Column('initial_price', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False, default='RUB'),
        sa.Column('publication_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('submission_deadline', sa.DateTime(timezone=True), nullable=True),
        sa.Column('review_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('customer_name', sa.String(length=500), nullable=True),
        sa.Column('customer_inn', sa.String(length=12), nullable=True),
        sa.Column('customer_region', sa.String(length=100), nullable=True),
        sa.Column('documents_url', sa.String(length=1000), nullable=True),
        sa.Column('technical_spec_url', sa.String(length=1000), nullable=True),
        sa.Column('ai_summary', sa.Text(), nullable=True),
        sa.Column('ai_risk_score', sa.Float(), nullable=True),
        sa.Column('ai_recommendations', postgresql.JSONB(astext_type=sa.Text()), nullable=True, default=list),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('assigned_to_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('search_vector', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, default=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['assigned_to_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_tenders_tender_number', 'tenders', ['tender_number'], unique=True)
    op.create_index('idx_tenders_status', 'tenders', ['status'])
    op.create_index('idx_tenders_status_deadline', 'tenders', ['status', 'submission_deadline'])
    op.create_index('idx_tenders_price', 'tenders', ['initial_price'])
    op.create_index('idx_tenders_customer_inn', 'tenders', ['customer_inn'])

    # Tender documents table
    op.create_table('tender_documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tender_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('file_type', postgresql.ENUM(name='documenttype'), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('storage_path', sa.String(length=1000), nullable=False),
        sa.Column('s3_key', sa.String(length=500), nullable=True),
        sa.Column('uploaded_by_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('checksum', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['tender_id'], ['tenders.id'], ),
        sa.ForeignKeyConstraint(['uploaded_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_tender_documents_tender_id', 'tender_documents', ['tender_id'])
    op.create_index('idx_tender_documents_file_type', 'tender_documents', ['file_type'])

    # Tender comments table
    op.create_table('tender_comments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tender_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('parent_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('is_edited', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['tender_id'], ['tenders.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['parent_id'], ['tender_comments.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_tender_comments_tender_id', 'tender_comments', ['tender_id'])
    op.create_index('idx_tender_comments_user_id', 'tender_comments', ['user_id'])

    # Favorite tenders table
    op.create_table('favorite_tenders',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tender_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['tender_id'], ['tenders.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'tender_id', name='uq_favorite_tenders_user_tender')
    )
    op.create_index('idx_favorite_tenders_user_id', 'favorite_tenders', ['user_id'])

    # Audit logs table
    op.create_table('audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('resource_type', sa.String(length=100), nullable=False),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('old_values', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('new_values', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_audit_logs_timestamp', 'audit_logs', ['timestamp'])
    op.create_index('idx_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('idx_audit_logs_timestamp_action', 'audit_logs', ['timestamp', 'action'])
    op.create_index('idx_audit_logs_resource', 'audit_logs', ['resource_type', 'resource_id'])


def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('favorite_tenders')
    op.drop_table('tender_comments')
    op.drop_table('tender_documents')
    op.drop_table('tenders')
    op.drop_table('users')
    
    # Drop enums
    sa.Enum(name='userrole').drop(op.get_bind())
    sa.Enum(name='tenderstatus').drop(op.get_bind())
    sa.Enum(name='tendertype').drop(op.get_bind())
    sa.Enum(name='documenttype').drop(op.get_bind())

"""Initial migration

Revision ID: 001
Revises:
Create Date: 2026-03-12

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('company', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('is_trial', sa.Boolean(), nullable=True, default=True),
        sa.Column('trial_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Create guides table
    op.create_table(
        'guides',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('target_url', sa.String(), nullable=False),
        sa.Column('config', postgresql.JSON(astext_type=sa.Text()), nullable=False, default={}),
        sa.Column('is_published', sa.Boolean(), nullable=True, default=False),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_guides_id'), 'guides', ['id'], unique=False)

    # Create steps table
    op.create_table(
        'steps',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('guide_id', sa.Integer(), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('element_selector', sa.String(), nullable=False),
        sa.Column('position', sa.String(), nullable=True, default='bottom'),
        sa.Column('config', postgresql.JSON(astext_type=sa.Text()), nullable=False, default={}),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['guide_id'], ['guides.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_steps_id'), 'steps', ['id'], unique=False)

    # Create page_analyses table
    op.create_table(
        'page_analyses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('html_content', sa.Text(), nullable=True),
        sa.Column('analysis_result', postgresql.JSON(astext_type=sa.Text()), nullable=False, default={}),
        sa.Column('suggested_elements', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_page_analyses_id'), 'page_analyses', ['id'], unique=False)

    # Create usage_logs table
    op.create_table(
        'usage_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('details', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_usage_logs_id'), 'usage_logs', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_usage_logs_id'), table_name='usage_logs')
    op.drop_table('usage_logs')
    op.drop_index(op.f('ix_page_analyses_id'), table_name='page_analyses')
    op.drop_table('page_analyses')
    op.drop_index(op.f('ix_steps_id'), table_name='steps')
    op.drop_table('steps')
    op.drop_index(op.f('ix_guides_id'), table_name='guides')
    op.drop_table('guides')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')

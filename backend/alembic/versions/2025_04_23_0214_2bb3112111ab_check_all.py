"""Synchronize schema with models

Revision ID: 2bb3112111ab
Revises: 24f06da2a916
Create Date: 2025-04-23 02:14:34.116386
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '2bb3112111ab'
down_revision = '24f06da2a916'
branch_labels = None
depends_on = None

def upgrade():
    # categories
    op.alter_column('categories', 'name', existing_type=sa.VARCHAR(), nullable=True)
    op.create_index(op.f('ix_categories_id'), 'categories', ['id'], unique=False)

    # company_items
    op.alter_column('company_items', 'identifier', existing_type=sa.VARCHAR(), nullable=True)
    op.alter_column('company_items', 'unit_id', existing_type=sa.INTEGER(), nullable=False)
    op.alter_column('company_items', 'rrprice', existing_type=sa.DOUBLE_PRECISION(precision=53), nullable=False)
    op.drop_index('ix_company_items_identifier', table_name='company_items')

    # stock_history
    op.add_column('stock_history', sa.Column('recorded_at', sa.DateTime(), nullable=True))
    op.alter_column('stock_history', 'company_item_id', existing_type=sa.INTEGER(), nullable=True)
    op.alter_column('stock_history', 'stock', existing_type=sa.INTEGER(), nullable=True)
    op.create_index(op.f('ix_stock_history_company_item_id'), 'stock_history', ['company_item_id'], unique=False)
    op.create_index(op.f('ix_stock_history_id'), 'stock_history', ['id'], unique=False)
    op.drop_column('stock_history', 'created_at')

    # units
    op.alter_column('units', 'name', existing_type=sa.VARCHAR(length=50), nullable=False)

def downgrade():
    # units
    op.alter_column('units', 'name', existing_type=sa.VARCHAR(length=50), nullable=True)

    # stock_history
    op.add_column('stock_history', sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False))
    op.drop_index(op.f('ix_stock_history_id'), table_name='stock_history')
    op.drop_index(op.f('ix_stock_history_company_item_id'), table_name='stock_history')
    op.alter_column('stock_history', 'stock', existing_type=sa.INTEGER(), nullable=False)
    op.alter_column('stock_history', 'company_item_id', existing_type=sa.INTEGER(), nullable=False)
    op.drop_column('stock_history', 'recorded_at')

    # company_items
    op.create_index('ix_company_items_identifier', 'company_items', ['identifier'], unique=False)
    op.alter_column('company_items', 'rrprice', existing_type=sa.DOUBLE_PRECISION(precision=53), nullable=True)
    op.alter_column('company_items', 'unit_id', existing_type=sa.INTEGER(), nullable=True)
    op.alter_column('company_items', 'identifier', existing_type=sa.VARCHAR(), nullable=False)

    # categories
    op.drop_index(op.f('ix_categories_id'), table_name='categories')
    op.alter_column('categories', 'name', existing_type=sa.VARCHAR(), nullable=False)
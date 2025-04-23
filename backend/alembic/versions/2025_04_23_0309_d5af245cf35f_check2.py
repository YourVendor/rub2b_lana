"""Synchronize goods_categories, company_item_categories, price_history

Revision ID: d5af245cf35f
Revises: 91995699b44e
Create Date: 2025-04-23 03:09:05.865387
"""
from alembic import op
import sqlalchemy as sa

revision = 'd5af245cf35f'
down_revision = '91995699b44e'
branch_labels = None
depends_on = None

def upgrade():
    # goods_categories: Добавляем индекс для id
    op.create_index(op.f('ix_goods_categories_id'), 'goods_categories', ['id'], unique=False)

    # company_item_categories: Добавляем индекс для id
    op.create_index(op.f('ix_company_item_categories_id'), 'company_item_categories', ['id'], unique=False)

def downgrade():
    # company_item_categories
    op.drop_index(op.f('ix_company_item_categories_id'), table_name='company_item_categories')

    # goods_categories
    op.drop_index(op.f('ix_goods_categories_id'), table_name='goods_categories')
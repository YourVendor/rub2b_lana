"""Add missing tables including users

Revision ID: aadbb94e6051
Revises: 02a0c57328f3
Create Date: 2025-04-18 13:08:59.220993

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aadbb94e6051'
down_revision: Union[str, None] = '02a0c57328f3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('login', sa.String(length=50), nullable=True),
        sa.Column('password', sa.String(length=50), nullable=True),
        sa.Column('role', sa.String(length=20), server_default='retail_client', nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('login')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_login'), 'users', ['login'], unique=True)
    op.create_table('employee_companies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['parent_id'], ['categories.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('warehouses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('address', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('goods',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('ean13', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('price_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_item_id', sa.Integer(), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['company_item_id'], ['company_items.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('stock_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_item_id', sa.Integer(), nullable=False),
        sa.Column('stock', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['company_item_id'], ['company_items.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('company_item_categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_item_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id']),
        sa.ForeignKeyConstraint(['company_item_id'], ['company_items.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('goods_categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('goods_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id']),
        sa.ForeignKeyConstraint(['goods_id'], ['goods.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('queries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('query_text', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('queries')
    op.drop_table('goods_categories')
    op.drop_table('company_item_categories')
    op.drop_table('stock_history')
    op.drop_table('price_history')
    op.drop_table('goods')
    op.drop_table('warehouses')
    op.drop_table('categories')
    op.drop_table('employee_companies')
    op.drop_index(op.f('ix_users_login'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
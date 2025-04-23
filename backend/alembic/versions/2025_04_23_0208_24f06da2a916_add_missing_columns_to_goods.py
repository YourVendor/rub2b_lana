"""Add missing columns to goods

Revision ID: 24f06da2a916
Revises: f57712d11ccd
Create Date: 2025-04-23 02:08:33.203193
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '24f06da2a916'
down_revision = 'f57712d11ccd'
branch_labels = None
depends_on = None

def upgrade():
    # Добавляем недостающие столбцы в goods
    op.add_column('goods', sa.Column('unit_id', sa.Integer(), nullable=True))
    op.add_column('goods', sa.Column('description', sa.String(length=500), nullable=True))
    op.add_column('goods', sa.Column('category', sa.String(length=50), nullable=True))
    op.add_column('goods', sa.Column('stock', sa.Integer(), nullable=True, server_default='0'))
    # Добавляем foreign key для unit_id
    op.create_foreign_key(None, 'goods', 'units', ['unit_id'], ['id'])
    # Синхронизируем name с моделью (делаем nullable=True, если нужно)
    op.alter_column('goods', 'name', existing_type=sa.String(), nullable=True)

def downgrade():
    # Удаляем foreign key
    op.drop_constraint(None, 'goods', type_='foreignkey')
    # Удаляем добавленные столбцы
    op.drop_column('goods', 'stock')
    op.drop_column('goods', 'category')
    op.drop_column('goods', 'description')
    op.drop_column('goods', 'unit_id')
    # Возвращаем name к NOT NULL
    op.alter_column('goods', 'name', existing_type=sa.String(), nullable=False)
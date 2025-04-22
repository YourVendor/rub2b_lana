"""Add name, author, active to queries

Revision ID: <new_revision>
Revises: 6ed7e3ba8c81  # ID текущей ревизии (до применения 6aa17068a602)
Create Date: 2025-04-22 20:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '54152b5df198'
down_revision = '6ed7e3ba8c81'
branch_labels = None
depends_on = None

def upgrade():
    # Добавляем name, author, active
    op.add_column('queries', sa.Column('name', sa.String(100), nullable=True))
    op.add_column('queries', sa.Column('author', sa.String(50), nullable=True))
    op.add_column('queries', sa.Column('active', sa.Boolean(), nullable=True))

def downgrade():
    # Удаляем name, author, active
    op.drop_column('queries', 'active')
    op.drop_column('queries', 'author')
    op.drop_column('queries', 'name')
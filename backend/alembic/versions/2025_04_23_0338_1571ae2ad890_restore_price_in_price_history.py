"""Restore price in price_history

Revision ID: 1571ae2ad890
Revises: 203cf26e7c40
Create Date: 2025-04-23 03:38:10.618933

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1571ae2ad890'
down_revision: Union[str, None] = '203cf26e7c40'
branch_labels = None
depends_on = None

def upgrade():
    # price_history: Восстанавливаем столбец price
    op.add_column('price_history', sa.Column('price', sa.Float(), nullable=False))

def downgrade():
    # price_history: Удаляем столбец price
    op.drop_column('price_history', 'price')

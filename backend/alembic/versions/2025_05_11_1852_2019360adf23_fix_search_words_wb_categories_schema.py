"""fix_search_words_wb_categories_schema

Revision ID: 2019360adf23
Revises: 3dd1fdf2b394
Create Date: 2025-05-11 18:52:46.449870

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '2019360adf23'
down_revision: Union[str, None] = '3dd1fdf2b394'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""
    # Удаляем существующий составной первичный ключ
    op.drop_constraint('search_words_wb_categories_pkey', 'search_words_wb_categories', type_='primary')
    
    # Проверяем, существует ли столбец id, и добавляем его, если нет
    op.execute("""
        ALTER TABLE search_words_wb_categories
        ADD COLUMN IF NOT EXISTS id SERIAL PRIMARY KEY
    """)
    
    # Устанавливаем NOT NULL для search_words_wb_id и category_id
    op.alter_column('search_words_wb_categories', 'search_words_wb_id', nullable=False)
    op.alter_column('search_words_wb_categories', 'category_id', nullable=False)

def downgrade() -> None:
    """Downgrade schema."""
    # Удаляем столбец id (если он был добавлен)
    op.drop_column('search_words_wb_categories', 'id')
    
    # Восстанавливаем составной первичный ключ
    op.create_primary_key(
        'search_words_wb_categories_pkey',
        'search_words_wb_categories',
        ['id', 'search_words_wb_id', 'category_id']
    )
    
    # Убираем NOT NULL, если нужно (опционально)
    op.alter_column('search_words_wb_categories', 'search_words_wb_id', nullable=True)
    op.alter_column('search_words_wb_categories', 'category_id', nullable=True)
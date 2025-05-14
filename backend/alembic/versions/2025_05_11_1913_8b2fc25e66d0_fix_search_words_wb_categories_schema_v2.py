"""fix_search_words_wb_categories_schema_v2

Revision ID: <новый_id>
Revises: 2019360adf23
Create Date: <дата>

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '<новый_id>'
down_revision: Union[str, None] = '2019360adf23'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""
    # Удаляем существующий столбец id, если он не PRIMARY KEY
    op.drop_column('search_words_wb_categories', 'id')
    
    # Добавляем новый столбец id как SERIAL PRIMARY KEY
    op.execute("""
        ALTER TABLE search_words_wb_categories
        ADD COLUMN id SERIAL PRIMARY KEY
    """)
    
    # Убедимся, что search_words_wb_id и category_id NOT NULL
    op.alter_column('search_words_wb_categories', 'search_words_wb_id', nullable=False)
    op.alter_column('search_words_wb_categories', 'category_id', nullable=False)

def downgrade() -> None:
    """Downgrade schema."""
    # Удаляем новый столбец id
    op.drop_column('search_words_wb_categories', 'id')
    
    # Восстанавливаем старый столбец id без PRIMARY KEY
    op.add_column(
        'search_words_wb_categories',
        sa.Column('id', sa.Integer, nullable=False)
    )
    
    # Убираем NOT NULL, если нужно
    op.alter_column('search_words_wb_categories', 'search_words_wb_id', nullable=True)
    op.alter_column('search_words_wb_categories', 'category_id', nullable=True)
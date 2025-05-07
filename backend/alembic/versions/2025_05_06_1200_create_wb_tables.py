"""Create WB-related tables

Revision ID: a1b2c3d4e5f6
Revises: 88e6ed2b0908
Create Date: 2025-05-06 12:00:00
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '88e6ed2b0908'
branch_labels = None
depends_on = None

def upgrade():
    # Create search_wb table
    op.create_table(
        'search_wb',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('text', sa.String(length=250), nullable=False),
        sa.Column('frequency_per_month', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_search_wb_id', 'id')
    )

    # Create competitors_wb table
    op.create_table(
        'competitors_wb',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('hyperlink', sa.String(length=500), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('img_competitors_wb', sa.String(length=20), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_competitors_wb_id', 'id')
    )

    # Create search_words_wb table
    op.create_table(
        'search_words_wb',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_search_words_wb_id', 'id')
    )

    # Create goods_wb table
    op.create_table(
        'goods_wb',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('article_our', sa.String(length=60), nullable=False),
        sa.Column('stock', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_goods_wb_id', 'id')
    )

    # Create search_wb_categories table
    op.create_table(
        'search_wb_categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('search_wb_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['search_wb_id'], ['search_wb.id'], ),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
        sa.PrimaryKeyConstraint('id', 'search_wb_id', 'category_id')
    )

    # Create search_wb_competitors table
    op.create_table(
        'search_wb_competitors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('search_wb_id', sa.Integer(), nullable=False),
        sa.Column('competitors_wb_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['search_wb_id'], ['search_wb.id'], ),
        sa.ForeignKeyConstraint(['competitors_wb_id'], ['competitors_wb.id'], ),
        sa.PrimaryKeyConstraint('id', 'search_wb_id', 'competitors_wb_id')
    )

    # Create competitors_wb_categories table
    op.create_table(
        'competitors_wb_categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('competitors_wb_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['competitors_wb_id'], ['competitors_wb.id'], ),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
        sa.PrimaryKeyConstraint('id', 'competitors_wb_id', 'category_id')
    )

    # Create search_words_wb_categories table
    op.create_table(
        'search_words_wb_categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('search_words_wb_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['search_words_wb_id'], ['search_words_wb.id'], ),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
        sa.PrimaryKeyConstraint('id', 'search_words_wb_id', 'category_id')
    )

    # Create goods_wb_goods table
    op.create_table(
        'goods_wb_goods',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('goods_wb_id', sa.Integer(), nullable=False),
        sa.Column('goods_ean13', sa.String(length=13), nullable=False),
        sa.ForeignKeyConstraint(['goods_wb_id'], ['goods_wb.id'], ),
        sa.ForeignKeyConstraint(['goods_ean13'], ['goods.ean13'], ),
        sa.PrimaryKeyConstraint('id', 'goods_wb_id', 'goods_ean13')
    )

def downgrade():
    op.drop_table('goods_wb_goods')
    op.drop_table('search_words_wb_categories')
    op.drop_table('competitors_wb_categories')
    op.drop_table('search_wb_competitors')
    op.drop_table('search_wb_categories')
    op.drop_table('goods_wb')
    op.drop_table('search_words_wb')
    op.drop_table('competitors_wb')
    op.drop_table('search_wb')
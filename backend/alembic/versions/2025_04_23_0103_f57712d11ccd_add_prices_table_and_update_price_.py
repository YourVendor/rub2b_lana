# backend/alembic/versions/2025_04_23_0103_f57712d11ccd_add_prices_table_and_update_price_.py
"""Add prices table and update price_history

Revision ID: f57712d11ccd
Revises: 54152b5df198
Create Date: 2025-04-23 01:03:48.949958
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f57712d11ccd'
down_revision = '54152b5df198'
branch_labels = None
depends_on = None

def upgrade():
    # Обновление goods_categories: замена goods_id на goods_ean13
    op.add_column('goods_categories', sa.Column('goods_ean13', sa.String(13), nullable=True))
    op.execute("""
        UPDATE goods_categories gc
        SET goods_ean13 = g.ean13
        FROM goods g
        WHERE gc.goods_id = g.id
    """)
    op.alter_column('goods_categories', 'goods_ean13', nullable=False)
    op.drop_constraint('goods_categories_goods_id_fkey', 'goods_categories', type_='foreignkey')
    op.drop_column('goods_categories', 'goods_id')

    # Обновление goods: делаем ean13 первичным ключом
    op.add_column('goods', sa.Column('ean13_new', sa.String(13), nullable=True))
    op.execute("UPDATE goods SET ean13_new = COALESCE(ean13, 'unknown_' || id::text)")
    op.alter_column('goods', 'ean13_new', nullable=False)
    op.drop_column('goods', 'ean13')
    op.drop_column('goods', 'id')
    op.alter_column('goods', 'ean13_new', new_column_name='ean13')
    op.create_primary_key('goods_pkey', 'goods', ['ean13'])
    op.create_index(op.f('ix_goods_ean13'), 'goods', ['ean13'], unique=True)
    op.create_foreign_key(None, 'goods_categories', 'goods', ['goods_ean13'], ['ean13'])

    # Создание таблицы prices
    op.create_table(
        'prices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('goods_ean13', sa.String(length=13), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('price_type', sa.String(length=20), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['goods_ean13'], ['goods.ean13']),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_prices_id'), 'prices', ['id'], unique=False)

    # Обновление price_history
    op.add_column('price_history', sa.Column('price_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'price_history', 'prices', ['price_id'], ['id'])
    op.add_column('price_history', sa.Column('price_type', sa.String(length=20), nullable=False, server_default='unknown'))
    # Переименовываем created_at в recorded_at, если created_at есть и recorded_at нет
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'price_history' AND column_name = 'created_at'
            ) AND NOT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'price_history' AND column_name = 'recorded_at'
            ) THEN
                ALTER TABLE price_history RENAME COLUMN created_at TO recorded_at;
            END IF;
        END $$;
    """)

def downgrade():
    # Откат price_history
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'price_history' AND column_name = 'recorded_at'
            ) AND NOT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'price_history' AND column_name = 'created_at'
            ) THEN
                ALTER TABLE price_history RENAME COLUMN recorded_at TO created_at;
            END IF;
        END $$;
    """)
    op.drop_column('price_history', 'price_type')
    op.drop_constraint(None, 'price_history', type_='foreignkey')
    op.drop_column('price_history', 'price_id')

    # Откат prices
    op.drop_index(op.f('ix_prices_id'), table_name='prices')
    op.drop_table('prices')

    # Откат goods
    op.add_column('goods', sa.Column('id', sa.Integer(), nullable=False))
    op.execute("UPDATE goods SET id = substring(ean13 from '[0-9]+')::integer WHERE ean13 ~ '^[0-9]+$';")
    op.add_column('goods', sa.Column('ean13_old', sa.String(), nullable=True))
    op.execute("UPDATE goods SET ean13_old = ean13")
    op.drop_index(op.f('ix_goods_ean13'), table_name='goods')
    op.drop_constraint('goods_pkey', 'goods', type_='primary')
    op.alter_column('goods', 'ean13', new_column_name='ean13_new')
    op.alter_column('goods', 'ean13_old', new_column_name='ean13')
    op.create_primary_key('goods_pkey', 'goods', ['id'])

    # Откат goods_categories
    op.drop_constraint(None, 'goods_categories', type_='foreignkey')
    op.add_column('goods_categories', sa.Column('goods_id', sa.Integer(), nullable=True))
    op.execute("""
        UPDATE goods_categories gc
        SET goods_id = g.id
        FROM goods g
        WHERE gc.goods_ean13 = g.ean13
    """)
    op.alter_column('goods_categories', 'goods_id', nullable=False)
    op.create_foreign_key('goods_categories_goods_id_fkey', 'goods_categories', 'goods', ['goods_id'], ['id'])
    op.drop_column('goods_categories', 'goods_ean13')
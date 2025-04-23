"""Fix price_history and other tables

Revision ID: 91995699b44e
Revises: 2bb3112111ab
Create Date: 2025-04-23 02:27:22.360144
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '91995699b44e'
down_revision = '2bb3112111ab'
branch_labels = None
depends_on = None

def upgrade():
    # price_history
    op.alter_column('price_history', 'price_id', existing_type=sa.Integer(), nullable=False)
    op.alter_column('price_history', 'recorded_at', existing_type=sa.DateTime(), nullable=True)
    op.create_index(op.f('ix_price_history_id'), 'price_history', ['id'], unique=False)

    # queries
    op.alter_column('queries', 'query_text', existing_type=sa.VARCHAR(), nullable=True)
    op.alter_column('queries', 'created_at', existing_type=postgresql.TIMESTAMP(), nullable=True)
    op.create_index(op.f('ix_queries_id'), 'queries', ['id'], unique=False)

    # warehouses
    op.add_column('warehouses', sa.Column('company_id', sa.Integer(), nullable=True))
    op.alter_column('warehouses', 'address', existing_type=sa.VARCHAR(), nullable=True)
    op.create_index(op.f('ix_warehouses_company_id'), 'warehouses', ['company_id'], unique=False)
    op.create_index(op.f('ix_warehouses_id'), 'warehouses', ['id'], unique=False)
    op.create_foreign_key(None, 'warehouses', 'companies', ['company_id'], ['id'])
    op.drop_column('warehouses', 'name')

    # users
    op.drop_constraint('users_login_key', 'users', type_='unique')

    # employee_companies
    op.create_index(op.f('ix_employee_companies_id'), 'employee_companies', ['id'], unique=False)

def downgrade():
    # employee_companies
    op.drop_index(op.f('ix_employee_companies_id'), table_name='employee_companies')

    # users
    op.create_unique_constraint('users_login_key', 'users', ['login'])

    # warehouses
    op.add_column('warehouses', sa.Column('name', sa.VARCHAR(), nullable=False))
    op.drop_constraint(None, 'warehouses', type_='foreignkey')
    op.drop_index(op.f('ix_warehouses_id'), table_name='warehouses')
    op.drop_index(op.f('ix_warehouses_company_id'), table_name='warehouses')
    op.alter_column('warehouses', 'address', existing_type=sa.VARCHAR(), nullable=False)
    op.drop_column('warehouses', 'company_id')

    # queries
    op.add_column('queries', sa.Column('active', sa.BOOLEAN(), nullable=True))
    op.drop_index(op.f('ix_queries_id'), table_name='queries')
    op.alter_column('queries', 'created_at', existing_type=postgresql.TIMESTAMP(), nullable=False)
    op.alter_column('queries', 'query_text', existing_type=sa.VARCHAR(), nullable=False)

    # price_history
    op.drop_index(op.f('ix_price_history_id'), table_name='price_history')
    op.alter_column('price_history', 'recorded_at', existing_type=sa.DateTime(), nullable=False)
    op.alter_column('price_history', 'price_id', existing_type=sa.Integer(), nullable=True)
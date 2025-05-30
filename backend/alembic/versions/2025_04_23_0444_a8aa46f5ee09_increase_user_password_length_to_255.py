"""Increase user password length to 255

Revision ID: a8aa46f5ee09
Revises: f82fe6f1b91c
Create Date: 2025-04-23 04:44:50.004520

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a8aa46f5ee09'
down_revision: Union[str, None] = 'f82fe6f1b91c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'password',
               existing_type=sa.VARCHAR(length=50),
               type_=sa.String(length=255),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'password',
               existing_type=sa.String(length=255),
               type_=sa.VARCHAR(length=50),
               existing_nullable=True)
    # ### end Alembic commands ###

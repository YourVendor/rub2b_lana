"""Sync company_items schema

Revision ID: 6ed7e3ba8c81
Revises: aadbb94e6051
Create Date: 2025-04-22 20:15:16.473599

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6ed7e3ba8c81'
down_revision: Union[str, None] = 'aadbb94e6051'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

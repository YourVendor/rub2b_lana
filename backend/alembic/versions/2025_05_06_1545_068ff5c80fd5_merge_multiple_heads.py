"""Merge multiple heads

Revision ID: 068ff5c80fd5
Revises: 88e6ed2b0908, a1b2c3d4e5f6
Create Date: 2025-05-06 15:45:10.705390

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '068ff5c80fd5'
down_revision: Union[str, None] = ('88e6ed2b0908', 'a1b2c3d4e5f6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

"""merge dashboard and alerts branches

Revision ID: f27db2f0feab
Revises: 1ccad690b339, 20260605_0004
Create Date: 2026-06-06 00:01:02.189684
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f27db2f0feab'
down_revision: Union[str, None] = '20260605_0004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

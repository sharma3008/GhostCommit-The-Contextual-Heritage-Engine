"""add version to rationale_summaries

Revision ID: 448299418594
Revises: a95cba69544d
Create Date: 2026-02-24 15:33:10.481575

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '448299418594'
down_revision: Union[str, Sequence[str], None] = 'a95cba69544d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

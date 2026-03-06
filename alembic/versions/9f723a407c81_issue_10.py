"""issue 10 ...

Revision ID: 9f723a407c81
Revises: 448299418594
Create Date: 2026-02-24 15:39:33.191556

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9f723a407c81'
down_revision: Union[str, Sequence[str], None] = '448299418594'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

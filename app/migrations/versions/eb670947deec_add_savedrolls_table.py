"""add SavedRolls table

Revision ID: eb670947deec
Revises: 00c06de477d8
Create Date: 2024-03-16 18:17:21.567789

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eb670947deec'
down_revision: Union[str, None] = '00c06de477d8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'savedroll',
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("scope", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("discord_id", sa.String(), nullable=False),
        sa.Column("dice_pool", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),

    )


def downgrade() -> None:
    op.drop_table('savedroll')

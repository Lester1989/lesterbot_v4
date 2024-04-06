"""id int to str

Revision ID: 3ddfd2d40d9c
Revises: e361e2a3dacb
Create Date: 2024-04-06 20:25:08.981689

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3ddfd2d40d9c'
down_revision: Union[str, None] = 'e361e2a3dacb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table("sheet_modifications")
    op.drop_table("rule_system_suggestions")
    op.drop_table("rule_system_rolls")
    op.drop_table("charactersheet_entries")
    op.drop_table("character_headers")
    op.drop_table("category_users")
    op.drop_table("category_settings")
    op.create_table(
        "category_settings",
        sa.Column("category_id", sa.String(), nullable=False),
        sa.Column("state", sa.Enum("CREATING", "STARTED", name="groupstate"), nullable=False),
        sa.Column("rule_system", sa.String(), nullable=False),
        sa.Column("changes_need_approval", sa.Boolean(), nullable=False),
        sa.Column("character_hidden", sa.Boolean(), nullable=False),
        sa.Column("hidden_rolls_allowed", sa.Boolean(), nullable=False),
        sa.Column("web_interface_enabled", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("category_id"),
    )
    op.create_table(
        "category_users",
        sa.Column("category_id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("is_gm", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("category_id", "user_id"),
    )
    op.create_table(
        "character_headers",
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("category_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("concept", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("image_url", sa.String(), nullable=False),
        sa.Column("is_inactive", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("user_id", "category_id", "name"),
    )
    op.create_table(
        "charactersheet_entries",
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("category_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("sheet_key", sa.String(), nullable=False),
        sa.Column("value", sa.Integer(), nullable=False),
        sa.Column(
            "attribute_type",
            sa.Enum("ATTRIBUTE", "SKILL", "SPECIALTY", "GENERAL", "UNKNOWN", name="attributetype"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("user_id", "category_id", "name", "sheet_key"),
    )
    op.create_table(
        "rule_system_rolls",
        sa.Column("rule_system", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("roll", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("rule_system", "name"),
    )
    op.create_table(
        "rule_system_suggestions",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("rule_system", sa.String(), nullable=False),
        sa.Column("suggested_key", sa.String(), nullable=False),
        sa.Column("suggested_value", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "sheet_modifications",
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("category_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("sheet_key", sa.String(), nullable=False),
        sa.Column("value", sa.Integer(), nullable=False),
        sa.Column(
            "attribute_type",
            sa.Enum("ATTRIBUTE", "SKILL", "SPECIALTY", "GENERAL", "UNKNOWN", name="attributetype"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("PENDING", "APPROVED", "REJECTED", name="modificationstate"),
            nullable=False,
        ),
        sa.Column("comment", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("user_id", "category_id", "name", "sheet_key"),
    )


def downgrade() -> None:
    op.create_table(
        "category_settings",
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("state", sa.Enum("CREATING", "STARTED", name="groupstate"), nullable=False),
        sa.Column("rule_system", sa.String(), nullable=False),
        sa.Column("changes_need_approval", sa.Boolean(), nullable=False),
        sa.Column("character_hidden", sa.Boolean(), nullable=False),
        sa.Column("hidden_rolls_allowed", sa.Boolean(), nullable=False),
        sa.Column("web_interface_enabled", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("category_id"),
    )
    op.create_table(
        "category_users",
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("is_gm", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("category_id", "user_id"),
    )
    op.create_table(
        "character_headers",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("concept", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("image_url", sa.String(), nullable=False),
        sa.Column("is_inactive", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("user_id", "category_id", "name"),
    )
    op.create_table(
        "charactersheet_entries",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("sheet_key", sa.String(), nullable=False),
        sa.Column("value", sa.Integer(), nullable=False),
        sa.Column(
            "attribute_type",
            sa.Enum("ATTRIBUTE", "SKILL", "SPECIALTY", "GENERAL", "UNKNOWN", name="attributetype"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("user_id", "category_id", "name", "sheet_key"),
    )
    op.create_table(
        "rule_system_rolls",
        sa.Column("rule_system", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("roll", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("rule_system", "name"),
    )
    op.create_table(
        "rule_system_suggestions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("rule_system", sa.String(), nullable=False),
        sa.Column("suggested_key", sa.String(), nullable=False),
        sa.Column("suggested_value", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "sheet_modifications",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("sheet_key", sa.String(), nullable=False),
        sa.Column("value", sa.Integer(), nullable=False),
        sa.Column(
            "attribute_type",
            sa.Enum("ATTRIBUTE", "SKILL", "SPECIALTY", "GENERAL", "UNKNOWN", name="attributetype"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("PENDING", "APPROVED", "REJECTED", name="modificationstate"),
            nullable=False,
        ),
        sa.Column("comment", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("user_id", "category_id", "name", "sheet_key"),
    )

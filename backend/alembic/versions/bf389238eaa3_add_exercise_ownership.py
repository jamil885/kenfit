"""add exercise ownership

Revision ID: bf389238eaa3
Revises: dac4af7ed78c
Create Date: 2026-09-28 18:35:53.406044

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bf389238eaa3'
down_revision: Union[str, Sequence[str], None] = 'dac4af7ed78c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # 1. Add owner_id
    op.add_column(
        "exercises",
        sa.Column(
            "owner_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    # 2. Add source temporarily as nullable
    op.add_column(
        "exercises",
        sa.Column(
            "source",
            sa.String(length=20),
            nullable=True,
        ),
    )

    # 3. Existing exercises become SYSTEM content
    op.execute(
        "UPDATE exercises SET source = 'SYSTEM' WHERE source IS NULL"
    )

    # 4. source is now safe to make NOT NULL
    op.alter_column(
        "exercises",
        "source",
        existing_type=sa.String(length=20),
        nullable=False,
    )

    # 5. owner index
    op.create_index(
        op.f("ix_exercises_owner_id"),
        "exercises",
        ["owner_id"],
        unique=False,
    )

    # 6. Named foreign key
    op.create_foreign_key(
        "fk_exercises_owner_id_users",
        "exercises",
        "users",
        ["owner_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        "fk_exercises_owner_id_users",
        "exercises",
        type_="foreignkey",
    )

    op.drop_index(
        op.f("ix_exercises_owner_id"),
        table_name="exercises",
    )

    op.drop_column(
        "exercises",
        "source",
    )

    op.drop_column(
        "exercises",
        "owner_id",
    )
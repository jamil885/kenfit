"""Account recovery and access-token invalidation."""

import sqlalchemy as sa

from alembic import op

revision = "b37a84d915c2"
down_revision = "9c4a10b2d7ef"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "users", sa.Column("token_version", sa.Integer(), nullable=False, server_default="0")
    )
    op.create_table(
        "password_resets",
        sa.Column("token_hash", sa.String(64), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_password_resets_user_id", "password_resets", ["user_id"])
    op.create_table(
        "auth_rate_limits",
        sa.Column("key", sa.String(64), primary_key=True),
        sa.Column("count", sa.Integer(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade():
    op.drop_table("auth_rate_limits")
    op.drop_table("password_resets")
    with op.batch_alter_table("users") as batch:
        batch.drop_column("token_version")

"""Preserve the PC training-session API alongside execution logs."""

import sqlalchemy as sa

from alembic import op

revision = "9c4a10b2d7ef"
down_revision = "82d6be1a904f"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "training_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("workout_id", sa.Integer(), sa.ForeignKey("workouts.id", ondelete="SET NULL")),
        sa.Column(
            "training_plan_id",
            sa.Integer(),
            sa.ForeignKey("training_plans.id", ondelete="SET NULL"),
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("notes", sa.Text()),
    )
    for field in ("id", "user_id", "workout_id", "training_plan_id"):
        op.create_index(f"ix_training_sessions_{field}", "training_sessions", [field])


def downgrade():
    op.drop_table("training_sessions")

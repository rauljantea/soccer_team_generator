"""Add index on soccer_power for leaderboard / analytics queries.

Revision ID: 0002_soccer_power_index
Revises: 0001_initial
Create Date: 2026-03-16
"""

from alembic import op

revision: str = "0002_soccer_power_index"
down_revision: str | None = "0001_initial"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade() -> None:
    op.create_index(
        "ix_teams_total_soccer_power",
        "teams",
        ["total_soccer_power"],
    )
    op.create_index(
        "ix_players_soccer_power",
        "players",
        ["soccer_power"],
    )


def downgrade() -> None:
    op.drop_index("ix_players_soccer_power", table_name="players")
    op.drop_index("ix_teams_total_soccer_power", table_name="teams")

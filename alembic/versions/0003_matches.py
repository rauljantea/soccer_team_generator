"""Add matches and match_events tables.

Revision ID: 0003_matches
Revises: 0002_soccer_power_index
Create Date: 2026-03-16
"""

from alembic import op
import sqlalchemy as sa

revision: str = "0003_matches"
down_revision: str | None = "0002_soccer_power_index"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "matches",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("home_team_id", sa.Integer(), nullable=False),
        sa.Column("away_team_id", sa.Integer(), nullable=False),
        sa.Column("home_score", sa.Integer(), nullable=False),
        sa.Column("away_score", sa.Integer(), nullable=False),
        sa.Column(
            "played_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["home_team_id"], ["teams.id"]),
        sa.ForeignKeyConstraint(["away_team_id"], ["teams.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_matches_home_team_id", "matches", ["home_team_id"])
    op.create_index("ix_matches_away_team_id", "matches", ["away_team_id"])

    op.create_table(
        "match_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("match_id", sa.Integer(), nullable=False),
        sa.Column("minute", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["match_id"], ["matches.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_match_events_match_id", "match_events", ["match_id"])


def downgrade() -> None:
    op.drop_index("ix_match_events_match_id", table_name="match_events")
    op.drop_table("match_events")
    op.drop_index("ix_matches_away_team_id", table_name="matches")
    op.drop_index("ix_matches_home_team_id", table_name="matches")
    op.drop_table("matches")

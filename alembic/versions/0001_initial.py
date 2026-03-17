"""Initial schema — teams and players tables.

Revision ID: 0001_initial
Revises: 
Create Date: 2026-03-16
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade() -> None:
    op.create_table(
        "teams",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("universe", sa.String(length=50), nullable=False),
        sa.Column("defenders", sa.Integer(), nullable=False),
        sa.Column("attackers", sa.Integer(), nullable=False),
        sa.Column("total_soccer_power", sa.Float(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_teams_universe", "teams", ["universe"])

    op.create_table(
        "players",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("team_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("height_cm", sa.Float(), nullable=False),
        sa.Column("weight_kg", sa.Float(), nullable=False),
        sa.Column("position", sa.String(length=20), nullable=False),
        sa.Column("universe", sa.String(length=50), nullable=False),
        sa.Column("soccer_power", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_players_team_id", "players", ["team_id"])


def downgrade() -> None:
    op.drop_index("ix_players_team_id", table_name="players")
    op.drop_table("players")
    op.drop_index("ix_teams_universe", table_name="teams")
    op.drop_table("teams")

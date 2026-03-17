"""
ORM models (persistence layer).
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class PlayerORM(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    team_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    height_cm: Mapped[float] = mapped_column(Float, nullable=False)
    weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    position: Mapped[str] = mapped_column(String(20), nullable=False)
    universe: Mapped[str] = mapped_column(String(50), nullable=False)
    soccer_power: Mapped[float] = mapped_column(Float, nullable=False)

    team: Mapped["TeamORM"] = relationship("TeamORM", back_populates="players")


class TeamORM(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    universe: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    defenders: Mapped[int] = mapped_column(Integer, nullable=False)
    attackers: Mapped[int] = mapped_column(Integer, nullable=False)
    total_soccer_power: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    players: Mapped[list["PlayerORM"]] = relationship(
        "PlayerORM", back_populates="team", cascade="all, delete-orphan"
    )

class MatchEventORM(Base):
    __tablename__ = "match_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    match_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("matches.id", ondelete="CASCADE"), nullable=False, index=True
    )
    minute: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)

    match: Mapped["MatchORM"] = relationship("MatchORM", back_populates="events")


class MatchORM(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    home_team_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("teams.id"), nullable=False, index=True
    )
    away_team_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("teams.id"), nullable=False, index=True
    )
    home_score: Mapped[int] = mapped_column(Integer, nullable=False)
    away_score: Mapped[int] = mapped_column(Integer, nullable=False)
    played_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    events: Mapped[list["MatchEventORM"]] = relationship(
        "MatchEventORM", back_populates="match", cascade="all, delete-orphan",
        order_by="MatchEventORM.minute"
    )

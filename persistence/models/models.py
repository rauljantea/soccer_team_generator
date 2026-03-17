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
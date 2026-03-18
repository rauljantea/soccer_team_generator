"""
Domain models

"""

from dataclasses import dataclass
from enum import Enum


class Position(str, Enum):
    GOALIE = "Goalie"
    DEFENCE = "Defence"
    OFFENCE = "Offence"


class Universe(str, Enum):
    STAR_WARS = "star_wars"
    POKEMON = "pokemon"
    BLADERUNNER = "bladerunner"


@dataclass(frozen=True)
class Player:
    name: str
    height_cm: float
    weight_kg: float
    universe: Universe
    position: Position | None = None

    @property
    def soccer_power(self) -> float:
        return round(self.height_cm * 0.4 + self.weight_kg * 0.6, 2)

    def with_position(self, position: Position) -> "Player":
        return Player(
            name=self.name,
            height_cm=self.height_cm,
            weight_kg=self.weight_kg,
            universe=self.universe,
            position=position,
        )


@dataclass(frozen=True)
class Lineup:
    TOTAL_PLAYERS: int = 5
    FIELD_PLAYERS: int = 4
    defenders: int = 2
    attackers: int = 2

    def __post_init__(self) -> None:
        if self.defenders + self.attackers != self.FIELD_PLAYERS:
            raise ValueError(
                f"defenders ({self.defenders}) + attackers ({self.attackers}) "
                f"must equal {self.FIELD_PLAYERS}"
            )
        if self.defenders < 1 or self.attackers < 1:
            raise ValueError("Must have at least 1 defender and 1 attacker")


@dataclass(frozen=True)
class Team:
    universe: Universe
    players: tuple[Player, ...]
    lineup: Lineup
    id: int | None = None

    def __post_init__(self) -> None:
        if len(self.players) != self.lineup.TOTAL_PLAYERS:
            raise ValueError(
                f"Team must have exactly {self.lineup.TOTAL_PLAYERS} players, "
                f"got {len(self.players)}"
            )
        positions = [p.position for p in self.players]
        if positions.count(Position.GOALIE) != 1:
            raise ValueError("Team must have exactly 1 goalie")
        if positions.count(Position.DEFENCE) != self.lineup.defenders:
            raise ValueError(f"Team must have exactly {self.lineup.defenders} defender(s)")
        if positions.count(Position.OFFENCE) != self.lineup.attackers:
            raise ValueError(f"Team must have exactly {self.lineup.attackers} attacker(s)")

    @property
    def total_soccer_power(self) -> float:
        return round(sum(p.soccer_power for p in self.players), 2)

    @property
    def goalie(self) -> Player:
        return next(p for p in self.players if p.position == Position.GOALIE)

    @property
    def defenders(self) -> tuple[Player, ...]:
        return tuple(p for p in self.players if p.position == Position.DEFENCE)

    @property
    def attackers(self) -> tuple[Player, ...]:
        return tuple(p for p in self.players if p.position == Position.OFFENCE)

@dataclass(frozen=True)
class MatchEvent:
    """A single commentary line from the match."""
    minute: int
    text: str


@dataclass(frozen=True)
class Match:
    home_team: Team
    away_team: Team
    home_score: int
    away_score: int
    events: tuple[MatchEvent, ...]
    id: int | None = None

"""Domain interfaces — abstract interfaces that define what the application needs."""

from abc import ABC, abstractmethod

from domain.models.models import Player, Team, Universe, Match


class UniverseInterface(ABC):
    @abstractmethod
    async def fetch_random_players(self, count: int) -> list[Player]:
        ...

    @property
    @abstractmethod
    def universe(self) -> Universe:
        ...


class TeamRepositoryInterface(ABC):
    @abstractmethod
    async def save(self, team: Team) -> int:
        ...

    @abstractmethod
    async def get_by_id(self, team_id: int) -> Team | None:
        ...

    @abstractmethod
    async def list_recent(self, limit: int = 20) -> list[Team]:
        ...

class MatchRepositoryInterface(ABC):
    @abstractmethod
    async def save(self, match: Match) -> int:
        ...

    @abstractmethod
    async def get_by_id(self, match_id: int) -> Match | None:
        ...

    @abstractmethod
    async def list_recent(self, limit: int = 20) -> list[Match]:
        ...
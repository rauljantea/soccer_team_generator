"""Application use case — PlayMatchUseCase."""

import logging

from domain.interfaces.interfaces import TeamRepositoryInterface, MatchRepositoryInterface
from domain.match_engine import MatchEngine
from domain.models.models import Match

logger = logging.getLogger(__name__)


class TeamNotFoundError(Exception):
    pass


class PlayMatchUseCase:
    def __init__(
            self,
            team_repository: TeamRepositoryInterface,
            match_repository: MatchRepositoryInterface,
            engine: MatchEngine | None = None,
    ) -> None:
        self._teams = team_repository
        self._matches = match_repository
        self._engine = engine or MatchEngine()

    async def execute(self, home_team_id: int, away_team_id: int) -> Match:
        home = await self._teams.get_by_id(home_team_id)
        if home is None:
            raise TeamNotFoundError(f"Team {home_team_id} not found")

        away = await self._teams.get_by_id(away_team_id)
        if away is None:
            raise TeamNotFoundError(f"Team {away_team_id} not found")

        logger.info("Simulating match: %s vs %s", home.universe, away.universe)
        match = self._engine.simulate(home, away)

        match_id = await self._matches.save(match)
        logger.info("Match %d saved", match_id)

        return match

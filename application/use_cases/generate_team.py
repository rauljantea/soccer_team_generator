"""Application use cases  — generate_team."""

import logging

from domain.models.models import Lineup, Team, Universe
from domain.interfaces.interfaces import TeamRepositoryInterface, UniverseInterface
from domain.team_assembler import TeamAssembler

logger = logging.getLogger(__name__)


class GenerateTeamUseCase:
    def __init__(
        self,
        universe_adapter: UniverseInterface,
        team_repository: TeamRepositoryInterface,
        assembler: TeamAssembler | None = None,
    ) -> None:
        self._adapter = universe_adapter
        self._repo = team_repository
        self._assembler = assembler or TeamAssembler()

    async def execute(self, lineup: Lineup) -> Team:
        logger.info("Fetching %d players from %s", lineup.TOTAL_PLAYERS, self._adapter.universe)
        players = await self._adapter.fetch_random_players(lineup.TOTAL_PLAYERS)
        team = self._assembler.assemble(players, self._adapter.universe, lineup)
        await self._repo.save(team)
        return team

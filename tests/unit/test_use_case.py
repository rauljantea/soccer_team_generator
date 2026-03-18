from unittest.mock import AsyncMock

import pytest

from application.use_cases.generate_team import GenerateTeamUseCase
from domain.models.models import Lineup, Player, Position, Universe
from domain.team_assembler import TeamAssembler


def _make_players():
    return [
        Player("Tall Terry", 200, 80, Universe.STAR_WARS),
        Player("Heavy Harry", 170, 120, Universe.STAR_WARS),
        Player("Beefy Bob", 175, 110, Universe.STAR_WARS),
        Player("Short Sam", 150, 60, Universe.STAR_WARS),
        Player("Petite Pat", 155, 65, Universe.STAR_WARS),
    ]


def _make_use_case():
    adapter = AsyncMock()
    adapter.universe = Universe.STAR_WARS
    adapter.fetch_random_players = AsyncMock(return_value=_make_players())

    repo = AsyncMock()
    repo.save = AsyncMock(return_value=1)

    return GenerateTeamUseCase(
        universe_adapter=adapter,
        team_repository=repo,
        assembler=TeamAssembler(),
    ), adapter, repo


class TestGenerateTeamUseCase:
    @pytest.mark.asyncio
    async def test_returns_assembled_team(self):
        uc, _, _ = _make_use_case()
        team = await uc.execute(Lineup())
        assert len(team.players) == 5

    @pytest.mark.asyncio
    async def test_persists_team(self):
        uc, _, repo = _make_use_case()
        await uc.execute(Lineup())
        repo.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_correct_positions_assigned(self):
        uc, _, _ = _make_use_case()
        team = await uc.execute(Lineup())
        positions = {p.position for p in team.players}
        assert Position.GOALIE in positions
        assert Position.DEFENCE in positions
        assert Position.OFFENCE in positions

    @pytest.mark.asyncio
    async def test_fetches_from_adapter(self):
        uc, adapter, _ = _make_use_case()
        await uc.execute(Lineup())
        adapter.fetch_random_players.assert_called_once_with(5)

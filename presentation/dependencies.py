from sqlalchemy.ext.asyncio import AsyncSession

from adapters.registry import registry
from application.use_cases.generate_team import GenerateTeamUseCase
from application.use_cases.play_match import PlayMatchUseCase
from domain.models.models import Universe
from persistence.repositories.repositories import (
    TeamRepository, MatchRepository,
)


def build_team_generator_use_case(universe: Universe, session: AsyncSession) -> GenerateTeamUseCase:
    adapter = registry.get(universe)
    repo = TeamRepository(session)
    return GenerateTeamUseCase(universe_adapter=adapter, team_repository=repo)


def build_play_match_use_case(session: AsyncSession) -> PlayMatchUseCase:
    return PlayMatchUseCase(
        team_repository=TeamRepository(session),
        match_repository=MatchRepository(session),
    )

"""Dependency injection — composition root."""

from sqlalchemy.ext.asyncio import AsyncSession

from adapters.pokemon import PokemonAdapter
from adapters.star_wars import StarWarsAdapter
from application.use_cases.generate_team import GenerateTeamUseCase
from application.use_cases.play_match import PlayMatchUseCase
from domain.models.models import Universe
from persistence.repositories.repositories import (
    SQLAlchemyTeamRepository, SQLAlchemyMatchRepository,
)


def build_use_case(universe: Universe, session: AsyncSession) -> GenerateTeamUseCase:
    adapter = StarWarsAdapter() if universe == Universe.STAR_WARS else PokemonAdapter()
    repo = SQLAlchemyTeamRepository(session)
    return GenerateTeamUseCase(universe_adapter=adapter, team_repository=repo)


def build_play_match_use_case(session: AsyncSession) -> PlayMatchUseCase:
    return PlayMatchUseCase(
        team_repository=SQLAlchemyTeamRepository(session),
        match_repository=SQLAlchemyMatchRepository(session),
    )

"""Dependency injection — composition root."""

from sqlalchemy.ext.asyncio import AsyncSession

from adapters.pokemon import PokemonAdapter
from application.use_cases.generate_team import GenerateTeamUseCase
from domain.models.models import Universe
from adapters.star_wars import StarWarsAdapter
from persistence.repositories.repositories import (
    SQLAlchemyTeamRepository,
)


def build_use_case(universe: Universe, session: AsyncSession) -> GenerateTeamUseCase:
    adapter = StarWarsAdapter() if universe == Universe.STAR_WARS else PokemonAdapter()
    repo = SQLAlchemyTeamRepository(session)
    return GenerateTeamUseCase(universe_adapter=adapter, team_repository=repo)


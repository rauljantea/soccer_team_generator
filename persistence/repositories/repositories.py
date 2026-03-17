"""SQLAlchemy implementations of repository interfaces."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from domain.interfaces.interfaces import TeamRepositoryInterface
from domain.models.models import Lineup, Player, Position, Team, Universe
from persistence.models.models import PlayerORM, TeamORM


class SQLAlchemyTeamRepository(TeamRepositoryInterface):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, team: Team) -> int:
        orm = TeamORM(
            universe=team.universe.value,
            defenders=team.lineup.defenders,
            attackers=team.lineup.attackers,
            total_soccer_power=team.total_soccer_power,
            players=[
                PlayerORM(
                    name=p.name,
                    height_cm=p.height_cm,
                    weight_kg=p.weight_kg,
                    position=p.position.value,
                    universe=p.universe.value,
                    soccer_power=p.soccer_power,
                )
                for p in team.players
            ],
        )
        self._session.add(orm)
        await self._session.flush()
        return orm.id

    async def get_by_id(self, team_id: int) -> Team | None:
        stmt = (
            select(TeamORM)
            .where(TeamORM.id == team_id)
            .options(selectinload(TeamORM.players))
        )
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def list_recent(self, limit: int = 20) -> list[Team]:
        stmt = (
            select(TeamORM)
            .order_by(TeamORM.created_at.desc())
            .limit(limit)
            .options(selectinload(TeamORM.players))
        )
        result = await self._session.execute(stmt)
        return [self._to_domain(row) for row in result.scalars()]

    @staticmethod
    def _to_domain(orm: TeamORM) -> Team:
        lineup = Lineup(defenders=orm.defenders, attackers=orm.attackers)
        players = tuple(
            Player(
                name=p.name,
                height_cm=p.height_cm,
                weight_kg=p.weight_kg,
                universe=Universe(p.universe),
                position=Position(p.position),
            )
            for p in orm.players
        )
        return Team(
            universe=Universe(orm.universe),
            players=players,
            lineup=lineup,
            id=orm.id,
        )

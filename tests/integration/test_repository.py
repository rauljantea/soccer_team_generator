import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from domain.models.models import Lineup, Player, Position, Universe
from domain.team_assembler import TeamAssembler
from persistence.models.models import Base
from persistence.repositories.repositories import TeamRepository

DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        async with s.begin():
            yield s
    await engine.dispose()


def _build_team():
    players = [
        Player("Tall Terry", 200, 80, Universe.STAR_WARS),
        Player("Heavy Harry", 170, 120, Universe.STAR_WARS),
        Player("Beefy Bob", 175, 110, Universe.STAR_WARS),
        Player("Short Sam", 150, 60, Universe.STAR_WARS),
        Player("Petite Pat", 155, 65, Universe.STAR_WARS),
    ]
    return TeamAssembler().assemble(players, Universe.STAR_WARS, Lineup())


class TestSQLAlchemyTeamRepository:
    @pytest.mark.asyncio
    async def test_save_and_get_by_id(self, session: AsyncSession):
        repo = TeamRepository(session)
        team = _build_team()
        team_id = await repo.save(team)

        assert isinstance(team_id, int)
        fetched = await repo.get_by_id(team_id)
        assert fetched is not None
        assert fetched.universe == Universe.STAR_WARS
        assert len(fetched.players) == 5

    @pytest.mark.asyncio
    async def test_total_soccer_power_preserved(self, session: AsyncSession):
        repo = TeamRepository(session)
        team = _build_team()
        team_id = await repo.save(team)
        fetched = await repo.get_by_id(team_id)
        assert fetched.total_soccer_power == team.total_soccer_power

    @pytest.mark.asyncio
    async def test_positions_preserved(self, session: AsyncSession):
        repo = TeamRepository(session)
        team = _build_team()
        team_id = await repo.save(team)
        fetched = await repo.get_by_id(team_id)
        positions = {p.position for p in fetched.players}
        assert Position.GOALIE in positions
        assert Position.DEFENCE in positions
        assert Position.OFFENCE in positions

    @pytest.mark.asyncio
    async def test_get_nonexistent_returns_none(self, session: AsyncSession):
        repo = TeamRepository(session)
        result = await repo.get_by_id(9999)
        assert result is None

    @pytest.mark.asyncio
    async def test_list_recent_ordering(self, session: AsyncSession):
        repo = TeamRepository(session)
        await repo.save(_build_team())
        await repo.save(_build_team())
        teams = await repo.list_recent(limit=10)
        assert len(teams) == 2

    @pytest.mark.asyncio
    async def test_lineup_preserved(self, session: AsyncSession):
        repo = TeamRepository(session)
        team = TeamAssembler().assemble(
            [
                Player("T1", 200, 80, Universe.STAR_WARS),
                Player("T2", 170, 120, Universe.STAR_WARS),
                Player("T3", 175, 110, Universe.STAR_WARS),
                Player("T4", 150, 60, Universe.STAR_WARS),
                Player("T5", 155, 65, Universe.STAR_WARS),
            ],
            Universe.STAR_WARS,
            Lineup(defenders=3, attackers=1),
        )
        team_id = await repo.save(team)
        fetched = await repo.get_by_id(team_id)
        assert fetched.lineup.defenders == 3
        assert fetched.lineup.attackers == 1

"""FastAPI routes — controllers."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import get_session
from domain.models.models import Lineup
from persistence.repositories.repositories import (
    SQLAlchemyTeamRepository,
)
from presentation.dependencies import build_use_case
from presentation.schemas.schemas import (
    GenerateTeamRequest,
    PlayerResponse,
    TeamResponse,
)

router = APIRouter(prefix="/api/v1", tags=["showdown"])


def _team_to_response(team) -> TeamResponse:
    return TeamResponse(
        id=team.id,
        universe=team.universe.value,
        lineup={"defenders": team.lineup.defenders, "attackers": team.lineup.attackers},
        players=[
            PlayerResponse(
                name=p.name,
                height_cm=p.height_cm,
                weight_kg=p.weight_kg,
                position=p.position.value,
                soccer_power=p.soccer_power,
            )
            for p in team.players
        ],
        total_soccer_power=team.total_soccer_power,
    )


@router.post("/teams/generate", response_model=TeamResponse, status_code=201)
async def generate_team(
        request: GenerateTeamRequest,
        session: AsyncSession = Depends(get_session),
) -> TeamResponse:
    try:
        lineup = Lineup(defenders=request.defenders, attackers=request.attackers)
        use_case = build_use_case(request.universe, session)
        team = await use_case.execute(lineup)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return _team_to_response(team)


@router.get("/teams", response_model=list[TeamResponse])
async def list_teams(
        limit: int = 20,
        session: AsyncSession = Depends(get_session),
) -> list[TeamResponse]:
    repo = SQLAlchemyTeamRepository(session)
    teams = await repo.list_recent(limit=limit)
    return [_team_to_response(t) for t in teams]


@router.get("/teams/{team_id}", response_model=TeamResponse)
async def get_team(
        team_id: int,
        session: AsyncSession = Depends(get_session),
) -> TeamResponse:
    repo = SQLAlchemyTeamRepository(session)
    team = await repo.get_by_id(team_id)
    if team is None:
        raise HTTPException(status_code=404, detail=f"Team {team_id} not found")
    return _team_to_response(team)

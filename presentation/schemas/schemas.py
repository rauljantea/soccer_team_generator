"""Schemas for the presentation layer."""

from pydantic import BaseModel, Field, field_validator

from domain.models.models import Universe


class GenerateTeamRequest(BaseModel):
    universe: Universe
    defenders: int = Field(default=2, ge=1, le=3)
    attackers: int = Field(default=2, ge=1, le=3)

    @field_validator("attackers")
    @classmethod
    def validate_total(cls, attackers: int, info) -> int:
        defenders = info.data.get("defenders", 2)
        if defenders + attackers != 4:
            raise ValueError(
                f"defenders ({defenders}) + attackers ({attackers}) must equal 4"
            )
        return attackers


class PlayerResponse(BaseModel):
    name: str
    height_cm: float
    weight_kg: float
    position: str
    soccer_power: float


class TeamResponse(BaseModel):
    id: int | None = None
    universe: str
    lineup: dict[str, int]
    players: list[PlayerResponse]
    total_soccer_power: float

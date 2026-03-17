"""Star Wars universe adapter.

Fetches characters from SWAPI (https://swapi.dev/api/people/).
Normalises units: SWAPI height is already in cm, mass in kg.
Unknown stats ('unknown') are filtered out before returning.
Uses tenacity for retry with exponential back-off.
"""

import asyncio
import logging
import random

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from domain.models.models import Player, Universe
from domain.interfaces.interfaces import UniverseInterface

logger = logging.getLogger(__name__)

_SWAPI_BASE = "https://swapi.dev/api"
_TOTAL_CHARACTERS = 82  # SWAPI people count as of writing


class StarWarsAdapter(UniverseInterface):
    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = client or httpx.AsyncClient(timeout=10.0)

    @property
    def universe(self) -> Universe:
        return Universe.STAR_WARS

    async def fetch_random_players(self, count: int) -> list[Player]:
        """Fetch `count` valid players (over-fetches to handle unknown stats)."""
        ids = random.sample(range(1, _TOTAL_CHARACTERS + 1), min(count + 10, _TOTAL_CHARACTERS))
        results = await asyncio.gather(
            *[self._fetch_one(i) for i in ids], return_exceptions=True
        )
        players = [r for r in results if isinstance(r, Player)]
        if len(players) < count:
            raise RuntimeError(
                f"Could not fetch {count} valid Star Wars players "
                f"(got {len(players)} with known stats)"
            )
        return players[:count]

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
        reraise=True,
    )
    async def _fetch_one(self, character_id: int) -> Player:
        url = f"{_SWAPI_BASE}/people/{character_id}/"
        response = await self._client.get(url)
        response.raise_for_status()
        data = response.json()

        height_raw = data.get("height", "unknown")
        mass_raw = data.get("mass", "unknown").replace(",", "")

        if height_raw == "unknown" or mass_raw == "unknown":
            raise ValueError(f"Unknown stats for character {character_id}")

        return Player(
            name=data["name"],
            height_cm=float(height_raw),
            weight_kg=float(mass_raw),
            universe=Universe.STAR_WARS,
        )

    async def close(self) -> None:
        await self._client.aclose()

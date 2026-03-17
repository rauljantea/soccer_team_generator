"""Pokémon universe adapter.

Fetches Pokémon from PokéAPI (https://pokeapi.co/api/v2/pokemon/).
Unit conversion:
  height: PokéAPI returns decimetres  → multiply by 10 for cm
  weight: PokéAPI returns hectograms  → divide by 10 for kg

Resilience:
  - Retry with exponential back-off via tenacity
  - Falls back to a small seeded dataset when the upstream is unhealthy
    (circuit-breaker pattern: tracked via consecutive failure counter)
"""

import asyncio
import logging
import random

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from domain.models.models import Player, Universe
from domain.interfaces.interfaces import UniverseInterface

logger = logging.getLogger(__name__)

_POKEAPI_BASE = "https://pokeapi.co/api/v2"
_TOTAL_POKEMON = 151  # Gen 1 only — extend as desired

# Seeded fallback dataset for resilience when PokéAPI is down
_FALLBACK_POKEMON: list[dict] = [
    {"name": "bulbasaur", "height_cm": 70, "weight_kg": 6.9},
    {"name": "charmander", "height_cm": 60, "weight_kg": 8.5},
    {"name": "squirtle", "height_cm": 50, "weight_kg": 9.0},
    {"name": "pikachu", "height_cm": 40, "weight_kg": 6.0},
    {"name": "mewtwo", "height_cm": 200, "weight_kg": 122.0},
    {"name": "snorlax", "height_cm": 210, "weight_kg": 460.0},
    {"name": "gengar", "height_cm": 150, "weight_kg": 40.5},
    {"name": "machamp", "height_cm": 160, "weight_kg": 130.0},
    {"name": "dragonite", "height_cm": 220, "weight_kg": 210.0},
    {"name": "alakazam", "height_cm": 150, "weight_kg": 48.0},
]

_CIRCUIT_THRESHOLD = 5  # failures before switching to fallback


class PokemonAdapter(UniverseInterface):
    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = client or httpx.AsyncClient(timeout=10.0)
        self._consecutive_failures = 0

    @property
    def universe(self) -> Universe:
        return Universe.POKEMON

    async def fetch_random_players(self, count: int) -> list[Player]:
        if self._consecutive_failures >= _CIRCUIT_THRESHOLD:
            logger.warning("PokéAPI circuit open — serving fallback dataset")
            return self._fallback_players(count)

        ids = random.sample(range(1, _TOTAL_POKEMON + 1), min(count + 5, _TOTAL_POKEMON))
        results = await asyncio.gather(
            *[self._fetch_one(i) for i in ids], return_exceptions=True
        )
        players = [r for r in results if isinstance(r, Player)]

        if len(players) < count:
            self._consecutive_failures += 1
            logger.warning(
                "PokéAPI returned only %d valid players (need %d), failure count: %d",
                len(players), count, self._consecutive_failures,
            )
            # Supplement from fallback
            fallback = self._fallback_players(count - len(players))
            players.extend(fallback)
        else:
            self._consecutive_failures = 0  # reset on success

        return players[:count]

    @retry(
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
        reraise=True,
    )
    async def _fetch_one(self, pokemon_id: int) -> Player:
        url = f"{_POKEAPI_BASE}/pokemon/{pokemon_id}/"
        response = await self._client.get(url)
        response.raise_for_status()
        data = response.json()

        return Player(
            name=data["name"],
            height_cm=data["height"] * 10,  # dm → cm
            weight_kg=data["weight"] / 10,  # hg → kg
            universe=Universe.POKEMON,
        )

    @staticmethod
    def _fallback_players(count: int) -> list[Player]:
        sample = random.sample(_FALLBACK_POKEMON, min(count, len(_FALLBACK_POKEMON)))
        return [
            Player(
                name=p["name"],
                height_cm=p["height_cm"],
                weight_kg=p["weight_kg"],
                universe=Universe.POKEMON,
            )
            for p in sample
        ]

    async def close(self) -> None:
        await self._client.aclose()

from unittest.mock import AsyncMock, MagicMock

import pytest

from adapters.pokemon import PokemonAdapter
from adapters.star_wars import StarWarsAdapter
from domain.models.models import Universe


def _sw_response(name="Luke Skywalker", height="172", mass="77"):
    mock = MagicMock()
    mock.raise_for_status = MagicMock()
    mock.json.return_value = {"name": name, "height": height, "mass": mass}
    return mock


def _pk_response(name="pikachu", height=4, weight=60):
    mock = MagicMock()
    mock.raise_for_status = MagicMock()
    mock.json.return_value = {"name": name, "height": height, "weight": weight}
    return mock


class TestStarWarsAdapter:
    @pytest.mark.asyncio
    async def test_fetch_returns_player(self):
        adapter = StarWarsAdapter()
        mock_client = AsyncMock()
        mock_client.get.return_value = _sw_response()
        adapter._client = mock_client

        player = await adapter._fetch_one(1)

        assert player.name == "Luke Skywalker"
        assert player.height_cm == 172.0
        assert player.weight_kg == 77.0
        assert player.universe == Universe.STAR_WARS

    @pytest.mark.asyncio
    async def test_unknown_height_raises(self):
        adapter = StarWarsAdapter()
        mock_client = AsyncMock()
        mock_client.get.return_value = _sw_response(height="unknown")
        adapter._client = mock_client

        with pytest.raises(ValueError, match="Unknown stats"):
            await adapter._fetch_one(1)

    @pytest.mark.asyncio
    async def test_unknown_mass_raises(self):
        adapter = StarWarsAdapter()
        mock_client = AsyncMock()
        mock_client.get.return_value = _sw_response(mass="unknown")
        adapter._client = mock_client

        with pytest.raises(ValueError, match="Unknown stats"):
            await adapter._fetch_one(1)


class TestPokemonAdapter:
    @pytest.mark.asyncio
    async def test_unit_conversion(self):
        adapter = PokemonAdapter()
        mock_client = AsyncMock()
        mock_client.get.return_value = _pk_response(height=4, weight=60)
        adapter._client = mock_client

        player = await adapter._fetch_one(25)

        # height: 4 dm → 40 cm; weight: 60 hg → 6.0 kg
        assert player.height_cm == 40.0
        assert player.weight_kg == 6.0
        assert player.universe == Universe.POKEMON

    @pytest.mark.asyncio
    async def test_circuit_breaker_uses_fallback(self):
        adapter = PokemonAdapter()
        adapter._consecutive_failures = 5  # trip the circuit

        players = await adapter.fetch_random_players(5)

        assert len(players) == 5
        assert all(p.universe == Universe.POKEMON for p in players)

    def test_fallback_players_all_valid(self):
        players = PokemonAdapter._fallback_players(5)
        assert len(players) == 5
        assert all(p.height_cm > 0 and p.weight_kg > 0 for p in players)

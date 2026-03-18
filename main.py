"""Application entrypoint."""

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from adapters.pokemon import PokemonAdapter
from adapters.registry import registry
from adapters.star_wars import StarWarsAdapter
from domain.models.models import Universe
from presentation.api.router import router

app = FastAPI(
    title="Super Soccer Showdown",
    description="Star Wars vs Pokémon team generator",
    version="0.1.0",
)

registry.register(Universe.STAR_WARS, StarWarsAdapter())
registry.register(Universe.POKEMON, PokemonAdapter())

app.include_router(router)

@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}

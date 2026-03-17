"""Application entrypoint."""

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from presentation.api.router import router

app = FastAPI(
    title="Super Soccer Showdown",
    description="Star Wars vs Pokémon team generator",
    version="0.1.0",
)

app.include_router(router)

@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}

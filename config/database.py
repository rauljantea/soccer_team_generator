"""Async SQLAlchemy session factory.

Engine and session factory are created lazily on first use,
not at module import time, so settings are always fully loaded first.
"""

from collections.abc import AsyncGenerator
from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, async_sessionmaker, create_async_engine

from .config import get_settings


@lru_cache
def get_engine() -> AsyncEngine:
    settings = get_settings()
    return create_async_engine(settings.database_url, echo=settings.debug)


@lru_cache
def get_session_factory() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(get_engine(), expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    factory = get_session_factory()
    async with factory() as session:
        async with session.begin():
            yield session

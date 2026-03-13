from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config.settings import Settings


def get_settings() -> Settings:
    return Settings()


def make_engine(settings: Settings = Depends(get_settings)):  # noqa: B008
    return create_async_engine(settings.database_url, echo=False, pool_pre_ping=True)


# Module-level engine and session factory created lazily
_engine = None
_session_factory = None


def _init_db(database_url: str) -> None:
    global _engine, _session_factory
    _engine = create_async_engine(database_url, echo=False, pool_pre_ping=True)
    _session_factory = async_sessionmaker(_engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession]:
    if _session_factory is None:
        raise RuntimeError("Database not initialised. Call init_db() first.")
    async with _session_factory() as session:
        yield session

"""FastAPI dependency providers."""
from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from contextlib import suppress
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionFactory
from config.settings import Settings, get_settings


async def _run_cleanup(cleanup_coro: Any) -> None:
    cleanup_task = asyncio.create_task(cleanup_coro)
    try:
        await asyncio.shield(cleanup_task)
    except asyncio.CancelledError:
        # If outer task is cancelled, still wait for cleanup to finish.
        with suppress(Exception):
            await cleanup_task
        raise


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    session = AsyncSessionFactory()
    try:
        yield session
    except asyncio.CancelledError:
        # Client disconnects can cancel request tasks while a transaction is open.
        # Shield cleanup so pool connection termination is not interrupted.
        with suppress(Exception):
            await _run_cleanup(session.rollback())
        raise
    except Exception:
        with suppress(Exception):
            await _run_cleanup(session.rollback())
        raise
    finally:
        with suppress(Exception):
            await _run_cleanup(session.close())


def get_settings_dep() -> Settings:
    return get_settings()

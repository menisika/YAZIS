"""Semantic search endpoint."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_settings_dep
from app.services import semantic as semantic_svc
from config.settings import Settings

router = APIRouter(prefix="/semantic", tags=["semantic"])


@router.get("/search")
async def semantic_search(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings_dep),
):
    return await semantic_svc.semantic_search(db, settings=settings, query=q, limit=limit)

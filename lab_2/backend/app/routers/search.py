"""Concordance / KWIC search endpoint."""
from __future__ import annotations

from typing import Optional, Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.services import concordance as concordance_svc

router = APIRouter(prefix="/search", tags=["search"])


@router.get("")
async def concordance_search(
    q: str = Query(..., min_length=1),
    field: Literal["surface", "lemma"] = Query("surface"),
    context: int = Query(5, ge=1, le=20),
    sort_by: Literal["left", "right", "author", "year", "none"] = Query("none"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    text_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    return await concordance_svc.get_concordance(
        db,
        query=q,
        field=field,
        context_window=context,
        sort_by=sort_by,
        page=page,
        page_size=page_size,
        text_id=text_id,
    )

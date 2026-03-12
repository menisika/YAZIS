"""Frequency analysis endpoints."""
from __future__ import annotations

from typing import Optional, Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.services import frequency as freq_svc

router = APIRouter(prefix="/frequency", tags=["frequency"])


@router.get("")
async def get_frequency(
    q: str = Query(..., min_length=1),
    by: Literal["surface", "lemma", "pos"] = Query("lemma"),
    text_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    return await freq_svc.get_frequency(db, query=q, by=by, text_id=text_id)


@router.get("/top")
async def top_n(
    n: int = Query(20, ge=1, le=200),
    by: Literal["surface", "lemma", "pos"] = Query("lemma"),
    pos: Optional[str] = Query(None, description="Filter by POS tag (e.g. NOUN)"),
    text_id: Optional[int] = Query(None),
    exclude_punct: bool = Query(True),
    db: AsyncSession = Depends(get_db),
):
    return await freq_svc.get_top_n(
        db, n=n, by=by, pos_filter=pos, text_id=text_id, exclude_punct=exclude_punct
    )

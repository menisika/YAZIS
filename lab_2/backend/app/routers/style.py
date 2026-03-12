"""Style fingerprint endpoints."""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.services import style as style_svc

router = APIRouter(prefix="/style", tags=["style"])


@router.get("/texts/{text_id}")
async def text_style(text_id: int, db: AsyncSession = Depends(get_db)):
    result = await style_svc.get_text_style(db, text_id)
    if not result:
        raise HTTPException(404, "Text not found")
    return result


@router.get("/compare")
async def compare_texts(
    text_ids: str = Query(..., description="Comma-separated text IDs, e.g. 1,2,3"),
    db: AsyncSession = Depends(get_db),
):
    try:
        ids = [int(x.strip()) for x in text_ids.split(",") if x.strip()]
    except ValueError:
        raise HTTPException(400, "text_ids must be comma-separated integers")
    if len(ids) < 2:
        raise HTTPException(400, "Provide at least 2 text IDs for comparison")
    if len(ids) > 4:
        raise HTTPException(400, "Maximum 4 texts for comparison")
    return await style_svc.compare_texts(db, ids)

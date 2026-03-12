"""Morphological analysis endpoint."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.services import morphology as morph_svc

router = APIRouter(prefix="/morphology", tags=["morphology"])


@router.get("/{lemma}")
async def grammar_card(
    lemma: str,
    text_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    result = await morph_svc.get_grammar_card(db, lemma=lemma, text_id=text_id)
    if result.get("total_occurrences", 0) == 0:
        raise HTTPException(404, f"Lemma '{lemma}' not found in corpus")
    return result

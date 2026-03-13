from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.pattern import PatternQuery, PatternSearchResponse
from app.services.pattern_service import search_pattern

router = APIRouter(prefix="/patterns", tags=["patterns"])


@router.post("/search", response_model=PatternSearchResponse)
async def pattern_search(
    query: PatternQuery,
    db: AsyncSession = Depends(get_db),
) -> PatternSearchResponse:
    return await search_pattern(db, query)

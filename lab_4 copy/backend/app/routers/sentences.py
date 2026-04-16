from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.sentence_repo import SentenceRepository
from app.schemas.sentence import SentenceListItem, SentenceResponse

router = APIRouter(tags=["sentences"])


@router.get("/documents/{document_id}/sentences", response_model=dict)
async def list_sentences(
    document_id: int,
    offset: int = 0,
    limit: int = 50,
    min_complexity: float | None = None,
    max_complexity: float | None = None,
    keyword: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> dict:
    repo = SentenceRepository(db)
    sentences, total = await repo.list_for_document(
        document_id,
        offset=offset,
        limit=limit,
        min_complexity=min_complexity,
        max_complexity=max_complexity,
        keyword=keyword,
    )
    return {
        "total": total,
        "items": [SentenceListItem.model_validate(s).model_dump() for s in sentences],
    }


@router.get("/documents/{document_id}/sentences/all", response_model=list[SentenceListItem])
async def get_all_sentences(
    document_id: int,
    db: AsyncSession = Depends(get_db),
) -> list[SentenceListItem]:
    """Return all sentences ordered by index — used for heatmap."""
    repo = SentenceRepository(db)
    sentences = await repo.get_all_for_document(document_id)
    return [SentenceListItem.model_validate(s) for s in sentences]


@router.get("/sentences/{sentence_id}", response_model=SentenceResponse)
async def get_sentence(
    sentence_id: int,
    db: AsyncSession = Depends(get_db),
) -> SentenceResponse:
    repo = SentenceRepository(db)
    sentence = await repo.get(sentence_id, with_tokens=True)
    if sentence is None:
        raise HTTPException(status_code=404, detail="Sentence not found.")
    return SentenceResponse.model_validate(sentence)

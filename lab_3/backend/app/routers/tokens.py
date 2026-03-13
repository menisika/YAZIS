import csv
import io

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.sentence_repo import SentenceRepository
from app.repositories.token_repo import TokenRepository
from app.schemas.token import TokenResponse

router = APIRouter(tags=["tokens"])


@router.get("/sentences/{sentence_id}/tokens", response_model=list[TokenResponse])
async def get_tokens(
    sentence_id: int,
    db: AsyncSession = Depends(get_db),
) -> list[TokenResponse]:
    sent_repo = SentenceRepository(db)
    if await sent_repo.get(sentence_id) is None:
        raise HTTPException(status_code=404, detail="Sentence not found.")
    repo = TokenRepository(db)
    tokens = await repo.get_for_sentence(sentence_id)
    return [TokenResponse.model_validate(t) for t in tokens]


@router.get("/sentences/{sentence_id}/tokens/csv")
async def export_tokens_csv(
    sentence_id: int,
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    sent_repo = SentenceRepository(db)
    sent = await sent_repo.get(sentence_id)
    if sent is None:
        raise HTTPException(status_code=404, detail="Sentence not found.")

    repo = TokenRepository(db)
    tokens = await repo.get_for_sentence(sentence_id)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["index", "form", "lemma", "pos", "tag", "dep", "head_index", "is_stop", "is_punct", "entity"])
    for t in tokens:
        writer.writerow(
            [t.index, t.text, t.lemma, t.pos, t.tag, t.dep, t.head_index, t.is_stop, t.is_punct, t.ent_type]
        )

    output.seek(0)
    filename = f"sentence_{sentence_id}_tokens.csv"
    return StreamingResponse(
        iter([output.read()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

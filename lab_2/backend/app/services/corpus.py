"""Corpus CRUD and annotated-text service."""
from __future__ import annotations

from typing import Any

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.corpus_text import CorpusText
from app.models.token import Token
from app.models.sentence import Sentence


async def list_texts(
    db: AsyncSession,
    search: str | None = None,
    genre: str | None = None,
    author: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> dict[str, Any]:
    q = select(CorpusText)
    if search:
        q = q.where(
            func.lower(CorpusText.title).contains(search.lower())
        )
    if genre:
        q = q.where(func.lower(CorpusText.genre) == genre.lower())
    if author:
        q = q.where(func.lower(CorpusText.author).contains(author.lower()))

    total_result = await db.execute(select(func.count()).select_from(q.subquery()))
    total = total_result.scalar_one()

    offset = (page - 1) * page_size
    rows = (await db.execute(q.order_by(CorpusText.created_at.desc()).offset(offset).limit(page_size))).scalars().all()

    return {"total": total, "page": page, "page_size": page_size, "results": [_text_summary(t) for t in rows]}


def _text_summary(t: CorpusText) -> dict[str, Any]:
    ttr = None  # computed separately in style service for performance
    return {
        "id": t.id,
        "title": t.title,
        "author": t.author,
        "year": t.year,
        "genre": t.genre,
        "source_url": t.source_url,
        "token_count": t.token_count,
        "sentence_count": t.sentence_count,
        "created_at": t.created_at.isoformat() if t.created_at else None,
    }


async def get_text(db: AsyncSession, text_id: int) -> CorpusText | None:
    return await db.get(CorpusText, text_id)


async def delete_text(db: AsyncSession, text_id: int) -> bool:
    obj = await db.get(CorpusText, text_id)
    if not obj:
        return False
    await db.delete(obj)
    await db.commit()
    return True


async def get_annotated_content(
    db: AsyncSession,
    text_id: int,
    page: int = 1,
    page_size: int = 500,
) -> dict[str, Any]:
    """Return paginated tokens with annotation for the inline reader."""
    corpus_text = await db.get(CorpusText, text_id)
    if not corpus_text:
        return {}

    offset = (page - 1) * page_size
    tokens = (
        await db.execute(
            select(Token)
            .where(Token.text_id == text_id)
            .order_by(Token.token_index)
            .offset(offset)
            .limit(page_size)
        )
    ).scalars().all()

    return {
        "text_id": text_id,
        "title": corpus_text.title,
        "total_tokens": corpus_text.token_count,
        "page": page,
        "page_size": page_size,
        "tokens": [
            {
                "surface": t.surface,
                "lemma": t.lemma,
                "pos": t.pos,
                "tag": t.tag,
                "morph": t.morph,
                "sentence_index": t.sentence_index,
                "token_index": t.token_index,
                "char_start": t.char_start,
                "char_end": t.char_end,
            }
            for t in tokens
        ],
    }

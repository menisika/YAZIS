"""Concordance / KWIC service."""
from __future__ import annotations

from typing import Any

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.token import Token
from app.models.corpus_text import CorpusText


async def get_concordance(
    db: AsyncSession,
    query: str,
    field: str = "surface",  # "surface" | "lemma"
    context_window: int = 5,
    sort_by: str = "none",  # "left" | "right" | "freq" | "author" | "year" | "none"
    page: int = 1,
    page_size: int = 50,
    text_id: int | None = None,
) -> dict[str, Any]:
    query_lower = query.lower().strip()

    col = Token.surface if field == "surface" else Token.lemma
    filter_clause = func.lower(col) == query_lower

    base_q = (
        select(Token, CorpusText)
        .join(CorpusText, Token.text_id == CorpusText.id)
        .where(filter_clause)
    )
    if text_id:
        base_q = base_q.where(Token.text_id == text_id)

    total_result = await db.execute(select(func.count()).select_from(base_q.subquery()))
    total = total_result.scalar_one()

    offset = (page - 1) * page_size
    rows = (await db.execute(base_q.offset(offset).limit(page_size))).all()

    lines = []
    for token, corpus_text in rows:
        context = await _get_context(db, token, context_window)
        lines.append(
            {
                "left": context["left"],
                "match": token.surface,
                "match_lemma": token.lemma,
                "match_pos": token.pos,
                "right": context["right"],
                "text_id": corpus_text.id,
                "title": corpus_text.title,
                "author": corpus_text.author,
                "year": corpus_text.year,
                "genre": corpus_text.genre,
                "sentence_index": token.sentence_index,
                "token_index": token.token_index,
            }
        )

    # Sorting
    if sort_by == "left":
        lines.sort(key=lambda x: x["left"].lower() if x["left"] else "")
    elif sort_by == "right":
        lines.sort(key=lambda x: x["right"].lower() if x["right"] else "")
    elif sort_by == "author":
        lines.sort(key=lambda x: (x["author"] or "").lower())
    elif sort_by == "year":
        lines.sort(key=lambda x: x["year"] or 0)

    return {"total": total, "page": page, "page_size": page_size, "results": lines}


async def _get_context(
    db: AsyncSession, token: Token, window: int
) -> dict[str, str]:
    left_q = (
        select(Token.surface)
        .where(
            and_(
                Token.text_id == token.text_id,
                Token.token_index >= token.token_index - window,
                Token.token_index < token.token_index,
            )
        )
        .order_by(Token.token_index)
    )
    right_q = (
        select(Token.surface)
        .where(
            and_(
                Token.text_id == token.text_id,
                Token.token_index > token.token_index,
                Token.token_index <= token.token_index + window,
            )
        )
        .order_by(Token.token_index)
    )
    left_tokens = (await db.execute(left_q)).scalars().all()
    right_tokens = (await db.execute(right_q)).scalars().all()
    return {
        "left": " ".join(left_tokens),
        "right": " ".join(right_tokens),
    }

"""Frequency analysis service."""
from __future__ import annotations

from typing import Any

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.token import Token
from app.models.corpus_text import CorpusText


async def get_frequency(
    db: AsyncSession,
    query: str,
    by: str = "surface",  # "surface" | "lemma" | "pos"
    text_id: int | None = None,
) -> dict[str, Any]:
    """Frequency of a specific word form / lemma / POS across corpus or per text."""
    query_lower = query.lower().strip()

    if by == "surface":
        match_col = Token.surface
        group_col = Token.text_id
    elif by == "lemma":
        match_col = Token.lemma
        group_col = Token.text_id
    else:  # pos
        match_col = Token.pos
        group_col = Token.text_id

    filter_clause = func.lower(match_col) == query_lower

    # Total count
    total_q = select(func.count()).select_from(Token).where(filter_clause)
    if text_id:
        total_q = total_q.where(Token.text_id == text_id)
    total = (await db.execute(total_q)).scalar_one()

    # Per-text breakdown
    per_text_q = (
        select(
            Token.text_id,
            CorpusText.title,
            CorpusText.author,
            CorpusText.year,
            CorpusText.token_count,
            func.count().label("count"),
        )
        .join(CorpusText, Token.text_id == CorpusText.id)
        .where(filter_clause)
        .group_by(Token.text_id, CorpusText.title, CorpusText.author, CorpusText.year, CorpusText.token_count)
        .order_by(func.count().desc())
    )
    if text_id:
        per_text_q = per_text_q.where(Token.text_id == text_id)

    per_text_rows = (await db.execute(per_text_q)).all()

    per_text = []
    for row in per_text_rows:
        rel_freq = (row.count / row.token_count * 1000) if row.token_count else 0
        per_text.append(
            {
                "text_id": row.text_id,
                "title": row.title,
                "author": row.author,
                "year": row.year,
                "count": row.count,
                "token_count": row.token_count,
                "relative_freq": round(rel_freq, 4),
            }
        )

    return {"query": query, "by": by, "total": total, "per_text": per_text}


async def get_top_n(
    db: AsyncSession,
    n: int = 20,
    by: str = "lemma",  # "surface" | "lemma" | "pos"
    pos_filter: str | None = None,
    text_id: int | None = None,
    exclude_punct: bool = True,
    exclude_stop: bool = False,
) -> dict[str, Any]:
    """Top-N most frequent forms/lemmas/POS tags."""
    if by == "surface":
        group_col = func.lower(Token.surface)
    elif by == "lemma":
        group_col = func.lower(Token.lemma)
    else:
        group_col = Token.pos

    filters = []
    if text_id:
        filters.append(Token.text_id == text_id)
    if pos_filter:
        filters.append(func.upper(Token.pos) == pos_filter.upper())
    if exclude_punct:
        filters.append(Token.pos != "PUNCT")
        filters.append(Token.pos != "SPACE")
        filters.append(Token.pos != "NUM")

    q = (
        select(group_col.label("term"), func.count().label("count"))
        .where(and_(*filters) if filters else True)
        .group_by(group_col)
        .order_by(func.count().desc())
        .limit(n)
    )

    rows = (await db.execute(q)).all()
    return {
        "by": by,
        "n": n,
        "results": [{"term": r.term, "count": r.count} for r in rows],
    }

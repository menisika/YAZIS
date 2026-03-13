"""SQL-based grammatical pattern search — no re-processing."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sentence import Sentence
from app.models.token import Token
from app.schemas.pattern import PatternMatch, PatternQuery, PatternSearchResponse
from app.schemas.sentence import SentenceListItem


async def search_pattern(db: AsyncSession, query: PatternQuery) -> PatternSearchResponse:
    """
    Find sentences where:
      source_token (pos=source_pos) is the head of target_token (pos=target_pos, dep=dep_rel)
    """
    t1 = Token.__table__.alias("t1")
    t2 = Token.__table__.alias("t2")
    s = Sentence.__table__

    stmt = (
        select(
            s.c.id.label("sentence_id"),
            s.c.document_id,
            s.c.index.label("sentence_index"),
            s.c.text.label("sentence_text"),
            s.c.complexity_score,
            s.c.token_count,
            t1.c.index.label("source_token_index"),
            t1.c.text.label("source_text"),
            t2.c.index.label("target_token_index"),
            t2.c.text.label("target_text"),
        )
        .select_from(s)
        .join(t1, t1.c.sentence_id == s.c.id)
        .join(
            t2,
            (t2.c.sentence_id == s.c.id)
            & (t2.c.dep == query.dep_rel)
            & (t2.c.pos == query.target_pos)
            & (t2.c.head_index == t1.c.index),
        )
        .where(t1.c.pos == query.source_pos)
        .order_by(s.c.id)
        .limit(500)
    )

    result = await db.execute(stmt)
    rows = result.all()

    matches = [
        PatternMatch(
            sentence=SentenceListItem(
                id=row.sentence_id,
                document_id=row.document_id,
                index=row.sentence_index,
                text=row.sentence_text,
                complexity_score=row.complexity_score,
                token_count=row.token_count,
            ),
            source_token_index=row.source_token_index,
            target_token_index=row.target_token_index,
            source_text=row.source_text,
            target_text=row.target_text,
        )
        for row in rows
    ]

    return PatternSearchResponse(query=query, total=len(matches), matches=matches)

"""Semantic passage search via pgvector + sentence-transformers."""
from __future__ import annotations

from typing import Any

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sentence import Sentence
from app.models.corpus_text import CorpusText
from config.settings import Settings

_embed_model_cache: dict[str, Any] = {}


def _get_embed_model(model_name: str) -> Any:
    if model_name not in _embed_model_cache:
        from sentence_transformers import SentenceTransformer
        _embed_model_cache[model_name] = SentenceTransformer(model_name)
    return _embed_model_cache[model_name]


async def semantic_search(
    db: AsyncSession,
    settings: Settings,
    query: str,
    limit: int = 20,
) -> dict[str, Any]:
    embed_model = _get_embed_model(settings.embedding_model)
    query_vec = embed_model.encode(query, normalize_embeddings=True).tolist()

    # pgvector cosine distance via raw SQL for flexibility
    sql = text(
        """
        SELECT s.id, s.text_id, s.sentence_index, s.content,
               1 - (s.embedding <=> CAST(:vec AS vector)) AS similarity,
               ct.title, ct.author, ct.year, ct.genre
        FROM sentences s
        JOIN corpus_texts ct ON ct.id = s.text_id
        WHERE s.embedding IS NOT NULL
        ORDER BY s.embedding <=> CAST(:vec AS vector)
        LIMIT :limit
        """
    )
    vec_str = "[" + ",".join(str(v) for v in query_vec) + "]"
    rows = (await db.execute(sql, {"vec": vec_str, "limit": limit})).all()

    results = [
        {
            "sentence_id": r.id,
            "text_id": r.text_id,
            "sentence_index": r.sentence_index,
            "content": r.content,
            "similarity": round(float(r.similarity), 4),
            "title": r.title,
            "author": r.author,
            "year": r.year,
            "genre": r.genre,
        }
        for r in rows
    ]

    return {"query": query, "results": results}

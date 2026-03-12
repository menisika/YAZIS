"""Morphological analysis service — grammar card for a lemma."""
from __future__ import annotations

from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.token import Token
from app.models.sentence import Sentence


async def get_grammar_card(
    db: AsyncSession,
    lemma: str,
    text_id: int | None = None,
) -> dict[str, Any]:
    lemma_lower = lemma.lower().strip()

    filters = [func.lower(Token.lemma) == lemma_lower]
    if text_id:
        filters.append(Token.text_id == text_id)

    # Aggregate by (surface, pos, morph)
    # We fetch all tokens and group in Python for flexibility with JSONB morph
    q = select(Token).where(*filters)
    tokens = (await db.execute(q)).scalars().all()

    if not tokens:
        return {"lemma": lemma_lower, "total_occurrences": 0, "forms": []}

    # Group by (surface_lower, pos, serialized morph)
    groups: dict[tuple, dict[str, Any]] = {}
    for tok in tokens:
        morph_key = str(sorted((tok.morph or {}).items()))
        key = (tok.surface.lower(), tok.pos, morph_key)
        if key not in groups:
            groups[key] = {
                "surface": tok.surface,
                "lemma": lemma_lower,
                "pos": tok.pos,
                "tag": tok.tag,
                "morph": tok.morph or {},
                "count": 0,
                "example_sentence_ids": [],
            }
        entry = groups[key]
        entry["count"] += 1
        if len(entry["example_sentence_ids"]) < 3 and tok.sentence_id:
            if tok.sentence_id not in entry["example_sentence_ids"]:
                entry["example_sentence_ids"].append(tok.sentence_id)

    # Fetch example sentence texts
    all_sent_ids = {sid for g in groups.values() for sid in g["example_sentence_ids"]}
    sent_map: dict[int, str] = {}
    if all_sent_ids:
        sent_rows = (
            await db.execute(select(Sentence).where(Sentence.id.in_(all_sent_ids)))
        ).scalars().all()
        sent_map = {s.id: s.content for s in sent_rows}

    forms = []
    for g in sorted(groups.values(), key=lambda x: -x["count"]):
        forms.append(
            {
                "surface": g["surface"],
                "pos": g["pos"],
                "tag": g["tag"],
                "morph": g["morph"],
                "count": g["count"],
                "examples": [sent_map[sid] for sid in g["example_sentence_ids"] if sid in sent_map],
            }
        )

    return {
        "lemma": lemma_lower,
        "total_occurrences": sum(g["count"] for g in forms),
        "forms": forms,
    }

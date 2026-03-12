"""Author Style Fingerprint service — computes per-text linguistic metrics."""
from __future__ import annotations

import math
import re
from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.token import Token
from app.models.corpus_text import CorpusText

CONTENT_POS = {"NOUN", "VERB", "ADJ", "ADV"}


def _count_syllables(word: str) -> int:
    """Rough syllable count heuristic for Flesch-Kincaid."""
    word = word.lower().strip(".,!?;:'\"()-")
    if not word:
        return 0
    count = len(re.findall(r"[aeiou]+", word))
    if word.endswith("e") and count > 1:
        count -= 1
    return max(1, count)


def _mtld(tokens: list[str], threshold: float = 0.72) -> float:
    """Measure of Textual Lexical Diversity (bidirectional mean)."""
    def _one_pass(seq: list[str]) -> float:
        types: set[str] = set()
        total = 0
        segments = 0
        for t in seq:
            types.add(t)
            total += 1
            if total > 0:
                ttr = len(types) / total
                if ttr <= threshold:
                    segments += 1
                    types = set()
                    total = 0
        # partial segment
        if total > 0:
            ttr = len(types) / total
            if ttr > threshold:
                segments += (1 - ttr) / (1 - threshold)
        return len(seq) / segments if segments > 0 else len(seq)

    forward = _one_pass(tokens)
    backward = _one_pass(list(reversed(tokens)))
    return (forward + backward) / 2


async def get_text_style(
    db: AsyncSession,
    text_id: int,
) -> dict[str, Any]:
    corpus_text = await db.get(CorpusText, text_id)
    if not corpus_text:
        return {}

    tokens = (
        await db.execute(
            select(Token).where(Token.text_id == text_id).order_by(Token.token_index)
        )
    ).scalars().all()

    alpha_tokens = [t for t in tokens if t.pos not in ("PUNCT", "SPACE", "NUM") and t.surface.isalpha()]
    if not alpha_tokens:
        return {"text_id": text_id, "error": "No alphabetic tokens found"}

    lemmas = [t.lemma for t in alpha_tokens]
    surfaces = [t.surface.lower() for t in alpha_tokens]
    pos_list = [t.pos for t in alpha_tokens]

    total = len(alpha_tokens)
    unique_lemmas = len(set(lemmas))

    ttr = unique_lemmas / total if total else 0
    mtld = _mtld(lemmas)

    sentence_count = corpus_text.sentence_count or 1
    avg_sent_len = total / sentence_count

    content_count = sum(1 for p in pos_list if p in CONTENT_POS)
    lexical_density = content_count / total if total else 0

    pos_counts: dict[str, int] = {}
    for p in pos_list:
        pos_counts[p] = pos_counts.get(p, 0) + 1

    pos_dist = {
        "NOUN": round(pos_counts.get("NOUN", 0) / total * 100, 2),
        "VERB": round(pos_counts.get("VERB", 0) / total * 100, 2),
        "ADJ": round(pos_counts.get("ADJ", 0) / total * 100, 2),
        "ADV": round(pos_counts.get("ADV", 0) / total * 100, 2),
        "OTHER": round(
            sum(v for k, v in pos_counts.items() if k not in CONTENT_POS) / total * 100, 2
        ),
    }

    # Flesch-Kincaid readability
    syllable_count = sum(_count_syllables(t.surface) for t in alpha_tokens)
    word_count = total
    fk_score = (
        206.835
        - 1.015 * (word_count / sentence_count)
        - 84.6 * (syllable_count / word_count)
        if word_count and sentence_count
        else 0
    )

    # Top-20 most frequent lemmas (content words only)
    lemma_freq: dict[str, int] = {}
    for t in alpha_tokens:
        if t.pos in CONTENT_POS:
            lemma_freq[t.lemma] = lemma_freq.get(t.lemma, 0) + 1
    top_lemmas = sorted(lemma_freq.items(), key=lambda x: -x[1])[:20]

    return {
        "text_id": text_id,
        "title": corpus_text.title,
        "author": corpus_text.author,
        "year": corpus_text.year,
        "genre": corpus_text.genre,
        "token_count": corpus_text.token_count,
        "sentence_count": corpus_text.sentence_count,
        "metrics": {
            "ttr": round(ttr, 4),
            "mtld": round(mtld, 2),
            "avg_sentence_length": round(avg_sent_len, 2),
            "lexical_density": round(lexical_density, 4),
            "flesch_kincaid": round(fk_score, 2),
        },
        "pos_distribution": pos_dist,
        "top_content_lemmas": [{"lemma": w, "count": c} for w, c in top_lemmas],
    }


async def compare_texts(
    db: AsyncSession,
    text_ids: list[int],
) -> dict[str, Any]:
    results = []
    for tid in text_ids:
        r = await get_text_style(db, tid)
        if r:
            results.append(r)

    # TF-IDF distinctive words across selected texts
    # Build per-text term frequencies
    all_lemma_sets: list[dict[str, int]] = []
    for r in results:
        freq: dict[str, int] = {item["lemma"]: item["count"] for item in r.get("top_content_lemmas", [])}
        all_lemma_sets.append(freq)

    N = len(all_lemma_sets)
    all_terms: set[str] = set()
    for freq in all_lemma_sets:
        all_terms.update(freq.keys())

    # IDF: log(N / df) for each term
    df: dict[str, int] = {}
    for term in all_terms:
        df[term] = sum(1 for freq in all_lemma_sets if freq.get(term, 0) > 0)

    for i, (r, freq) in enumerate(zip(results, all_lemma_sets)):
        total = sum(freq.values()) or 1
        tfidf: list[tuple[str, float]] = []
        for term, cnt in freq.items():
            tf = cnt / total
            idf = math.log(N / df.get(term, 1)) if N > 1 else 0
            tfidf.append((term, tf * idf))
        tfidf.sort(key=lambda x: -x[1])
        r["distinctive_words"] = [{"lemma": t, "score": round(s, 6)} for t, s in tfidf[:20]]

    return {"texts": results}

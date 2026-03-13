"""Orchestrates the full upload -> parse -> NLP -> store pipeline."""
from __future__ import annotations

import time
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sentence import Sentence
from app.models.token import Token
from app.parsers.registry import parse
from app.repositories.document_repo import DocumentRepository
from app.repositories.sentence_repo import SentenceRepository
from app.repositories.token_repo import TokenRepository
from app.schemas.processing import ProcessingSummary
from app.services.complexity_service import compute_raw_complexity, normalise_scores
from app.services.nlp_service import process_text


async def process_upload(
    db: AsyncSession,
    *,
    file_path: Path,
    filename: str,
    ext: str,
) -> ProcessingSummary:
    t_start = time.perf_counter()

    # 1. Extract text
    raw_text = parse(file_path, ext)

    # 2. Run spaCy
    sentence_data_list = await process_text(raw_text)

    # 3. Compute raw complexity scores, then normalise
    raw_scores = [compute_raw_complexity(sd.tokens) for sd in sentence_data_list]
    normalised = normalise_scores(raw_scores)

    # 4. Persist
    doc_repo = DocumentRepository(db)
    sent_repo = SentenceRepository(db)
    tok_repo = TokenRepository(db)

    word_count = len(raw_text.split())
    doc = await doc_repo.create(
        filename=filename,
        original_format=ext.lstrip("."),
        raw_text=raw_text,
        word_count=word_count,
        sentence_count=len(sentence_data_list),
    )

    total_tokens = 0
    for sd, norm_score in zip(sentence_data_list, normalised, strict=True):
        sent_obj = Sentence(
            document_id=doc.id,
            index=sd.index,
            text=sd.text,
            complexity_score=round(norm_score, 2),
            token_count=len(sd.tokens),
        )
        sent_repo.db.add(sent_obj)
        await db.flush()  # get sent_obj.id

        token_objs = [
            Token(
                sentence_id=sent_obj.id,
                index=td.index,
                text=td.text,
                lemma=td.lemma,
                pos=td.pos,
                tag=td.tag,
                dep=td.dep,
                head_index=td.head_index,
                is_stop=td.is_stop,
                is_punct=td.is_punct,
                ent_type=td.ent_type,
            )
            for td in sd.tokens
        ]
        await tok_repo.bulk_create(token_objs)
        total_tokens += len(token_objs)

    await db.commit()

    duration_ms = (time.perf_counter() - t_start) * 1000
    return ProcessingSummary(
        document_id=doc.id,
        filename=filename,
        sentence_count=len(sentence_data_list),
        token_count=total_tokens,
        parse_duration_ms=round(duration_ms, 1),
    )

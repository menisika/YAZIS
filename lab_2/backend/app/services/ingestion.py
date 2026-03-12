"""Ingestion service: parse file -> NLP -> store tokens/sentences/entities -> embeddings."""
from __future__ import annotations

import asyncio
import json
from contextlib import suppress
from typing import TYPE_CHECKING, Any

from app.models.corpus_text import CorpusText
from app.models.named_entity import NamedEntity
from app.models.sentence import Sentence
from app.models.text_embedding import TextEmbedding
from app.models.token import Token
from app.utils import nlp as nlp_utils

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator
    from config.settings import Settings
    from sqlalchemy.ext.asyncio import AsyncSession

_embed_model_cache: dict[str, Any] = {}


def _sse(event: str, data: dict[str, Any]) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


def _get_embed_model(model_name: str) -> Any:
    if model_name not in _embed_model_cache:
        from sentence_transformers import SentenceTransformer  # noqa: PLC0415

        _embed_model_cache[model_name] = SentenceTransformer(model_name)
    return _embed_model_cache[model_name]


async def _run_cleanup(cleanup_coro: Any) -> None:
    cleanup_task = asyncio.create_task(cleanup_coro)
    try:
        await asyncio.shield(cleanup_task)
    except asyncio.CancelledError:
        with suppress(Exception):
            await cleanup_task
        raise


async def ingest_text(
    *,
    db: AsyncSession,
    settings: Settings,
    title: str,
    author: str | None,
    year: int | None,
    genre: str | None,
    source_url: str | None,
    raw_text: str,
) -> AsyncGenerator[str, None]:
    """Yield SSE progress events while ingesting a text into the corpus."""

    async def _run() -> AsyncGenerator[str, None]:
        try:
            yield _sse("progress", {"stage": "parsing", "progress": 5, "message": "Text extracted"})

            # --- NLP ---
            yield _sse("progress", {"stage": "nlp", "progress": 15, "message": "Running NLP pipeline…"})
            doc = nlp_utils.process_text(raw_text, settings.spacy_model)

            sentences_data = nlp_utils.doc_to_sentences(doc)
            tokens_data = nlp_utils.doc_to_tokens(doc)
            entities_data = nlp_utils.doc_to_entities(doc)

            token_count = len(tokens_data)
            sentence_count = len(sentences_data)

            yield _sse("progress", {"stage": "nlp", "progress": 35, "message": f"Found {token_count} tokens in {sentence_count} sentences"})

            # --- Persist CorpusText ---
            corpus_text = CorpusText(
                title=title,
                author=author,
                year=year,
                genre=genre,
                source_url=source_url,
                raw_text=raw_text,
                token_count=token_count,
                sentence_count=sentence_count,
            )
            db.add(corpus_text)
            await db.flush()
            text_id = corpus_text.id

            yield _sse("progress", {"stage": "storing", "progress": 40, "message": "Storing sentences…"})

            # --- Sentences ---
            sentence_objs = []
            for s in sentences_data:
                obj = Sentence(
                    text_id=text_id,
                    sentence_index=s["sentence_index"],
                    content=s["content"],
                )
                db.add(obj)
                sentence_objs.append(obj)
            await db.flush()

            # Build index: sentence_index -> Sentence.id
            sent_index_to_id: dict[int, int] = {
                obj.sentence_index: obj.id for obj in sentence_objs
            }

            yield _sse("progress", {"stage": "storing", "progress": 50, "message": "Storing tokens…"})

            # --- Tokens (bulk) ---
            batch_size = 500
            for i in range(0, len(tokens_data), batch_size):
                batch = tokens_data[i : i + batch_size]
                db.add_all(
                    [
                        Token(
                            text_id=text_id,
                            sentence_id=sent_index_to_id.get(t["sentence_index"]),
                            surface=t["surface"],
                            lemma=t["lemma"],
                            pos=t["pos"],
                            tag=t["tag"],
                            morph=t["morph"],
                            sentence_index=t["sentence_index"],
                            token_index=t["token_index"],
                            char_start=t["char_start"],
                            char_end=t["char_end"],
                        )
                        for t in batch
                    ],
                )

            yield _sse("progress", {"stage": "storing", "progress": 60, "message": "Storing named entities…"})

            # --- Named Entities ---
            db.add_all(
                [
                    NamedEntity(
                        text_id=text_id,
                        sentence_id=sent_index_to_id.get(e["sentence_index"]) if e["sentence_index"] is not None else None,
                        entity_text=e["entity_text"],
                        label=e["label"],
                        start_char=e["start_char"],
                        end_char=e["end_char"],
                    )
                    for e in entities_data
                ],
            )
            await db.flush()

            # --- Sentence Embeddings ---
            yield _sse("progress", {"stage": "embeddings", "progress": 70, "message": "Computing sentence embeddings…"})

            import numpy as np  # noqa: PLC0415

            embed_model = _get_embed_model(settings.embedding_model)
            sentence_texts = [s["content"] for s in sentences_data]

            embed_batch = 64
            all_embeddings: list = []
            for i in range(0, len(sentence_texts), embed_batch):
                batch = sentence_texts[i : i + embed_batch]
                vecs = embed_model.encode(batch, normalize_embeddings=True)
                all_embeddings.extend(vecs.tolist())

            for obj, emb in zip(sentence_objs, all_embeddings, strict=False):
                obj.embedding = emb

            # Document embedding = mean of sentence embeddings
            doc_embedding = np.mean(all_embeddings, axis=0).tolist() if all_embeddings else None

            yield _sse("progress", {"stage": "embeddings", "progress": 90, "message": "Storing document embedding…"})

            db.add(TextEmbedding(text_id=text_id, embedding=doc_embedding))
            await db.commit()

            yield _sse("done", {"text_id": text_id, "progress": 100, "message": "Ingestion complete"})
        except asyncio.CancelledError:
            if db.in_transaction():
                with suppress(Exception):
                    await _run_cleanup(db.rollback())
            raise
        except Exception:
            if db.in_transaction():
                await db.rollback()
            raise

    return _run()

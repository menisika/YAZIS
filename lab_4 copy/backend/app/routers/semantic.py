"""Semantic analysis endpoints — paraphrase, WordNet info, WordNet graph, and on-demand enrichment."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.sentence_repo import SentenceRepository
from app.repositories.token_repo import TokenRepository
from app.schemas.semantic import (
    ConceptNetEdge,
    ConceptNetResponse,
    ParaphraseChange,
    ParaphraseResponse,
    WordNetResponse,
)
from app.services.nlp_service import TokenData
from app.services.paraphrase_service import generate_paraphrase
from app.services.semantic_service import enrich_tokens_with_semantics
from app.services.wordnet_service import get_word_info, get_word_relations

router = APIRouter(tags=["semantic"])


@router.get("/words/{word}/conceptnet", response_model=ConceptNetResponse)
async def get_conceptnet(word: str, pos: str = "") -> ConceptNetResponse:
    """Return WordNet semantic relations in ConceptNet edge format."""
    edges = get_word_relations(word, pos)
    return ConceptNetResponse(
        word=word,
        edges=[
            ConceptNetEdge(
                relation=e["relation"],  # type: ignore[arg-type]
                start_label=e["start_label"],  # type: ignore[arg-type]
                end_label=e["end_label"],  # type: ignore[arg-type]
                weight=float(e["weight"]),  # type: ignore[arg-type]
            )
            for e in edges
        ],
    )


@router.get("/words/{word}/wordnet", response_model=WordNetResponse)
async def get_wordnet(word: str, pos: str = "") -> WordNetResponse:
    """Return WordNet definition and synonyms for a word, optionally filtered by spaCy POS tag."""
    info = get_word_info(word, pos)
    return WordNetResponse(
        word=word,
        definition=info["definition"],  # type: ignore[arg-type]
        synonyms=info["synonyms"],  # type: ignore[arg-type]
    )


@router.get("/sentences/{sentence_id}/paraphrase", response_model=ParaphraseResponse)
async def get_paraphrase(
    sentence_id: int,
    db: AsyncSession = Depends(get_db),
) -> ParaphraseResponse:
    """Generate a paraphrase of the sentence using WordNet synonyms."""
    sent_repo = SentenceRepository(db)
    sentence = await sent_repo.get(sentence_id)
    if sentence is None:
        raise HTTPException(status_code=404, detail="Sentence not found.")

    tok_repo = TokenRepository(db)
    db_tokens = await tok_repo.get_for_sentence(sentence_id)

    token_data_list = [
        TokenData(
            index=t.index,
            text=t.text,
            lemma=t.lemma,
            pos=t.pos,
            tag=t.tag,
            dep=t.dep,
            head_index=t.head_index,
            is_stop=t.is_stop,
            is_punct=t.is_punct,
            ent_type=t.ent_type or "",
        )
        for t in db_tokens
    ]

    result = generate_paraphrase(sentence.text, token_data_list)

    return ParaphraseResponse(
        original=result.original,
        paraphrased=result.paraphrased,
        changes=[
            ParaphraseChange(
                index=c.index,
                original_text=c.original_text,
                synonym=c.synonym,
            )
            for c in result.changes
        ],
    )


@router.post("/sentences/{sentence_id}/analyze")
async def analyze_sentence(
    sentence_id: int,
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    """Run semantic enrichment on-demand for a sentence and persist the results."""
    sent_repo = SentenceRepository(db)
    sentence = await sent_repo.get(sentence_id)
    if sentence is None:
        raise HTTPException(status_code=404, detail="Sentence not found.")

    tok_repo = TokenRepository(db)
    db_tokens = await tok_repo.get_for_sentence(sentence_id)

    token_data_list = [
        TokenData(
            index=t.index,
            text=t.text,
            lemma=t.lemma,
            pos=t.pos,
            tag=t.tag,
            dep=t.dep,
            head_index=t.head_index,
            is_stop=t.is_stop,
            is_punct=t.is_punct,
            ent_type=t.ent_type or "",
        )
        for t in db_tokens
    ]

    enrich_tokens_with_semantics(token_data_list)

    # Write enriched fields back to ORM objects
    td_by_index = {td.index: td for td in token_data_list}
    for db_tok in db_tokens:
        td = td_by_index[db_tok.index]
        db_tok.semantic_role = td.semantic_role or None
        db_tok.semantic_label = td.semantic_label or None
        db_tok.is_anomalous = td.is_anomalous
        db_tok.anomaly_reason = td.anomaly_reason or None

    await db.commit()

    anomaly_count = sum(1 for td in token_data_list if td.is_anomalous)
    return {"analyzed": True, "anomaly_count": anomaly_count}

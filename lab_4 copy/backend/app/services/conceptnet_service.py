"""ConceptNet service — async proxy to the public ConceptNet API."""
from __future__ import annotations

from dataclasses import dataclass

import httpx

CONCEPTNET_BASE = "https://api.conceptnet.io"
_MAX_EDGES = 15


@dataclass
class ConceptNetEdge:
    relation: str
    start_label: str
    end_label: str
    weight: float


@dataclass
class ConceptNetResult:
    word: str
    edges: list[ConceptNetEdge]


def _is_english(node: dict) -> bool:
    """Return True if the ConceptNet node is English.

    Checks the ``language`` field first; falls back to the ``@id`` path prefix
    in case the field is absent in some API responses.
    """
    lang = node.get("language")
    if lang is not None:
        return lang == "en"
    return node.get("@id", "").startswith("/c/en/")


async def fetch_conceptnet(word: str) -> ConceptNetResult:
    """Fetch related concepts for *word* from ConceptNet and return filtered edges."""
    url = f"{CONCEPTNET_BASE}/c/en/{word.lower()}?limit=30"
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()

    raw_edges = data.get("edges", [])
    edges: list[ConceptNetEdge] = []

    for edge in raw_edges:
        start = edge.get("start", {})
        end = edge.get("end", {})
        rel = edge.get("rel", {})

        if not _is_english(start) or not _is_english(end):
            continue

        relation = rel.get("label", "RelatedTo")
        start_label = start.get("label", start.get("term", "?"))
        end_label = end.get("label", end.get("term", "?"))
        weight = float(edge.get("weight", 1.0))

        if start_label.lower() == end_label.lower():
            continue

        edges.append(ConceptNetEdge(
            relation=relation,
            start_label=start_label,
            end_label=end_label,
            weight=weight,
        ))

        if len(edges) >= _MAX_EDGES:
            break

    return ConceptNetResult(word=word, edges=edges)

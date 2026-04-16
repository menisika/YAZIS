"""WordNet service — definitions, synonyms, and semantic relation graphs."""
from __future__ import annotations

from nltk.corpus import wordnet as wn

_SPACY_TO_WN: dict[str, str] = {
    "NOUN": wn.NOUN,
    "VERB": wn.VERB,
    "ADJ": wn.ADJ,
    "ADV": wn.ADV,
}

_MAX_EDGES = 15


def get_word_info(word: str, spacy_pos: str) -> dict[str, object]:
    """Return the definition and synonyms for *word* filtered by its POS tag."""
    wn_pos = _SPACY_TO_WN.get(spacy_pos)
    synsets = wn.synsets(word.lower(), pos=wn_pos) if wn_pos else wn.synsets(word.lower())
    if not synsets:
        return {"definition": None, "synonyms": []}
    ss = synsets[0]
    definition = ss.definition()
    synonyms = [
        lemma.name().replace("_", " ")
        for lemma in ss.lemmas()
        if lemma.name().lower() != word.lower()
    ][:6]
    return {"definition": definition, "synonyms": synonyms}


def get_word_relations(word: str, spacy_pos: str = "") -> list[dict[str, object]]:
    """Return WordNet semantic relations as ConceptNet-shaped edge dicts.

    Covers: Synonym, Antonym, IsA (hypernym), Narrower (hyponym),
    PartOf (holonym), HasPart (meronym).
    """
    wn_pos = _SPACY_TO_WN.get(spacy_pos)
    synsets = wn.synsets(word.lower(), pos=wn_pos) if wn_pos else wn.synsets(word.lower())
    if not synsets:
        return []

    edges: list[dict[str, object]] = []
    seen: set[tuple[str, str, str]] = set()

    def _add(relation: str, target: str, weight: float = 1.0) -> None:
        key = (relation, word.lower(), target.lower())
        if key in seen or target.lower() == word.lower():
            return
        seen.add(key)
        edges.append({
            "relation": relation,
            "start_label": word,
            "end_label": target.replace("_", " "),
            "weight": weight,
        })

    # Use the first synset for primary relations, up to 3 for broader coverage
    for ss in synsets[:2]:
        # Synonyms (other lemmas in same synset)
        for lemma in ss.lemmas():
            _add("SimilarTo", lemma.name(), 2.0)
            # Antonyms
            for ant in lemma.antonyms():
                _add("Antonym", ant.name(), 1.5)

        # Hypernyms — "IsA" (word IsA hypernym)
        for hyper in ss.hypernyms():
            label = hyper.lemmas()[0].name() if hyper.lemmas() else hyper.name()
            _add("IsA", label, 1.8)

        # Hyponyms — narrower concepts
        for hypo in ss.hyponyms()[:4]:
            label = hypo.lemmas()[0].name() if hypo.lemmas() else hypo.name()
            _add("Narrower", label, 1.2)

        # Holonyms — "PartOf"
        for holo in ss.part_holonyms() + ss.substance_holonyms():
            label = holo.lemmas()[0].name() if holo.lemmas() else holo.name()
            _add("PartOf", label, 1.0)

        # Meronyms — "HasPart"
        for mero in ss.part_meronyms() + ss.substance_meronyms():
            label = mero.lemmas()[0].name() if mero.lemmas() else mero.name()
            _add("HasPart", label, 1.0)

        if len(edges) >= _MAX_EDGES:
            break

    return edges[:_MAX_EDGES]
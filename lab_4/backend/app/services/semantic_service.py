"""Semantic analysis service — assigns semantic roles and detects anomalies."""
from __future__ import annotations

from nltk.corpus import wordnet as wn

from app.services.nlp_service import TokenData

# ─── Semantic role mapping from dependency relation ───────────────────────────

DEP_TO_SEMANTIC_ROLE: dict[str, tuple[str, str]] = {
    "nsubj": ("AGNT", "Agent"),
    "nsubjpass": ("PAT", "Patient"),
    "csubj": ("AGNT", "Agent"),
    "csubjpass": ("PAT", "Patient"),
    "ROOT": ("ACT", "Action"),
    "obj": ("PAT", "Patient"),
    "dobj": ("PAT", "Patient"),
    "iobj": ("RCPT", "Recipient"),
    "dative": ("RCPT", "Recipient"),
    "amod": ("ATTR", "Attribute"),
    "advmod": ("ATTR", "Attribute"),
    "npadvmod": ("ATTR", "Attribute"),
    "acomp": ("ATTR", "Attribute"),
    "oprd": ("ATTR", "Attribute"),
    "conj": ("CONJ", "Conjunction"),
    "aux": ("AUX", "Auxiliary"),
    "auxpass": ("AUX", "Auxiliary"),
    "cop": ("AUX", "Copula"),
    "neg": ("NEG", "Negation"),
    "compound": ("MOD", "Modifier"),
    "det": ("DET", "Determiner"),
    "poss": ("POSS", "Possessor"),
    "nummod": ("QUANT", "Quantity"),
    "quantmod": ("QUANT", "Quantity"),
    "appos": ("APPOS", "Apposition"),
    "prep": ("MOD", "Modifier"),
    "relcl": ("MOD", "Modifier"),
    "advcl": ("MOD", "Modifier"),
    "acl": ("MOD", "Modifier"),
    "mark": ("MOD", "Modifier"),
    "cc": ("CONJ", "Conjunction"),
    "punct": ("PUNCT", "Punctuation"),
    "intj": ("MOD", "Modifier"),
    "expl": ("MOD", "Modifier"),
    "attr": ("ATTR", "Attribute"),
    "agent": ("AGNT", "Agent"),
    "xcomp": ("PAT", "Patient"),
    "ccomp": ("PAT", "Patient"),
    "pcomp": ("MOD", "Modifier"),
    "parataxis": ("MOD", "Modifier"),
    "dep": ("MOD", "Modifier"),
}

# Role refinement for pobj based on their preposition head's text
PREP_TO_ROLE: dict[str, tuple[str, str]] = {
    "with": ("INST", "Instrument"),
    "using": ("INST", "Instrument"),
    "via": ("INST", "Instrument"),
    "by means of": ("INST", "Instrument"),
    "in": ("LOC", "Location"),
    "at": ("LOC", "Location"),
    "on": ("LOC", "Location"),
    "inside": ("LOC", "Location"),
    "outside": ("LOC", "Location"),
    "near": ("LOC", "Location"),
    "beside": ("LOC", "Location"),
    "above": ("LOC", "Location"),
    "below": ("LOC", "Location"),
    "beneath": ("LOC", "Location"),
    "around": ("LOC", "Location"),
    "for": ("PURP", "Purpose"),
    "from": ("SRC", "Source"),
    "out of": ("SRC", "Source"),
    "since": ("TEMP", "Time"),
    "after": ("TEMP", "Time"),
    "before": ("TEMP", "Time"),
    "during": ("TEMP", "Time"),
    "while": ("TEMP", "Time"),
    "when": ("TEMP", "Time"),
    "to": ("GOAL", "Goal"),
    "toward": ("GOAL", "Goal"),
    "towards": ("GOAL", "Goal"),
    "into": ("GOAL", "Goal"),
    "by": ("MANN", "Manner"),
    "because of": ("CAUS", "Cause"),
    "due to": ("CAUS", "Cause"),
}

# Verbs that require animate (living) subjects
ANIMATE_REQUIRING_VERBS: frozenset[str] = frozenset({
    "drink", "eat", "speak", "think", "run", "walk", "sleep", "breathe",
    "feel", "see", "hear", "taste", "smell", "talk", "write", "read",
    "love", "hate", "believe", "know", "remember", "want", "decide",
    "laugh", "cry", "sing", "dance", "fear", "hope", "wish", "die",
    "live", "grow", "play", "dream", "choose", "say", "tell", "ask",
    "swim", "fly", "jump", "sit", "stand", "smile", "look", "watch",
    "listen", "touch", "hold", "carry", "give", "take", "buy", "sell",
    "work", "study", "learn", "teach", "understand", "forget", "wake",
})

# WordNet animate hypernym names
_ANIMATE_SYNSET_NAMES: frozenset[str] = frozenset({
    "living_thing.n.01",
    "organism.n.01",
    "person.n.01",
    "animal.n.01",
    "human.n.01",
    "causal_agent.n.01",
})


def _is_animate(lemma: str) -> bool:
    """Return True if the word's WordNet hypernym path includes a living entity."""
    synsets = wn.synsets(lemma.lower(), pos=wn.NOUN)
    for synset in synsets[:3]:
        try:
            for path in synset.hypernym_paths():
                for ancestor in path:
                    if ancestor.name() in _ANIMATE_SYNSET_NAMES:
                        return True
        except Exception:  # noqa: BLE001
            continue
    return False


def _get_pobj_role(token: TokenData, index_map: dict[int, TokenData]) -> tuple[str, str]:
    """Find semantic role for a pobj by looking at its preposition head."""
    prep = index_map.get(token.head_index)
    if prep is not None:
        prep_text = prep.text.lower()
        role = PREP_TO_ROLE.get(prep_text)
        if role:
            return role
    return ("PAT", "Patient")


def enrich_tokens_with_semantics(tokens: list[TokenData]) -> list[TokenData]:
    """Assign semantic roles and detect anomalies for a sentence's tokens.

    Mutates tokens in-place and returns the list.
    """
    index_map: dict[int, TokenData] = {t.index: t for t in tokens}

    # Pass 1: assign semantic roles
    for token in tokens:
        dep = token.dep
        if dep == "pobj":
            role, label = _get_pobj_role(token, index_map)
        else:
            role, label = DEP_TO_SEMANTIC_ROLE.get(dep, ("MOD", "Modifier"))
        token.semantic_role = role
        token.semantic_label = label

    # Pass 2: anomaly detection — for each verb requiring animate agent,
    # check if its nsubj child is inanimate
    verb_tokens = [t for t in tokens if t.pos == "VERB" and t.lemma.lower() in ANIMATE_REQUIRING_VERBS]
    for verb in verb_tokens:
        # Find nsubj child
        nsubj_children = [
            t for t in tokens
            if t.head_index == verb.index and t.dep in ("nsubj", "csubj")
        ]
        for subj in nsubj_children:
            if subj.pos in ("NOUN", "PROPN") and not _is_animate(subj.lemma):
                subj.is_anomalous = True
                subj.anomaly_reason = (
                    f"Inanimate subject '{subj.text}' used with animate-requiring verb '{verb.lemma}'"
                )

    return tokens

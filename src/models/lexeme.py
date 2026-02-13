"""Core domain models: MorphologicalFeature, WordForm, DictionaryEntry."""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Any

from models.enums import PartOfSpeech


@dataclass(slots=True)
class MorphologicalFeature:
    """Morphological properties associated with a word form.

    Attributes:
        tense: Verb tense (present, past, past_participle, present_participle).
        number: Grammatical number (singular, plural).
        person: Grammatical person (1st, 2nd, 3rd).
        case: Pronoun case (subject, object, possessive, reflexive).
        degree: Comparison degree (positive, comparative, superlative).
        aspect: Verbal aspect (e.g. ``progressive``).
        voice: Active or passive.
    """

    tense: str | None = None
    number: str | None = None
    person: str | None = None
    case: str | None = None
    degree: str | None = None
    aspect: str | None = None
    voice: str | None = None

    def to_dict(self) -> dict[str, str]:
        """Serialize non-None fields to a dict."""
        return {f.name: getattr(self, f.name) for f in fields(self) if getattr(self, f.name) is not None}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MorphologicalFeature:
        """Deserialize from a dict, ignoring unknown keys."""
        valid_keys = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in valid_keys})

    def matches(self, **criteria: str | None) -> bool:
        """Check whether this feature set matches all given criteria.

        Only non-None criteria are checked.
        """
        for key, value in criteria.items():
            if value is not None and getattr(self, key, None) != value:
                return False
        return True

    def summary(self) -> str:
        """Human-readable summary of features."""
        parts = [f"{k}={v}" for k, v in self.to_dict().items()]
        return ", ".join(parts) if parts else "base"


@dataclass(slots=True)
class WordForm:
    """A single inflected form of a lexeme.

    Attributes:
        form: The actual word form string (e.g. ``running``).
        ending: The suffix/ending applied to the stem (e.g. ``-ning``).
        features: Morphological features describing this form.
    """

    form: str
    ending: str
    features: MorphologicalFeature

    def to_dict(self) -> dict[str, Any]:
        return {
            "form": self.form,
            "ending": self.ending,
            "features": self.features.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WordForm:
        return cls(
            form=data["form"],
            ending=data.get("ending", ""),
            features=MorphologicalFeature.from_dict(data.get("features", {})),
        )


@dataclass(slots=True)
class DictionaryEntry:
    """A complete dictionary entry for a single lexeme.

    Attributes:
        lexeme: The base/lemma form (e.g. ``run``).
        stem: The morphological stem (e.g. ``run``).
        pos: Part of speech.
        frequency: Number of occurrences in source text.
        word_forms: All known inflected forms.
        irregular: Whether the lexeme has irregular morphology.
        notes: Free-text annotation.
    """

    lexeme: str
    stem: str
    pos: PartOfSpeech
    frequency: int = 0
    word_forms: list[WordForm] = field(default_factory=list)
    irregular: bool = False
    notes: str = ""
    definition: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "lexeme": self.lexeme,
            "stem": self.stem,
            "pos": str(self.pos),
            "frequency": self.frequency,
            "word_forms": [wf.to_dict() for wf in self.word_forms],
            "irregular": self.irregular,
            "notes": self.notes,
            "definition": self.definition,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DictionaryEntry:
        return cls(
            lexeme=data["lexeme"],
            stem=data["stem"],
            pos=PartOfSpeech(data["pos"]),
            frequency=data.get("frequency", 0),
            word_forms=[WordForm.from_dict(wf) for wf in data.get("word_forms", [])],
            irregular=data.get("irregular", False),
            notes=data.get("notes", ""),
            definition=data.get("definition", ""),
        )

    def get_forms_by(self, **criteria: str | None) -> list[WordForm]:
        """Filter word forms by morphological criteria."""
        return [wf for wf in self.word_forms if wf.features.matches(**criteria)]

    def add_word_form(self, word_form: WordForm) -> None:
        """Add a word form, avoiding exact duplicates."""
        for existing in self.word_forms:
            if existing.form == word_form.form and existing.features.to_dict() == word_form.features.to_dict():
                return
        self.word_forms.append(word_form)

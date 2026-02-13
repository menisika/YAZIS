"""Rule engine for word form generation from stem + morphological rules."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from models.enums import Degree, Number, PartOfSpeech, Tense
from models.lexeme import MorphologicalFeature, WordForm
from utils.constants import RESOURCES_DIR
from utils.helpers import (
    apply_e_dropping,
    apply_es_rule,
    apply_ies_rule,
    apply_y_to_i,
    double_final_consonant,
    is_consonant,
    is_vowel,
)
from utils.logging_config import get_logger

logger = get_logger("core.rule_engine")


class RuleEngine:
    """Generate inflected word forms from a lexeme and desired features.

    Loads irregular form dictionaries on first use and applies
    regular English morphological rules with spelling adjustments.
    """

    def __init__(self) -> None:
        self._irregular_verbs: dict[str, dict[str, str]] = {}
        self._irregular_nouns: dict[str, str] = {}
        self._irregular_adjectives: dict[str, dict[str, str]] = {}
        self._loaded = False

    def _ensure_loaded(self) -> None:
        """Lazy-load irregular form dictionaries."""
        if self._loaded:
            return
        self._irregular_verbs = self._load_json(RESOURCES_DIR / "irregular_verbs.json")
        self._irregular_nouns = self._load_json(RESOURCES_DIR / "irregular_nouns.json")
        self._irregular_adjectives = self._load_json(RESOURCES_DIR / "irregular_adjectives.json")
        self._loaded = True
        logger.debug(
            "Loaded irregular forms: %d verbs, %d nouns, %d adjectives",
            len(self._irregular_verbs),
            len(self._irregular_nouns),
            len(self._irregular_adjectives),
        )

    @staticmethod
    def _load_json(path: Path) -> Any:
        if not path.exists():
            logger.warning("Resource file not found: %s", path)
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    # --- Public API ---

    def generate_form(
        self, lexeme: str, pos: PartOfSpeech, features: MorphologicalFeature
    ) -> WordForm:
        """Generate a single word form.

        Args:
            lexeme: Base form (lemma).
            pos: Part of speech.
            features: Desired morphological features.

        Returns:
            Generated :class:`WordForm`.
        """
        self._ensure_loaded()

        if pos == PartOfSpeech.VERB:
            form = self._generate_verb_form(lexeme, features)
        elif pos == PartOfSpeech.NOUN:
            form = self._generate_noun_form(lexeme, features)
        elif pos == PartOfSpeech.ADJECTIVE:
            form = self._generate_adjective_form(lexeme, features)
        elif pos == PartOfSpeech.ADVERB:
            form = self._generate_adverb_form(lexeme, features)
        else:
            form = lexeme

        ending = self._compute_ending(lexeme, form)
        return WordForm(form=form, ending=ending, features=features)

    def generate_all_forms(
        self, lexeme: str, pos: PartOfSpeech
    ) -> list[WordForm]:
        """Generate all standard inflected forms for a lexeme.

        Args:
            lexeme: Base form.
            pos: Part of speech.

        Returns:
            List of generated :class:`WordForm` objects.
        """
        self._ensure_loaded()

        if pos == PartOfSpeech.VERB:
            return self._all_verb_forms(lexeme)
        elif pos == PartOfSpeech.NOUN:
            return self._all_noun_forms(lexeme)
        elif pos == PartOfSpeech.ADJECTIVE:
            return self._all_adjective_forms(lexeme)
        elif pos == PartOfSpeech.ADVERB:
            return self._all_adverb_forms(lexeme)
        else:
            return [WordForm(form=lexeme, ending="", features=MorphologicalFeature())]

    def is_irregular(self, lexeme: str, pos: PartOfSpeech) -> bool:
        """Check whether a lexeme has irregular forms."""
        self._ensure_loaded()
        if pos == PartOfSpeech.VERB:
            return lexeme.lower() in self._irregular_verbs
        if pos == PartOfSpeech.NOUN:
            return lexeme.lower() in self._irregular_nouns
        if pos == PartOfSpeech.ADJECTIVE:
            return lexeme.lower() in self._irregular_adjectives
        return False

    # --- Verb generation ---

    def _generate_verb_form(self, lemma: str, feat: MorphologicalFeature) -> str:
        irr = self._irregular_verbs.get(lemma.lower(), {})

        tense = feat.tense
        if tense == Tense.PAST:
            return irr.get("past") or self._regular_past(lemma)
        if tense == Tense.PAST_PARTICIPLE:
            return irr.get("past_participle") or self._regular_past(lemma)
        if tense == Tense.PRESENT_PARTICIPLE:
            return irr.get("present_participle") or self._regular_present_participle(lemma)
        if tense == Tense.PRESENT and feat.person == "3rd" and feat.number == "singular":
            return irr.get("third_person") or self._regular_third_person(lemma)
        if tense == Tense.INFINITIVE:
            return lemma
        return lemma

    def _regular_past(self, lemma: str) -> str:
        """Regular -ed formation with spelling rules."""
        if lemma.endswith("e"):
            return lemma + "d"
        if lemma.endswith("y") and len(lemma) >= 2 and is_consonant(lemma[-2]):
            return lemma[:-1] + "ied"
        stem = double_final_consonant(lemma)
        if stem != lemma:
            return stem + "ed"
        return lemma + "ed"

    def _regular_present_participle(self, lemma: str) -> str:
        """Regular -ing formation."""
        if lemma.endswith("ie"):
            return lemma[:-2] + "ying"
        if lemma.endswith("e") and not lemma.endswith("ee"):
            return lemma[:-1] + "ing"
        stem = double_final_consonant(lemma)
        if stem != lemma:
            return stem + "ing"
        return lemma + "ing"

    def _regular_third_person(self, lemma: str) -> str:
        """Regular 3rd person singular present."""
        return apply_es_rule(lemma) if lemma.endswith(("s", "x", "z", "ch", "sh")) else apply_ies_rule(lemma)

    def _all_verb_forms(self, lemma: str) -> list[WordForm]:
        forms: list[WordForm] = []
        specs = [
            MorphologicalFeature(tense="infinitive"),
            MorphologicalFeature(tense="present"),
            MorphologicalFeature(tense="present", person="3rd", number="singular"),
            MorphologicalFeature(tense="past"),
            MorphologicalFeature(tense="past_participle"),
            MorphologicalFeature(tense="present_participle", aspect="progressive"),
        ]
        for feat in specs:
            wf = self.generate_form(lemma, PartOfSpeech.VERB, feat)
            forms.append(wf)
        return forms

    # --- Noun generation ---

    def _generate_noun_form(self, lemma: str, feat: MorphologicalFeature) -> str:
        if feat.number == "plural":
            irr = self._irregular_nouns.get(lemma.lower())
            if irr:
                return irr
            return self._regular_plural(lemma)
        if feat.case == "possessive":
            return lemma + "'s"
        return lemma

    def _regular_plural(self, lemma: str) -> str:
        if lemma.endswith(("s", "x", "z", "ch", "sh")):
            return lemma + "es"
        if lemma.endswith("y") and len(lemma) >= 2 and is_consonant(lemma[-2]):
            return lemma[:-1] + "ies"
        if lemma.endswith("f"):
            return lemma[:-1] + "ves"
        if lemma.endswith("fe"):
            return lemma[:-2] + "ves"
        return lemma + "s"

    def _all_noun_forms(self, lemma: str) -> list[WordForm]:
        return [
            self.generate_form(lemma, PartOfSpeech.NOUN, MorphologicalFeature(number="singular")),
            self.generate_form(lemma, PartOfSpeech.NOUN, MorphologicalFeature(number="plural")),
            self.generate_form(lemma, PartOfSpeech.NOUN, MorphologicalFeature(case="possessive")),
        ]

    # --- Adjective generation ---

    def _generate_adjective_form(self, lemma: str, feat: MorphologicalFeature) -> str:
        irr = self._irregular_adjectives.get(lemma.lower(), {})

        if feat.degree == "comparative":
            if irr and "comparative" in irr:
                return irr["comparative"]
            return self._regular_comparative(lemma)
        if feat.degree == "superlative":
            if irr and "superlative" in irr:
                return irr["superlative"]
            return self._regular_superlative(lemma)
        return lemma

    def _regular_comparative(self, lemma: str) -> str:
        """Generate comparative form. Short adjectives get -er, long ones get 'more'."""
        if self._is_short_adjective(lemma):
            if lemma.endswith("e"):
                return lemma + "r"
            if lemma.endswith("y") and len(lemma) >= 2 and is_consonant(lemma[-2]):
                return lemma[:-1] + "ier"
            stem = double_final_consonant(lemma)
            if stem != lemma:
                return stem + "er"
            return lemma + "er"
        return f"more {lemma}"

    def _regular_superlative(self, lemma: str) -> str:
        if self._is_short_adjective(lemma):
            if lemma.endswith("e"):
                return lemma + "st"
            if lemma.endswith("y") and len(lemma) >= 2 and is_consonant(lemma[-2]):
                return lemma[:-1] + "iest"
            stem = double_final_consonant(lemma)
            if stem != lemma:
                return stem + "est"
            return lemma + "est"
        return f"most {lemma}"

    @staticmethod
    def _is_short_adjective(word: str) -> bool:
        """Heuristic: adjectives with <=2 syllables typically use -er/-est."""
        vowel_groups = 0
        prev_vowel = False
        for ch in word.lower():
            if is_vowel(ch):
                if not prev_vowel:
                    vowel_groups += 1
                prev_vowel = True
            else:
                prev_vowel = False
        return vowel_groups <= 2

    def _all_adjective_forms(self, lemma: str) -> list[WordForm]:
        return [
            self.generate_form(lemma, PartOfSpeech.ADJECTIVE, MorphologicalFeature(degree="positive")),
            self.generate_form(lemma, PartOfSpeech.ADJECTIVE, MorphologicalFeature(degree="comparative")),
            self.generate_form(lemma, PartOfSpeech.ADJECTIVE, MorphologicalFeature(degree="superlative")),
        ]

    # --- Adverb generation ---

    def _generate_adverb_form(self, lemma: str, feat: MorphologicalFeature) -> str:
        if feat.degree == "comparative":
            return f"more {lemma}"
        if feat.degree == "superlative":
            return f"most {lemma}"
        return lemma

    def _all_adverb_forms(self, lemma: str) -> list[WordForm]:
        return [
            self.generate_form(lemma, PartOfSpeech.ADVERB, MorphologicalFeature(degree="positive")),
            self.generate_form(lemma, PartOfSpeech.ADVERB, MorphologicalFeature(degree="comparative")),
            self.generate_form(lemma, PartOfSpeech.ADVERB, MorphologicalFeature(degree="superlative")),
        ]

    # --- Helpers ---

    @staticmethod
    def _compute_ending(lemma: str, form: str) -> str:
        if form == lemma:
            return ""
        min_len = min(len(lemma), len(form))
        i = 0
        while i < min_len and lemma[i] == form[i]:
            i += 1
        suffix = form[i:]
        return f"-{suffix}" if suffix else ""

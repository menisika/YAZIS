"""Morphological analysis with Strategy pattern (NLTK vs spaCy)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from models.enums import PartOfSpeech
from models.lexeme import DictionaryEntry, MorphologicalFeature, WordForm
from utils.logging_config import get_logger

logger = get_logger("core.morphological_analyzer")


class AnalysisStrategy(ABC):
    """Abstract strategy for morphological analysis of tokens."""

    @abstractmethod
    def analyze_tokens(
        self,
        tokens: list[str],
        pos_map: dict[str, PartOfSpeech],
        forms_map: dict[str, list[str]],
    ) -> dict[str, list[WordForm]]:
        """Analyze tokens and return word forms keyed by lemma.

        Args:
            tokens: Unique lemma strings.
            pos_map: Lemma-to-POS mapping.
            forms_map: Lemma-to-observed-forms mapping.

        Returns:
            ``{lemma: [WordForm, ...]}`` for each lemma.
        """


class NLTKStrategy(AnalysisStrategy):
    """NLTK-based morphological analysis.

    Derives morphological features by comparing observed inflected forms
    to the base lemma, using POS tag to infer feature meaning.
    """

    def analyze_tokens(
        self,
        lemmas: list[str],
        pos_map: dict[str, PartOfSpeech],
        forms_map: dict[str, list[str]],
    ) -> dict[str, list[WordForm]]:
        import nltk  # type: ignore[import-untyped]

        results: dict[str, list[WordForm]] = {}

        for lemma in lemmas:
            pos = pos_map.get(lemma, PartOfSpeech.OTHER)
            observed_forms = forms_map.get(lemma, [lemma])
            word_forms: list[WordForm] = []

            for form in observed_forms:
                features = self._infer_features(lemma, form, pos)
                ending = self._compute_ending(lemma, form)
                word_forms.append(WordForm(form=form, ending=ending, features=features))

            # Always include the base form
            if not any(wf.form == lemma for wf in word_forms):
                word_forms.insert(
                    0,
                    WordForm(
                        form=lemma,
                        ending="",
                        features=MorphologicalFeature(
                            tense="present" if pos == PartOfSpeech.VERB else None,
                            number="singular" if pos == PartOfSpeech.NOUN else None,
                            degree="positive" if pos in (PartOfSpeech.ADJECTIVE, PartOfSpeech.ADVERB) else None,
                        ),
                    ),
                )

            results[lemma] = word_forms

        logger.info("NLTK strategy analyzed %d lemmas", len(results))
        return results

    def _infer_features(
        self, lemma: str, form: str, pos: PartOfSpeech
    ) -> MorphologicalFeature:
        """Heuristic feature inference from form vs lemma."""
        if form == lemma:
            return self._base_features(pos)

        if pos == PartOfSpeech.VERB:
            return self._infer_verb_features(lemma, form)
        elif pos == PartOfSpeech.NOUN:
            return self._infer_noun_features(lemma, form)
        elif pos in (PartOfSpeech.ADJECTIVE, PartOfSpeech.ADVERB):
            return self._infer_adj_features(lemma, form)

        return MorphologicalFeature()

    def _base_features(self, pos: PartOfSpeech) -> MorphologicalFeature:
        if pos == PartOfSpeech.VERB:
            return MorphologicalFeature(tense="present")
        if pos == PartOfSpeech.NOUN:
            return MorphologicalFeature(number="singular")
        if pos in (PartOfSpeech.ADJECTIVE, PartOfSpeech.ADVERB):
            return MorphologicalFeature(degree="positive")
        return MorphologicalFeature()

    def _infer_verb_features(self, lemma: str, form: str) -> MorphologicalFeature:
        if form.endswith("ing"):
            return MorphologicalFeature(tense="present_participle", aspect="progressive")
        if form.endswith("ed"):
            return MorphologicalFeature(tense="past")
        if form.endswith("en") and form != lemma:
            return MorphologicalFeature(tense="past_participle")
        if form.endswith("s") and form != lemma:
            return MorphologicalFeature(tense="present", person="3rd", number="singular")
        return MorphologicalFeature(tense="present")

    def _infer_noun_features(self, lemma: str, form: str) -> MorphologicalFeature:
        if form != lemma and (form.endswith("s") or form.endswith("es") or form.endswith("ies")):
            return MorphologicalFeature(number="plural")
        if "'s" in form or "s'" in form:
            return MorphologicalFeature(case="possessive")
        return MorphologicalFeature(number="singular")

    def _infer_adj_features(self, lemma: str, form: str) -> MorphologicalFeature:
        if form.endswith("est") or form.startswith("most "):
            return MorphologicalFeature(degree="superlative")
        if form.endswith("er") or form.startswith("more "):
            return MorphologicalFeature(degree="comparative")
        return MorphologicalFeature(degree="positive")

    @staticmethod
    def _compute_ending(lemma: str, form: str) -> str:
        """Compute the suffix that differs between lemma and form."""
        if form == lemma:
            return ""
        # Find common prefix
        min_len = min(len(lemma), len(form))
        i = 0
        while i < min_len and lemma[i] == form[i]:
            i += 1
        suffix = form[i:]
        return f"-{suffix}" if suffix else ""


class SpaCyStrategy(AnalysisStrategy):
    """spaCy-based morphological analysis using spaCy's morphology component."""

    def __init__(self, model_name: str = "en_core_web_sm") -> None:
        self._model_name = model_name
        self._nlp: Any = None

    def _load_model(self) -> Any:
        if self._nlp is None:
            try:
                import spacy  # type: ignore[import-untyped]
                self._nlp = spacy.load(self._model_name)
                logger.info("Loaded spaCy model: %s", self._model_name)
            except (ImportError, OSError) as exc:
                logger.warning("spaCy model '%s' unavailable: %s", self._model_name, exc)
                raise
        return self._nlp

    def analyze_tokens(
        self,
        lemmas: list[str],
        pos_map: dict[str, PartOfSpeech],
        forms_map: dict[str, list[str]],
    ) -> dict[str, list[WordForm]]:
        nlp = self._load_model()
        results: dict[str, list[WordForm]] = {}

        for lemma in lemmas:
            observed_forms = forms_map.get(lemma, [lemma])
            word_forms: list[WordForm] = []

            for form in observed_forms:
                doc = nlp(form)
                if not doc:
                    continue
                token = doc[0]
                features = self._morph_to_features(token.morph.to_dict())
                ending = NLTKStrategy._compute_ending(lemma, form)
                word_forms.append(WordForm(form=form, ending=ending, features=features))

            if not any(wf.form == lemma for wf in word_forms):
                pos = pos_map.get(lemma, PartOfSpeech.OTHER)
                word_forms.insert(
                    0,
                    WordForm(
                        form=lemma,
                        ending="",
                        features=MorphologicalFeature(
                            tense="present" if pos == PartOfSpeech.VERB else None,
                            number="singular" if pos == PartOfSpeech.NOUN else None,
                            degree="positive" if pos in (PartOfSpeech.ADJECTIVE, PartOfSpeech.ADVERB) else None,
                        ),
                    ),
                )

            results[lemma] = word_forms

        logger.info("spaCy strategy analyzed %d lemmas", len(results))
        return results

    @staticmethod
    def _morph_to_features(morph: dict[str, str]) -> MorphologicalFeature:
        """Convert spaCy morph dict to our MorphologicalFeature."""
        tense_map = {"Past": "past", "Pres": "present"}
        number_map = {"Sing": "singular", "Plur": "plural"}
        person_map = {"1": "1st", "2": "2nd", "3": "3rd"}
        degree_map = {"Pos": "positive", "Cmp": "comparative", "Sup": "superlative"}

        return MorphologicalFeature(
            tense=tense_map.get(morph.get("Tense", ""), None),
            number=number_map.get(morph.get("Number", ""), None),
            person=person_map.get(morph.get("Person", ""), None),
            degree=degree_map.get(morph.get("Degree", ""), None),
            aspect="progressive" if morph.get("Aspect") == "Prog" else None,
            voice="passive" if morph.get("Voice") == "Pass" else None,
        )


class MorphologicalAnalyzer:
    """Facade that delegates to a configurable analysis strategy.

    Args:
        strategy: The analysis strategy to use.
    """

    def __init__(self, strategy: AnalysisStrategy | None = None) -> None:
        self._strategy = strategy or NLTKStrategy()

    @property
    def strategy(self) -> AnalysisStrategy:
        return self._strategy

    @strategy.setter
    def strategy(self, value: AnalysisStrategy) -> None:
        self._strategy = value
        logger.info("Morphological strategy changed to %s", type(value).__name__)

    def analyze(
        self,
        lemmas: list[str],
        pos_map: dict[str, PartOfSpeech],
        forms_map: dict[str, list[str]],
    ) -> dict[str, list[WordForm]]:
        """Run morphological analysis on extracted lemmas.

        Args:
            lemmas: Unique lemma strings.
            pos_map: Lemma-to-POS mapping.
            forms_map: Lemma-to-observed-forms mapping.

        Returns:
            ``{lemma: [WordForm, ...]}`` for each lemma.
        """
        return self._strategy.analyze_tokens(lemmas, pos_map, forms_map)

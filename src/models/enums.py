"""Enumerations for morphological and POS classification."""

from __future__ import annotations

from enum import StrEnum


class PartOfSpeech(StrEnum):
    """Part-of-speech tags used throughout the system."""

    NOUN = "NOUN"
    VERB = "VERB"
    ADJECTIVE = "ADJ"
    ADVERB = "ADV"
    PRONOUN = "PRON"
    PREPOSITION = "ADP"
    CONJUNCTION = "CONJ"
    DETERMINER = "DET"
    INTERJECTION = "INTJ"
    NUMERAL = "NUM"
    PARTICLE = "PART"
    OTHER = "OTHER"

    @classmethod
    def from_penn(cls, tag: str) -> PartOfSpeech:
        """Convert a Penn Treebank POS tag to our enum.

        Args:
            tag: Penn Treebank tag (e.g. ``NN``, ``VBD``, ``JJ``).

        Returns:
            Corresponding ``PartOfSpeech`` member.
        """
        mapping: dict[str, PartOfSpeech] = {
            "NN": cls.NOUN, "NNS": cls.NOUN, "NNP": cls.NOUN, "NNPS": cls.NOUN,
            "VB": cls.VERB, "VBD": cls.VERB, "VBG": cls.VERB,
            "VBN": cls.VERB, "VBP": cls.VERB, "VBZ": cls.VERB,
            "JJ": cls.ADJECTIVE, "JJR": cls.ADJECTIVE, "JJS": cls.ADJECTIVE,
            "RB": cls.ADVERB, "RBR": cls.ADVERB, "RBS": cls.ADVERB,
            "PRP": cls.PRONOUN, "PRP$": cls.PRONOUN, "WP": cls.PRONOUN, "WP$": cls.PRONOUN,
            "IN": cls.PREPOSITION, "TO": cls.PREPOSITION,
            "CC": cls.CONJUNCTION,
            "DT": cls.DETERMINER, "PDT": cls.DETERMINER, "WDT": cls.DETERMINER,
            "UH": cls.INTERJECTION,
            "CD": cls.NUMERAL,
            "RP": cls.PARTICLE,
        }
        return mapping.get(tag, cls.OTHER)

    @classmethod
    def from_spacy(cls, tag: str) -> PartOfSpeech:
        """Convert a spaCy coarse POS tag to our enum.

        Args:
            tag: spaCy POS tag (e.g. ``NOUN``, ``VERB``).

        Returns:
            Corresponding ``PartOfSpeech`` member.
        """
        try:
            return cls(tag)
        except ValueError:
            return cls.OTHER


class Tense(StrEnum):
    """Verb tenses."""

    PRESENT = "present"
    PAST = "past"
    PAST_PARTICIPLE = "past_participle"
    PRESENT_PARTICIPLE = "present_participle"
    INFINITIVE = "infinitive"


class Number(StrEnum):
    """Grammatical number."""

    SINGULAR = "singular"
    PLURAL = "plural"


class Person(StrEnum):
    """Grammatical person."""

    FIRST = "1st"
    SECOND = "2nd"
    THIRD = "3rd"


class Case(StrEnum):
    """Pronoun case forms."""

    SUBJECT = "subject"
    OBJECT = "object"
    POSSESSIVE = "possessive"
    REFLEXIVE = "reflexive"


class Degree(StrEnum):
    """Adjective / adverb degree of comparison."""

    POSITIVE = "positive"
    COMPARATIVE = "comparative"
    SUPERLATIVE = "superlative"

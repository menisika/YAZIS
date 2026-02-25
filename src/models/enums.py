"""Перечисления для морфологической и POS-классификации."""

from __future__ import annotations

from enum import StrEnum


class PartOfSpeech(StrEnum):
    """Теги частей речи, используемые в системе."""

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

    def display_name(self) -> str:
        """Полное название части речи для отображения (напр. Adjective, Noun)."""
        names = {
            "NOUN": "Noun",
            "VERB": "Verb",
            "ADJ": "Adjective",
            "ADV": "Adverb",
            "PRON": "Pronoun",
            "ADP": "Preposition",
            "CONJ": "Conjunction",
            "DET": "Determiner",
            "INTJ": "Interjection",
            "NUM": "Numeral",
            "PART": "Particle",
            "OTHER": "Other",
        }
        return names.get(self.value, self.value)

    @classmethod
    def from_penn(cls, tag: str) -> PartOfSpeech:
        """Преобразовать тег Penn Treebank в наш enum.

        Аргументы:
            tag: Тег Penn Treebank (напр. NN, VBD, JJ).

        Возвращает:
            Соответствующий элемент PartOfSpeech.
        """
        mapping: dict[str, PartOfSpeech] = {
            "NN": cls.NOUN,
            "NNS": cls.NOUN,
            "NNP": cls.NOUN,
            "NNPS": cls.NOUN,
            "VB": cls.VERB,
            "VBD": cls.VERB,
            "VBG": cls.VERB,
            "VBN": cls.VERB,
            "VBP": cls.VERB,
            "VBZ": cls.VERB,
            "JJ": cls.ADJECTIVE,
            "JJR": cls.ADJECTIVE,
            "JJS": cls.ADJECTIVE,
            "RB": cls.ADVERB,
            "RBR": cls.ADVERB,
            "RBS": cls.ADVERB,
            "PRP": cls.PRONOUN,
            "PRP$": cls.PRONOUN,
            "WP": cls.PRONOUN,
            "WP$": cls.PRONOUN,
            "IN": cls.PREPOSITION,
            "TO": cls.PREPOSITION,
            "CC": cls.CONJUNCTION,
            "DT": cls.DETERMINER,
            "PDT": cls.DETERMINER,
            "WDT": cls.DETERMINER,
            "UH": cls.INTERJECTION,
            "CD": cls.NUMERAL,
            "RP": cls.PARTICLE,
        }
        return mapping.get(tag, cls.OTHER)

    @classmethod
    def from_spacy(cls, tag: str) -> PartOfSpeech:
        """Преобразовать грубый POS-тег spaCy в наш enum.

        Аргументы:
            tag: POS-тег spaCy (напр. NOUN, VERB).

        Возвращает:
            Соответствующий элемент PartOfSpeech.
        """
        try:
            return cls(tag)
        except ValueError:
            return cls.OTHER


class Tense(StrEnum):
    """Времена глагола."""

    PRESENT = "present"
    PAST = "past"
    PAST_PARTICIPLE = "past_participle"
    PRESENT_PARTICIPLE = "present_participle"
    INFINITIVE = "infinitive"


class Number(StrEnum):
    """Грамматическое число."""

    SINGULAR = "singular"
    PLURAL = "plural"


class Person(StrEnum):
    """Грамматическое лицо."""

    FIRST = "1st"
    SECOND = "2nd"
    THIRD = "3rd"


class Case(StrEnum):
    """Падежные формы местоимений."""

    SUBJECT = "subject"
    OBJECT = "object"
    POSSESSIVE = "possessive"
    REFLEXIVE = "reflexive"


class Degree(StrEnum):
    """Степень сравнения прилагательных и наречий."""

    POSITIVE = "positive"
    COMPARATIVE = "comparative"
    SUPERLATIVE = "superlative"

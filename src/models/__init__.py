"""Доменные модели системы словаря."""

from models.enums import PartOfSpeech
from models.lexeme import DictionaryEntry, MorphologicalFeature, WordForm
from models.dictionary import Dictionary, DictionaryMetadata

__all__ = [
    "PartOfSpeech",
    "DictionaryEntry",
    "MorphologicalFeature",
    "WordForm",
    "Dictionary",
    "DictionaryMetadata",
]

"""Нормализация текста и вспомогательные правила орфографии для морфологии."""

from __future__ import annotations

import re
import unicodedata

from utils.constants import CONSONANTS, VOWELS


def normalize_text(text: str) -> str:
    """Нормализовать юникод, схлопнуть пробелы, обрезать."""
    text = unicodedata.normalize("NFKD", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def is_vowel(ch: str) -> bool:
    return ch.lower() in VOWELS


def is_consonant(ch: str) -> bool:
    return ch.lower() in CONSONANTS


# Правила орфографии для английской флексии

def double_final_consonant(stem: str) -> str:
    """Удвоить конечную согласную при добавлении -ing/-ed к основам CVC.

    Примеры:
        run  -> runn
        stop -> stopp
        big  -> bigg
    """
    if len(stem) < 2:
        return stem + stem[-1] if stem and is_consonant(stem[-1]) else stem
    if (
        is_consonant(stem[-1])
        and is_vowel(stem[-2])
        and (len(stem) < 3 or is_consonant(stem[-3]))
        and stem[-1] not in ("w", "x", "y")
    ):
        return stem + stem[-1]
    return stem


def apply_e_dropping(stem: str, suffix: str) -> str:
    """Отбросить немую e перед суффиксами на гласную.

    Примеры:
        make + -ing -> making
        love + -able -> lovable
    """
    if stem.endswith("e") and suffix and is_vowel(suffix[0]):
        return stem[:-1] + suffix
    return stem + suffix


def apply_y_to_i(stem: str, suffix: str) -> str:
    """Заменить конечную -y на -i перед суффиксами (кроме -ing).

    Примеры:
        carry + -ed  -> carried
        happy + -er  -> happier
    """
    if (
        stem.endswith("y")
        and len(stem) >= 2
        and is_consonant(stem[-2])
        and suffix not in ("-ing", "ing")
        and not suffix.startswith("i")
    ):
        return stem[:-1] + "i" + suffix
    return stem + suffix


def apply_ies_rule(stem: str) -> str:
    """Применить правило множественного числа -ies для основ на согласную+y.

    Примеры:
        baby  -> babies
        carry -> carries
    """
    if stem.endswith("y") and len(stem) >= 2 and is_consonant(stem[-2]):
        return stem[:-1] + "ies"
    return stem + "s"


def apply_es_rule(stem: str) -> str:
    """Правило -es для множественного числа/3-го лица при свистящих окончаниях.

    Примеры:
        box   -> boxes
        watch -> watches
        bus   -> buses
    """
    if stem.endswith(("s", "x", "z", "ch", "sh")):
        return stem + "es"
    return stem + "s"


def strip_punctuation(token: str) -> str:
    """Удалить ведущую и конечную пунктуацию у токена."""
    return token.strip(".,;:!?\"'()[]{}…–—-/\\")

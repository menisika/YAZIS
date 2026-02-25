"""Доменные модели: MorphologicalFeature, WordForm, DictionaryEntry."""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Any

from models.enums import PartOfSpeech


@dataclass(slots=True)
class MorphologicalFeature:
    """Морфологические свойства словоформы.

    Атрибуты:
        tense: Время глагола (present, past, past_participle, present_participle).
        number: Число (singular, plural).
        person: Лицо (1st, 2nd, 3rd).
        case: Падеж местоимения (subject, object, possessive, reflexive).
        degree: Степень сравнения (positive, comparative, superlative).
        aspect: Вид (напр. progressive).
        voice: Залог (active/passive).
    """

    tense: str | None = None
    number: str | None = None
    person: str | None = None
    case: str | None = None
    degree: str | None = None
    aspect: str | None = None
    voice: str | None = None

    def to_dict(self) -> dict[str, str]:
        """Сериализовать ненулевые поля в словарь."""
        return {f.name: getattr(self, f.name) for f in fields(self) if getattr(self, f.name) is not None}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MorphologicalFeature:
        """Десериализовать из словаря, игнорируя неизвестные ключи."""
        valid_keys = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in valid_keys})

    def matches(self, **criteria: str | None) -> bool:
        """Проверить, что набор признаков удовлетворяет всем заданным критериям.

        Учитываются только критерии с непустым значением.
        """
        for key, value in criteria.items():
            if value is not None and getattr(self, key, None) != value:
                return False
        return True

    def summary(self) -> str:
        """Читаемое краткое описание признаков."""
        parts = [f"{k}={v}" for k, v in self.to_dict().items()]
        return ", ".join(parts) if parts else "base"


@dataclass(slots=True)
class WordForm:
    """Одна словоизменительная форма лексемы.

    Атрибуты:
        form: Строка словоформы (напр. running).
        ending: Окончание/суффикс основы (напр. -ning).
        features: Морфологические признаки формы.
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
    """Полная запись словаря для одной лексемы.

    Атрибуты:
        lexeme: Базовая/лемма форма (напр. run).
        stem: Морфологическая основа (напр. run).
        pos: Часть речи.
        frequency: Частота в исходном тексте.
        word_forms: Известные словоизменительные формы.
        irregular: Нерегулярная морфология.
        notes: Произвольные заметки.
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
        """Отфильтровать словоформы по морфологическим критериям."""
        return [wf for wf in self.word_forms if wf.features.matches(**criteria)]

    def add_word_form(self, word_form: WordForm) -> None:
        """Добавить словоформу, избегая точных дубликатов."""
        for existing in self.word_forms:
            if existing.form == word_form.form and existing.features.to_dict() == word_form.features.to_dict():
                return
        self.word_forms.append(word_form)

"""Интеграция с Groq API для автоматической генерации определений."""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from models.lexeme import DictionaryEntry
from utils.constants import DEFINITION_PROMPT_TEMPLATE, GROQ_MODEL
from utils.logging_config import get_logger

logger = get_logger("core.definition_service")


class DefinitionService:
    """Получает определения слов через Groq API.

    Использует клиент groq и модель qwen/qwen3-32b.
    Поддерживает одиночный и пакетный (многопоточный) запрос.

    Аргументы:
        api_key: Ключ Groq API.
    """

    def __init__(self, api_key: str = "") -> None:
        self._api_key = api_key
        self._client: Any = None

    @property
    def api_key(self) -> str:
        return self._api_key

    @api_key.setter
    def api_key(self, value: str) -> None:
        self._api_key = value
        self._client = None  # force re-creation

    def _get_client(self) -> Any:
        """Создать клиент Groq при первом обращении."""
        if self._client is None:
            if not self._api_key:
                raise RuntimeError("Groq API key is not configured")
            from groq import Groq  # type: ignore[import-untyped]
            self._client = Groq(api_key=self._api_key)
        return self._client

    def test_connection(self) -> bool:
        """Проверить ключ API минимальным запросом.

        Возвращает:
            True при успешном ответе API.
        """
        try:
            client = self._get_client()
            completion = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role": "user", "content": "Say 'ok'"}],
                max_tokens=5,
            )
            return bool(completion.choices)
        except Exception as exc:
            logger.warning("Groq connection test failed: %s", exc)
            return False

    def fetch_definition(self, word: str, pos: str) -> str:
        """Получить определение для одного слова.

        Аргументы:
            word: Слово (англ.).
            pos: Метка части речи (напр. NOUN, VERB).

        Возвращает:
            Строка определения или пустая строка при ошибке.
        """
        prompt = DEFINITION_PROMPT_TEMPLATE.format(word=word, pos=pos)
        try:
            client = self._get_client()
            completion = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a dictionary assistant. "
                            "Reply with ONLY the definition — no labels, "
                            "no examples, no thinking, no extra text."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=60,
                temperature=0.3,
            )
            content = completion.choices[0].message.content or ""
            # Убрать теги размышлений, если есть (qwen3 иногда оборачивает в <think>)
            definition = self._clean_definition(content, word)
            logger.debug("Definition for '%s' (%s): %s", word, pos, definition)
            return definition
        except Exception as exc:
            logger.warning("Failed to fetch definition for '%s': %s", word, exc)
            return ""

    def fetch_definitions_batch(
        self,
        entries: list[DictionaryEntry],
        max_workers: int = 4,
        delay: float = 0.15,
        progress_callback: Any | None = None,
    ) -> dict[str, str]:
        """Получить определения для нескольких записей параллельно.

        Аргументы:
            entries: Записи, для которых нужны определения.
            max_workers: Размер пула потоков.
            delay: Задержка между запросами (сек) для лимитов.
            progress_callback: Опционально (completed, total).

        Возвращает:
            Словарь {лексема: определение} для успешно полученных слов.
        """
        results: dict[str, str] = {}
        total = len(entries)
        completed = 0

        def _fetch_one(entry: DictionaryEntry) -> tuple[str, str]:
            nonlocal completed
            time.sleep(delay)  # simple rate limiting
            defn = self.fetch_definition(entry.lexeme, entry.pos.display_name())
            return entry.lexeme, defn

        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = {pool.submit(_fetch_one, e): e for e in entries}
            for future in as_completed(futures):
                try:
                    lexeme, defn = future.result()
                    if defn:
                        results[lexeme] = defn
                except Exception as exc:
                    entry = futures[future]
                    logger.warning("Batch fetch failed for '%s': %s", entry.lexeme, exc)
                completed += 1
                if progress_callback:
                    try:
                        progress_callback(completed, total)
                    except Exception:
                        pass

        logger.info("Batch fetched %d/%d definitions", len(results), total)
        return results

    @staticmethod
    def _clean_definition(text: str, word: str) -> str:
        """Очистить вывод модели до текста определения.

        Удаляет блоки <think>, префиксы вроде «Definition:» или «word (noun):»,
        нормализует пунктуацию.
        """
        import re

        # Удалить блоки <think>...</think>
        cleaned = re.sub(r"<think>[\s\S]*?</think>", "", text)

        # При незакрытом блоке <think> отбросить всё до конца
        if "<think>" in cleaned:
            cleaned = cleaned.split("</think>")[-1]

        cleaned = cleaned.strip()

        # Убрать типичные префиксы, которые может добавить модель
        cleaned = re.sub(
            r"^(?:definition\s*:\s*|" + re.escape(word) + r"\s*(?:\([^)]*\)\s*)?[:\-–]\s*)",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )

        # Убрать обрамляющие кавычки
        if len(cleaned) > 2 and cleaned[0] in ('"', "'") and cleaned[-1] == cleaned[0]:
            cleaned = cleaned[1:-1]

        cleaned = cleaned.strip().rstrip(".")
        if cleaned:
            cleaned += "."
        return cleaned

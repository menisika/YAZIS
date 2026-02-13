"""Groq API integration for automatic definition generation."""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from models.lexeme import DictionaryEntry
from utils.constants import DEFINITION_PROMPT_TEMPLATE, GROQ_MODEL
from utils.logging_config import get_logger

logger = get_logger("core.definition_service")


class DefinitionService:
    """Fetches word definitions via the Groq API.

    Uses the ``groq`` Python client with the qwen/qwen3-32b model.
    Supports single-word and batch (threaded) fetching.

    Args:
        api_key: Groq API key.
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
        """Lazy-create the Groq client."""
        if self._client is None:
            if not self._api_key:
                raise RuntimeError("Groq API key is not configured")
            from groq import Groq  # type: ignore[import-untyped]
            self._client = Groq(api_key=self._api_key)
        return self._client

    def test_connection(self) -> bool:
        """Validate the API key by making a minimal request.

        Returns:
            ``True`` if the API responds successfully.
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
        """Fetch a definition for a single word.

        Args:
            word: The English word.
            pos: Part of speech label (e.g. ``NOUN``, ``VERB``).

        Returns:
            The definition string, or an empty string on failure.
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
            # Strip thinking tags if present (qwen3 sometimes wraps in <think>)
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
        """Fetch definitions for multiple entries in parallel.

        Args:
            entries: Entries that need definitions.
            max_workers: Thread pool size.
            delay: Delay between requests (seconds) to respect rate limits.
            progress_callback: Optional ``(completed, total)`` callable.

        Returns:
            ``{lexeme: definition}`` mapping for successfully fetched words.
        """
        results: dict[str, str] = {}
        total = len(entries)
        completed = 0

        def _fetch_one(entry: DictionaryEntry) -> tuple[str, str]:
            nonlocal completed
            time.sleep(delay)  # simple rate limiting
            defn = self.fetch_definition(entry.lexeme, str(entry.pos))
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
        """Clean model output to extract only the definition text.

        Strips ``<think>`` blocks, removes label prefixes like
        ``Definition:`` or ``word (noun):``, and normalises punctuation.
        """
        import re

        # Remove <think>...</think> blocks (greedy within single block)
        cleaned = re.sub(r"<think>[\s\S]*?</think>", "", text)

        # If there's an unclosed <think> block, drop everything before it ends
        if "<think>" in cleaned:
            cleaned = cleaned.split("</think>")[-1]

        cleaned = cleaned.strip()

        # Remove common label prefixes the model might add
        cleaned = re.sub(
            r"^(?:definition\s*:\s*|" + re.escape(word) + r"\s*(?:\([^)]*\)\s*)?[:\-–]\s*)",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )

        # Remove surrounding quotes
        if len(cleaned) > 2 and cleaned[0] in ('"', "'") and cleaned[-1] == cleaned[0]:
            cleaned = cleaned[1:-1]

        cleaned = cleaned.strip().rstrip(".")
        if cleaned:
            cleaned += "."
        return cleaned

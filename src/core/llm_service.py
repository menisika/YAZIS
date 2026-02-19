"""Groq API integration (LLM service)."""

from __future__ import annotations

from typing import Any

from utils.constants import GROQ_MODEL
from utils.logging_config import get_logger

logger = get_logger("core.llm_service")

_TASK_PROMPT = """\
You are an expert ESL teacher specializing in grammar and word formation.

Given a list of lexemes with their parts of speech, generate practice exercises \
for each word. Use ONLY the provided part of speech — do not add sections for \
other parts of speech.

For each lexeme:
- State its part of speech (use the one provided)
- Write 3-5 fill-in-the-blank sentences requiring different grammatical forms
- Each sentence must have a blank (_____)
- Add the base form in [brackets] at the end of each sentence
- Use clear context clues (time markers, comparatives, etc.) so only one form is correct

Rules by part of speech:
- Verbs: vary tenses, include passive and participle forms
- Nouns: test plural, possessive, countability
- Adjectives/Adverbs: test comparative and superlative
- Optionally: include one word-formation sentence (e.g., noun to adjective)

End with a complete Answer Key as a numbered list of answers only (e.g. "1. ran  2. has been taken"), one answer per item — no sentences, no explanations.

Lexemes:
{words}\
/no_think
"""

_POS_LABELS: dict[str, str] = {
    "NOUN": "noun",
    "VERB": "verb",
    "ADJ": "adjective",
    "ADV": "adverb",
    "PRON": "pronoun",
    "ADP": "preposition",
    "CONJ": "conjunction",
    "DET": "determiner",
    "INTJ": "interjection",
    "NUM": "numeral",
    "PART": "particle",
    "OTHER": "other",
}


class LLMService:
    """Groq API client for LLM access.

    Provides connection to Groq API (e.g. for future prompts).
    Uses the ``groq`` Python client.

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

    def generate_task(self, words: list[tuple[str, str]]) -> str:
        """Generate ESL fill-in-the-blank exercises for the given lexemes.

        Args:
            words: List of ``(lexeme, pos)`` pairs where *pos* is a
                :class:`PartOfSpeech` string value (e.g. ``"VERB"``).

        Returns:
            The model's response text containing exercises and answer key.

        Raises:
            RuntimeError: If the API key is not configured.
        """
        word_lines = "\n".join(
            f"- {lexeme} ({_POS_LABELS.get(pos, pos.lower())})" for lexeme, pos in words
        )
        prompt = _TASK_PROMPT.format(words=word_lines)
        client = self._get_client()
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        return (completion.choices[0].message.content or "").strip()

from __future__ import annotations

import os
import sys
from pathlib import Path
from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[2]  # lab_2/
ENV_FILE = ROOT_DIR / ".env"

DEFAULT_ENV_CONTENT = """\
DATABASE_URL=postgresql+asyncpg://corpus:corpus@localhost:5432/corpus_db
SPACY_MODEL=en_core_web_sm
EMBEDDING_MODEL=all-MiniLM-L6-v2
CORS_ORIGINS=["http://localhost:5173"]
API_HOST=0.0.0.0
API_PORT=8000
MAX_UPLOAD_SIZE_MB=50
EMBEDDING_DIM=384
POSTGRES_DB=corpus_db
POSTGRES_USER=corpus
POSTGRES_PASSWORD=corpus
"""


def ensure_env_file() -> None:
    """Write default .env if missing or empty, and notify the user."""
    if not ENV_FILE.exists() or ENV_FILE.stat().st_size == 0:
        ENV_FILE.write_text(DEFAULT_ENV_CONTENT)
        print(
            f"[corpus-manager] No .env found — created one with defaults at {ENV_FILE}\n"
            "  Edit it to customise database credentials, models, or ports.\n",
            file=sys.stderr,
        )


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    database_url: str = "postgresql+asyncpg://corpus:corpus@localhost:5432/corpus_db"

    # NLP
    spacy_model: str = "en_core_web_sm"
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dim: int = 384

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: List[str] = ["http://localhost:5173"]

    # Upload limits
    max_upload_size_mb: int = 50

    # Docker / Postgres (used by docker-compose only, not the app directly)
    postgres_db: str = "corpus_db"
    postgres_user: str = "corpus"
    postgres_password: str = "corpus"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors(cls, v: object) -> object:
        if isinstance(v, str):
            import json
            return json.loads(v)
        return v


@lru_cache
def get_settings() -> Settings:
    ensure_env_file()
    return Settings()

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/syntactic_analysis"
    spacy_model: str = "en_core_web_lg"
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    max_upload_size: int = 52428800  # 50 MB
    supported_extensions: list[str] = [".pdf", ".docx", ".rtf", ".txt"]


settings = Settings()

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://fitness:fitness_secret@db:5432/fitness_planner"
    groq_api_key: str = ""
    firebase_project_id: str = ""
    firebase_service_account_key: str = ""  # JSON string of the service account key (optional)
    firebase_service_account_key_path: str = "firebase_service_key.json"
    youtube_api_key: str = ""
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()

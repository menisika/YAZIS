import uvicorn

from app.config.settings import Settings


if __name__ == "__main__":
    settings = Settings()
    uvicorn.run("app.main:app", host=settings.api_host, port=settings.api_port, reload=False)

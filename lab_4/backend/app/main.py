from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import Settings
from app.db.session import _init_db
from app.routers import documents, patterns, semantic, sentences, tokens
from app.services.nlp_service import load_model


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    import nltk
    nltk.download("wordnet", quiet=True)
    nltk.download("omw-1.4", quiet=True)
    settings = Settings()
    _init_db(settings.database_url)
    load_model(settings.spacy_model)
    yield


def create_app() -> FastAPI:
    settings = Settings()
    app = FastAPI(title="Syntactic Analysis API", version="1.0.0", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(documents.router, prefix="/api")
    app.include_router(sentences.router, prefix="/api")
    app.include_router(tokens.router, prefix="/api")
    app.include_router(patterns.router, prefix="/api")
    app.include_router(semantic.router, prefix="/api")

    return app


app = create_app()

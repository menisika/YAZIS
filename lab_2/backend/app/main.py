"""FastAPI application entry point."""
from __future__ import annotations

import sys
import os

# Make sure backend/ is on the path for local runs
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import get_settings
from app.routers import corpus, search, frequency, morphology, semantic, style

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pre-load NLP model on startup to avoid first-request latency
    from app.utils.nlp import get_nlp
    get_nlp(settings.spacy_model)
    yield


app = FastAPI(
    title="Corpus Manager API",
    version="1.0.0",
    description="API for corpus management, linguistic analysis, and semantic search",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PREFIX = "/api/v1"
app.include_router(corpus.router, prefix=PREFIX)
app.include_router(search.router, prefix=PREFIX)
app.include_router(frequency.router, prefix=PREFIX)
app.include_router(morphology.router, prefix=PREFIX)
app.include_router(semantic.router, prefix=PREFIX)
app.include_router(style.router, prefix=PREFIX)


@app.get("/health")
async def health():
    return {"status": "ok"}

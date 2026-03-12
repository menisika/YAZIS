# Corpus Manager

A full-stack web application for building, querying, and analysing a corpus of English literary texts.

## Tech Stack

| Layer | Technology |
|---|---|
| Database | PostgreSQL 16 + pgvector (Docker) |
| Backend | Python 3.12, FastAPI, SQLAlchemy 2 (async), Alembic |
| NLP | spaCy (`en_core_web_sm`), sentence-transformers (`all-MiniLM-L6-v2`) |
| Frontend | React 18, TypeScript, Vite, Tailwind CSS, TanStack Query, Zustand, Recharts |

## Quick Start

### 1. Start PostgreSQL

```bash
docker compose up -d
```

### 2. Set up the backend

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Run migrations (creates all tables)
alembic upgrade head

# Start the API server
python run.py
# → http://localhost:8000
# → API docs at http://localhost:8000/docs
```

> On first run, a `.env` file is created automatically with sensible defaults.  
> Edit it to change database credentials, ports, or model names.

### 3. Set up the frontend

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

## Features

| Feature | Description |
|---|---|
| **Corpus Browser** | Upload TXT/PDF/DOCX/RTF files; view paginated text list with metadata |
| **Annotated Reader** | Read any text with hover tooltips showing lemma + POS + morphology |
| **Concordance / KWIC** | Key-word-in-context search with configurable context window; sortable |
| **Frequency Analysis** | Word/lemma/POS frequency lookup; top-N bar charts; word cloud |
| **Morphology Cards** | Full grammar card for any lemma: all attested forms, morphological features, examples |
| **Semantic Search** | Natural-language passage retrieval via pgvector cosine similarity |
| **Style Lab** | Compare 2–4 texts: radar charts for POS profiles, MTLD, TTR, Flesch-Kincaid, distinctive vocabulary |

## Configuration

All settings are read from `.env` (auto-generated on first run):

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://corpus:corpus@localhost:5432/corpus_db` | Async DB URL |
| `SPACY_MODEL` | `en_core_web_sm` | spaCy model name |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | sentence-transformers model |
| `EMBEDDING_DIM` | `384` | Embedding vector dimension |
| `API_HOST` | `0.0.0.0` | Uvicorn host |
| `API_PORT` | `8000` | Uvicorn port |
| `CORS_ORIGINS` | `["http://localhost:5173"]` | Allowed CORS origins |
| `MAX_UPLOAD_SIZE_MB` | `50` | Max upload file size |

## Project Structure

```
lab_2/
├── docker-compose.yml        # PostgreSQL 16 + pgvector
├── .env                      # Auto-generated config
├── backend/
│   ├── config/settings.py    # pydantic-settings configuration
│   ├── app/
│   │   ├── main.py           # FastAPI app + CORS + routers
│   │   ├── database.py       # Async SQLAlchemy engine
│   │   ├── dependencies.py   # DI providers
│   │   ├── models/           # SQLAlchemy ORM (5 tables)
│   │   ├── schemas/          # Pydantic DTOs
│   │   ├── routers/          # 6 API routers
│   │   ├── services/         # Business logic layer
│   │   └── utils/            # File parsers, NLP pipeline
│   ├── alembic/              # Database migrations
│   └── requirements.txt
└── frontend/
    └── src/
        ├── api/              # TanStack Query hooks
        ├── components/       # Shared UI components
        ├── pages/            # 7 page components
        └── stores/           # Zustand UI state
```

## API Overview

All endpoints are under `/api/v1`. Interactive docs at `http://localhost:8000/docs`.

| Router | Endpoints |
|---|---|
| `corpus` | `GET/POST /texts`, `GET/DELETE /texts/{id}`, `GET /texts/{id}/content` |
| `search` | `GET /search?q=&field=surface|lemma&context=5` |
| `frequency` | `GET /frequency?q=`, `GET /frequency/top?n=20` |
| `morphology` | `GET /morphology/{lemma}` |
| `semantic` | `GET /semantic/search?q=` |
| `style` | `GET /style/texts/{id}`, `GET /style/compare?text_ids=1,2,3` |

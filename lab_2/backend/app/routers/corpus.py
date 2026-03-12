"""Corpus management endpoints."""
from __future__ import annotations

from typing import Optional, Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_settings_dep
from app.utils.file_parsers import extract_text
from app.services import corpus as corpus_svc
from app.services import ingestion as ingestion_svc
from config.settings import Settings

router = APIRouter(prefix="/texts", tags=["corpus"])


@router.get("")
async def list_texts(
    search: Optional[str] = Query(None),
    genre: Optional[str] = Query(None),
    author: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    return await corpus_svc.list_texts(db, search=search, genre=genre, author=author, page=page, page_size=page_size)


@router.get("/{text_id}")
async def get_text(text_id: int, db: AsyncSession = Depends(get_db)):
    text = await corpus_svc.get_text(db, text_id)
    if not text:
        raise HTTPException(404, "Text not found")
    return corpus_svc._text_summary(text)


@router.delete("/{text_id}")
async def delete_text(text_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await corpus_svc.delete_text(db, text_id)
    if not deleted:
        raise HTTPException(404, "Text not found")
    return {"deleted": True}


@router.get("/{text_id}/content")
async def get_annotated_content(
    text_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(500, ge=1, le=2000),
    db: AsyncSession = Depends(get_db),
):
    result = await corpus_svc.get_annotated_content(db, text_id, page=page, page_size=page_size)
    if not result:
        raise HTTPException(404, "Text not found")
    return result


@router.post("/upload")
async def upload_text(
    file: UploadFile = File(...),
    title: str = Form(...),
    author: Optional[str] = Form(None),
    year: Optional[int] = Form(None),
    genre: Optional[str] = Form(None),
    source_url: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings_dep),
):
    """Upload and ingest a text file. Returns SSE stream with progress events."""
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if file.size and file.size > max_bytes:
        raise HTTPException(413, f"File exceeds {settings.max_upload_size_mb} MB limit")

    raw_text = await extract_text(file)
    if not raw_text.strip():
        raise HTTPException(422, "Extracted text is empty")

    gen = await ingestion_svc.ingest_text(
        db=db,
        settings=settings,
        title=title,
        author=author,
        year=year,
        genre=genre,
        source_url=source_url,
        raw_text=raw_text,
    )

    return StreamingResponse(gen, media_type="text/event-stream")

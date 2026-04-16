import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import Settings
from app.db.session import get_db
from app.repositories.document_repo import DocumentRepository
from app.schemas.document import DocumentResponse
from app.schemas.processing import ProcessingSummary
from app.services.document_service import process_upload

router = APIRouter(prefix="/documents", tags=["documents"])


def get_settings() -> Settings:
    return Settings()


@router.post("/upload", response_model=ProcessingSummary, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> ProcessingSummary:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required.")

    ext = Path(file.filename).suffix.lower()
    if ext not in settings.supported_extensions:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type '{ext}'. Supported: {settings.supported_extensions}",
        )

    content = await file.read()
    if len(content) > settings.max_upload_size:
        raise HTTPException(status_code=413, detail="File too large.")

    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)

    try:
        summary = await process_upload(
            db,
            file_path=tmp_path,
            filename=file.filename,
            ext=ext,
        )
    finally:
        tmp_path.unlink(missing_ok=True)

    return summary


@router.get("", response_model=dict)
async def list_documents(
    offset: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
) -> dict:
    repo = DocumentRepository(db)
    items, total = await repo.list_with_stats(offset=offset, limit=limit)
    return {"total": total, "items": [i.model_dump() for i in items]}


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
) -> DocumentResponse:
    repo = DocumentRepository(db)
    doc = await repo.get(document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    return DocumentResponse.model_validate(doc)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    repo = DocumentRepository(db)
    deleted = await repo.delete(document_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found.")
    await db.commit()

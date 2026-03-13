from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.sentence import Sentence
from app.schemas.document import DocumentListItem


class DocumentRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self,
        *,
        filename: str,
        original_format: str,
        raw_text: str,
        word_count: int,
        sentence_count: int,
    ) -> Document:
        doc = Document(
            filename=filename,
            original_format=original_format,
            raw_text=raw_text,
            word_count=word_count,
            sentence_count=sentence_count,
        )
        self.db.add(doc)
        await self.db.flush()
        return doc

    async def get(self, document_id: int) -> Document | None:
        result = await self.db.execute(select(Document).where(Document.id == document_id))
        return result.scalar_one_or_none()

    async def list_with_stats(self, offset: int = 0, limit: int = 20) -> tuple[list[DocumentListItem], int]:
        # Total count
        count_result = await self.db.execute(select(func.count()).select_from(Document))
        total = count_result.scalar_one()

        # Documents with aggregated sentence/token stats
        stmt = (
            select(
                Document.id,
                Document.filename,
                Document.original_format,
                Document.uploaded_at,
                Document.word_count,
                Document.sentence_count,
                func.coalesce(func.avg(Sentence.complexity_score), 0.0).label("avg_complexity"),
                func.coalesce(func.sum(Sentence.token_count), 0).label("total_tokens"),
            )
            .outerjoin(Sentence, Sentence.document_id == Document.id)
            .group_by(Document.id)
            .order_by(Document.uploaded_at.desc())
            .offset(offset)
            .limit(limit)
        )
        rows = await self.db.execute(stmt)
        items = [
            DocumentListItem(
                id=row.id,
                filename=row.filename,
                original_format=row.original_format,
                uploaded_at=row.uploaded_at,
                word_count=row.word_count,
                sentence_count=row.sentence_count,
                avg_complexity=float(row.avg_complexity),
                total_tokens=int(row.total_tokens),
            )
            for row in rows
        ]
        return items, total

    async def delete(self, document_id: int) -> bool:
        result = await self.db.execute(delete(Document).where(Document.id == document_id))
        await self.db.flush()
        return result.rowcount > 0

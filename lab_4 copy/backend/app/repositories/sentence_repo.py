from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.sentence import Sentence


class SentenceRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def bulk_create(self, sentences: list[Sentence]) -> None:
        self.db.add_all(sentences)
        await self.db.flush()

    async def get(self, sentence_id: int, *, with_tokens: bool = False) -> Sentence | None:
        stmt = select(Sentence).where(Sentence.id == sentence_id)
        if with_tokens:
            stmt = stmt.options(selectinload(Sentence.tokens))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_for_document(
        self,
        document_id: int,
        *,
        offset: int = 0,
        limit: int = 50,
        min_complexity: float | None = None,
        max_complexity: float | None = None,
        keyword: str | None = None,
    ) -> tuple[list[Sentence], int]:
        conditions = [Sentence.document_id == document_id]
        if min_complexity is not None:
            conditions.append(Sentence.complexity_score >= min_complexity)
        if max_complexity is not None:
            conditions.append(Sentence.complexity_score <= max_complexity)
        if keyword:
            conditions.append(Sentence.text.ilike(f"%{keyword}%"))

        where_clause = and_(*conditions)

        from sqlalchemy import func
        count_result = await self.db.execute(
            select(func.count()).select_from(Sentence).where(where_clause)
        )
        total = count_result.scalar_one()

        stmt = (
            select(Sentence)
            .where(where_clause)
            .order_by(Sentence.index)
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def get_all_for_document(self, document_id: int) -> list[Sentence]:
        """Fetch all sentences ordered by index — used for heatmap."""
        stmt = select(Sentence).where(Sentence.document_id == document_id).order_by(Sentence.index)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

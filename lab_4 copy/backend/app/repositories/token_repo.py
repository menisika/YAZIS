from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.token import Token


class TokenRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def bulk_create(self, tokens: list[Token]) -> None:
        self.db.add_all(tokens)
        await self.db.flush()

    async def get_for_sentence(self, sentence_id: int) -> list[Token]:
        stmt = select(Token).where(Token.sentence_id == sentence_id).order_by(Token.index)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

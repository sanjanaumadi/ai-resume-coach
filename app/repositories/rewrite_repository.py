import uuid

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rewrite import Rewrite


class RewriteRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, rewrite: Rewrite) -> Rewrite:
        self.db.add(rewrite)
        await self.db.commit()
        await self.db.refresh(rewrite)
        return rewrite

    async def list_for_user(self, user_id: uuid.UUID) -> list[Rewrite]:
        result = await self.db.execute(
            select(Rewrite).where(Rewrite.user_id == user_id).order_by(desc(Rewrite.created_at))
        )
        return list(result.scalars().all())

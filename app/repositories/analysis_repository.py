import uuid

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analysis import Analysis


class AnalysisRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, analysis: Analysis) -> Analysis:
        self.db.add(analysis)
        await self.db.commit()
        await self.db.refresh(analysis)
        return analysis

    async def get_by_id(self, analysis_id: uuid.UUID, user_id: uuid.UUID) -> Analysis | None:
        result = await self.db.execute(
            select(Analysis).where(Analysis.id == analysis_id, Analysis.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def list_for_user(self, user_id: uuid.UUID) -> list[Analysis]:
        result = await self.db.execute(
            select(Analysis).where(Analysis.user_id == user_id).order_by(desc(Analysis.created_at))
        )
        return list(result.scalars().all())

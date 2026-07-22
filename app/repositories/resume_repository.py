import uuid

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.resume import Resume


class ResumeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, resume: Resume) -> Resume:
        self.db.add(resume)
        await self.db.commit()
        await self.db.refresh(resume)
        return resume

    async def get_by_id(self, resume_id: uuid.UUID, user_id: uuid.UUID) -> Resume | None:
        result = await self.db.execute(
            select(Resume).where(Resume.id == resume_id, Resume.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def list_for_user(self, user_id: uuid.UUID) -> list[Resume]:
        result = await self.db.execute(
            select(Resume).where(Resume.user_id == user_id).order_by(desc(Resume.created_at))
        )
        return list(result.scalars().all())

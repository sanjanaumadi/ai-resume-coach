import uuid

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.interview import InterviewSession


class InterviewRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, session: InterviewSession) -> InterviewSession:
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def get_by_id(self, session_id: uuid.UUID, user_id: uuid.UUID) -> InterviewSession | None:
        result = await self.db.execute(
            select(InterviewSession).where(
                InterviewSession.id == session_id, InterviewSession.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def list_for_user(self, user_id: uuid.UUID) -> list[InterviewSession]:
        result = await self.db.execute(
            select(InterviewSession)
            .where(InterviewSession.user_id == user_id)
            .order_by(desc(InterviewSession.created_at))
        )
        return list(result.scalars().all())

    async def save(self, session: InterviewSession) -> InterviewSession:
        await self.db.commit()
        await self.db.refresh(session)
        return session

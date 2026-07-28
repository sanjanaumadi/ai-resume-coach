import uuid

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.career_suggestion import CareerSuggestion


class CareerSuggestionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, suggestion: CareerSuggestion) -> CareerSuggestion:
        self.db.add(suggestion)
        await self.db.commit()
        await self.db.refresh(suggestion)
        return suggestion

    async def get_by_id(self, suggestion_id: uuid.UUID, user_id: uuid.UUID) -> CareerSuggestion | None:
        result = await self.db.execute(
            select(CareerSuggestion).where(
                CareerSuggestion.id == suggestion_id, CareerSuggestion.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def list_for_user(self, user_id: uuid.UUID) -> list[CareerSuggestion]:
        result = await self.db.execute(
            select(CareerSuggestion)
            .where(CareerSuggestion.user_id == user_id)
            .order_by(desc(CareerSuggestion.created_at))
        )
        return list(result.scalars().all())

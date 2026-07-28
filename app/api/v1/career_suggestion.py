from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.career_suggestion_repository import CareerSuggestionRepository
from app.repositories.resume_repository import ResumeRepository
from app.schemas.career_suggestion import (
    CareerSuggestionListResponse,
    CareerSuggestionResponse,
    CareerSuggestionsRequest,
)
from app.services.career_suggestion_service import CareerSuggestionService

router = APIRouter(prefix="/career-suggestions", tags=["Career Suggestions"])


def get_career_service(db: AsyncSession = Depends(get_db)) -> CareerSuggestionService:
    return CareerSuggestionService(CareerSuggestionRepository(db), ResumeRepository(db))


@router.post("", response_model=CareerSuggestionResponse, status_code=201)
async def generate_career_suggestions(
    payload: CareerSuggestionsRequest,
    current_user: User = Depends(get_current_user),
    service: CareerSuggestionService = Depends(get_career_service),
):
    return await service.generate_suggestions(current_user.id, payload.resume_id, payload.target_role)


@router.get("", response_model=CareerSuggestionListResponse)
async def list_career_suggestions(
    current_user: User = Depends(get_current_user),
    service: CareerSuggestionService = Depends(get_career_service),
):
    suggestions = await service.list_suggestions(current_user.id)
    return CareerSuggestionListResponse(suggestions=suggestions, total=len(suggestions))

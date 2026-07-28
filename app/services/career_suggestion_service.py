import uuid

from app.models.career_suggestion import CareerSuggestion
from app.repositories.career_suggestion_repository import CareerSuggestionRepository
from app.repositories.resume_repository import ResumeRepository
from app.services.career_prompts import build_career_suggestions_prompt, parse_career_suggestions_response
from app.services.gemini_client import generate_text
from app.services.resume_service import ResumeNotFoundError
from app.utils.logger import get_logger

logger = get_logger(__name__)


class CareerSuggestionService:
    def __init__(self, suggestion_repo: CareerSuggestionRepository, resume_repo: ResumeRepository):
        self.suggestion_repo = suggestion_repo
        self.resume_repo = resume_repo

    async def generate_suggestions(
        self, user_id: uuid.UUID, resume_id: uuid.UUID, target_role: str | None
    ) -> CareerSuggestion:
        resume = await self.resume_repo.get_by_id(resume_id, user_id)
        if not resume:
            raise ResumeNotFoundError("Resume not found")

        prompt = build_career_suggestions_prompt(resume.extracted_text, target_role)
        raw_response = generate_text(prompt, temperature=0.5)
        result = parse_career_suggestions_response(raw_response)

        suggestion = CareerSuggestion(
            user_id=user_id,
            resume_id=resume_id,
            target_role=target_role,
            result=result,
        )
        suggestion = await self.suggestion_repo.create(suggestion)
        logger.info("Career suggestions generated: user=%s resume=%s", user_id, resume_id)
        return suggestion

    async def list_suggestions(self, user_id: uuid.UUID) -> list[CareerSuggestion]:
        return await self.suggestion_repo.list_for_user(user_id)

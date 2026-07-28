import uuid

from app.models.rewrite import Rewrite
from app.repositories.resume_repository import ResumeRepository
from app.repositories.rewrite_repository import RewriteRepository
from app.services.gemini_client import generate_text
from app.services.resume_service import ResumeNotFoundError
from app.services.rewrite_prompts import RewriteSection, build_prompt
from app.utils.logger import get_logger

logger = get_logger(__name__)


class RewriteService:
    def __init__(self, rewrite_repo: RewriteRepository, resume_repo: ResumeRepository):
        self.rewrite_repo = rewrite_repo
        self.resume_repo = resume_repo

    async def rewrite_section(
        self,
        user_id: uuid.UUID,
        resume_id: uuid.UUID,
        section: RewriteSection,
        text: str,
        job_description: str | None,
    ) -> Rewrite:
        # Confirm the resume belongs to this user before spending an API call on their behalf
        resume = await self.resume_repo.get_by_id(resume_id, user_id)
        if not resume:
            raise ResumeNotFoundError("Resume not found")

        prompt = build_prompt(section, text, job_description)
        rewritten_text = generate_text(prompt)

        rewrite = Rewrite(
            user_id=user_id,
            resume_id=resume_id,
            section=section,
            original_text=text,
            rewritten_text=rewritten_text,
            job_description=job_description,
        )
        rewrite = await self.rewrite_repo.create(rewrite)
        logger.info("Rewrite generated: user=%s resume=%s section=%s", user_id, resume_id, section)
        return rewrite

    async def list_rewrites(self, user_id: uuid.UUID) -> list[Rewrite]:
        return await self.rewrite_repo.list_for_user(user_id)

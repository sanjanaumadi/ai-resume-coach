import uuid

from app.models.analysis import Analysis
from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.resume_repository import ResumeRepository
from app.services.ats_analyzer import analyze_resume
from app.services.resume_service import ResumeNotFoundError
from app.utils.exceptions import AppError
from app.utils.logger import get_logger

logger = get_logger(__name__)


class AnalysisNotFoundError(AppError):
    status_code = 404


def _try_add_semantic_similarity(result: dict, resume_text: str, job_description: str | None) -> None:
    """Adds a semantic_similarity score to result['jd_match'] if sentence-transformers
    is installed. Silently no-ops otherwise - semantic matching is an enhancement on top
    of keyword matching, not a hard requirement, so its absence should never break analysis."""
    if not job_description or not result.get("jd_match"):
        return
    try:
        from app.services.semantic_matcher import compute_semantic_similarity
        result["jd_match"]["semantic_similarity"] = compute_semantic_similarity(resume_text, job_description)
    except ImportError:
        logger.info("sentence-transformers not installed - skipping semantic similarity score")
        result["jd_match"]["semantic_similarity"] = None


class AnalysisService:
    def __init__(self, analysis_repo: AnalysisRepository, resume_repo: ResumeRepository):
        self.analysis_repo = analysis_repo
        self.resume_repo = resume_repo

    async def run_analysis(
        self, user_id: uuid.UUID, resume_id: uuid.UUID, job_description: str | None
    ) -> Analysis:
        resume = await self.resume_repo.get_by_id(resume_id, user_id)
        if not resume:
            raise ResumeNotFoundError("Resume not found")

        result = analyze_resume(resume.extracted_text, job_description)
        _try_add_semantic_similarity(result, resume.extracted_text, job_description)

        analysis = Analysis(
            user_id=user_id,
            resume_id=resume_id,
            job_description=job_description,
            ats_score=result["ats_score"],
            result=result,
        )
        analysis = await self.analysis_repo.create(analysis)
        logger.info("Analysis run: user=%s resume=%s score=%d", user_id, resume_id, result["ats_score"])
        return analysis

    async def get_analysis(self, analysis_id: uuid.UUID, user_id: uuid.UUID) -> Analysis:
        analysis = await self.analysis_repo.get_by_id(analysis_id, user_id)
        if not analysis:
            raise AnalysisNotFoundError("Analysis not found")
        return analysis

    async def list_analyses(self, user_id: uuid.UUID) -> list[Analysis]:
        return await self.analysis_repo.list_for_user(user_id)

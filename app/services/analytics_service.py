import uuid

from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.interview_repository import InterviewRepository
from app.repositories.resume_repository import ResumeRepository
from app.services.analytics import AnalyticsSummary, build_analytics_summary


class AnalyticsService:
    def __init__(
        self,
        analysis_repo: AnalysisRepository,
        interview_repo: InterviewRepository,
        resume_repo: ResumeRepository,
    ):
        self.analysis_repo = analysis_repo
        self.interview_repo = interview_repo
        self.resume_repo = resume_repo

    async def get_summary(self, user_id: uuid.UUID) -> AnalyticsSummary:
        resumes = await self.resume_repo.list_for_user(user_id)
        analyses = await self.analysis_repo.list_for_user(user_id)
        sessions = await self.interview_repo.list_for_user(user_id)

        analyses_data = [{"ats_score": a.ats_score, "created_at": a.created_at, "result": a.result} for a in analyses]
        sessions_data = [
            {"status": s.status, "final_report": s.final_report, "created_at": s.created_at} for s in sessions
        ]

        return build_analytics_summary(
            resume_count=len(resumes),
            analyses=analyses_data,
            interview_sessions=sessions_data,
        )

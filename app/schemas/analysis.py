import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AnalyzeRequest(BaseModel):
    resume_id: uuid.UUID
    job_description: str | None = Field(default=None, max_length=10000)


class JDMatchResult(BaseModel):
    jd_skills_found: list[str]
    missing_skills: list[str]
    match_percentage: int
    semantic_similarity: int | None = None


class AnalysisResult(BaseModel):
    ats_score: int
    matched_skills: list[str]
    sections_found: dict[str, bool]
    contact_info: dict[str, bool]
    formatting_issues: list[str]
    recommendations: list[str]
    jd_match: JDMatchResult | None = None


class AnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    resume_id: uuid.UUID
    ats_score: int
    result: AnalysisResult
    created_at: datetime


class AnalysisListResponse(BaseModel):
    analyses: list[AnalysisResponse]
    total: int

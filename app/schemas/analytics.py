from pydantic import BaseModel


class ScorePointSchema(BaseModel):
    date: str
    score: int


class SkillFrequencySchema(BaseModel):
    skill: str
    count: int


class AnalyticsSummaryResponse(BaseModel):
    ats_score_trend: list[ScorePointSchema]
    interview_score_trend: list[ScorePointSchema]
    skills_frequency: list[SkillFrequencySchema]
    total_resumes: int
    total_analyses: int
    total_interviews: int
    latest_ats_score: int | None
    latest_interview_score: int | None

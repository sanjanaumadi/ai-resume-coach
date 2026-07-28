import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CareerSuggestionsRequest(BaseModel):
    resume_id: uuid.UUID
    target_role: str | None = Field(default=None, max_length=200)


class LearningStepOut(BaseModel):
    skill: str
    reason: str


class CareerSuggestionsResult(BaseModel):
    suitable_roles: list[str]
    missing_technologies: list[str]
    learning_roadmap: list[LearningStepOut]
    resume_readiness_score: int
    readiness_summary: str


class CareerSuggestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    resume_id: uuid.UUID
    result: CareerSuggestionsResult
    created_at: datetime


class CareerSuggestionListResponse(BaseModel):
    suggestions: list[CareerSuggestionResponse]
    total: int

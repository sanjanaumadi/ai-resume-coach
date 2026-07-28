import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.services.rewrite_prompts import RewriteSection


class RewriteRequest(BaseModel):
    resume_id: uuid.UUID
    section: RewriteSection
    text: str = Field(min_length=10, max_length=5000)
    job_description: str | None = Field(default=None, max_length=10000)


class RewriteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    resume_id: uuid.UUID
    section: str
    original_text: str
    rewritten_text: str
    created_at: datetime


class RewriteListResponse(BaseModel):
    rewrites: list[RewriteResponse]
    total: int

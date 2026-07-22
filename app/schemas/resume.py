import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ResumeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    original_filename: str
    file_type: str
    file_size_bytes: int
    char_count: int
    created_at: datetime


class ResumeDetailResponse(ResumeResponse):
    extracted_text: str


class ResumeListResponse(BaseModel):
    resumes: list[ResumeResponse]
    total: int

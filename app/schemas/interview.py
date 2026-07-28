import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class StartInterviewRequest(BaseModel):
    resume_id: uuid.UUID
    job_description: str | None = Field(default=None, max_length=10000)


class QuestionOut(BaseModel):
    id: str
    category: str
    question: str


class SubmitAnswerRequest(BaseModel):
    question_id: str
    answer: str = Field(min_length=1, max_length=5000)


class AnswerFeedback(BaseModel):
    question_id: str
    answer: str
    communication_score: int
    technical_accuracy_score: int
    relevance_score: int
    feedback: str
    suggested_improvement: str


class FinalReport(BaseModel):
    avg_communication_score: int
    avg_technical_accuracy_score: int
    avg_relevance_score: int
    overall_score: int
    questions_answered: int
    questions_total: int


class InterviewSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    resume_id: uuid.UUID
    status: str
    questions: list[QuestionOut]
    answers: list[AnswerFeedback]
    final_report: FinalReport | None
    created_at: datetime


class InterviewListResponse(BaseModel):
    sessions: list[InterviewSessionResponse]
    total: int

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.interview_repository import InterviewRepository
from app.repositories.resume_repository import ResumeRepository
from app.schemas.interview import (
    InterviewListResponse,
    InterviewSessionResponse,
    StartInterviewRequest,
    SubmitAnswerRequest,
)
from app.services.interview_service import InterviewService

router = APIRouter(prefix="/interview", tags=["Mock Interview"])


def get_interview_service(db: AsyncSession = Depends(get_db)) -> InterviewService:
    return InterviewService(InterviewRepository(db), ResumeRepository(db))


@router.post("", response_model=InterviewSessionResponse, status_code=201)
async def start_interview(
    payload: StartInterviewRequest,
    current_user: User = Depends(get_current_user),
    service: InterviewService = Depends(get_interview_service),
):
    return await service.start_interview(current_user.id, payload.resume_id, payload.job_description)


@router.post("/{session_id}/answer", response_model=InterviewSessionResponse)
async def submit_answer(
    session_id: uuid.UUID,
    payload: SubmitAnswerRequest,
    current_user: User = Depends(get_current_user),
    service: InterviewService = Depends(get_interview_service),
):
    return await service.submit_answer(current_user.id, session_id, payload.question_id, payload.answer)


@router.post("/{session_id}/finish", response_model=InterviewSessionResponse)
async def finish_interview(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: InterviewService = Depends(get_interview_service),
):
    return await service.finish_interview(current_user.id, session_id)


@router.get("", response_model=InterviewListResponse)
async def list_interviews(
    current_user: User = Depends(get_current_user),
    service: InterviewService = Depends(get_interview_service),
):
    sessions = await service.list_sessions(current_user.id)
    return InterviewListResponse(sessions=sessions, total=len(sessions))


@router.get("/{session_id}", response_model=InterviewSessionResponse)
async def get_interview(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: InterviewService = Depends(get_interview_service),
):
    return await service.get_session(current_user.id, session_id)

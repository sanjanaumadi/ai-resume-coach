import uuid

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.resume_repository import ResumeRepository
from app.schemas.resume import ResumeDetailResponse, ResumeListResponse, ResumeResponse
from app.services.resume_service import ResumeService

router = APIRouter(prefix="/resumes", tags=["Resumes"])


def get_resume_service(db: AsyncSession = Depends(get_db)) -> ResumeService:
    return ResumeService(ResumeRepository(db))


@router.post("/upload", response_model=ResumeDetailResponse, status_code=201)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    service: ResumeService = Depends(get_resume_service),
):
    file_bytes = await file.read()
    resume = await service.upload_and_extract(current_user.id, file.filename, file_bytes)
    return resume


@router.get("", response_model=ResumeListResponse)
async def list_resumes(
    current_user: User = Depends(get_current_user),
    service: ResumeService = Depends(get_resume_service),
):
    resumes = await service.list_resumes(current_user.id)
    return ResumeListResponse(resumes=resumes, total=len(resumes))


@router.get("/{resume_id}", response_model=ResumeDetailResponse)
async def get_resume(
    resume_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: ResumeService = Depends(get_resume_service),
):
    return await service.get_resume(resume_id, current_user.id)

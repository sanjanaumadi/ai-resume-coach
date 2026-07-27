import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.resume_repository import ResumeRepository
from app.schemas.analysis import AnalysisListResponse, AnalysisResponse, AnalyzeRequest
from app.services.analysis_service import AnalysisService

router = APIRouter(prefix="/analysis", tags=["ATS Analysis"])


def get_analysis_service(db: AsyncSession = Depends(get_db)) -> AnalysisService:
    return AnalysisService(AnalysisRepository(db), ResumeRepository(db))


@router.post("", response_model=AnalysisResponse, status_code=201)
async def run_analysis(
    payload: AnalyzeRequest,
    current_user: User = Depends(get_current_user),
    service: AnalysisService = Depends(get_analysis_service),
):
    return await service.run_analysis(current_user.id, payload.resume_id, payload.job_description)


@router.get("", response_model=AnalysisListResponse)
async def list_analyses(
    current_user: User = Depends(get_current_user),
    service: AnalysisService = Depends(get_analysis_service),
):
    analyses = await service.list_analyses(current_user.id)
    return AnalysisListResponse(analyses=analyses, total=len(analyses))


@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    analysis_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: AnalysisService = Depends(get_analysis_service),
):
    return await service.get_analysis(analysis_id, current_user.id)

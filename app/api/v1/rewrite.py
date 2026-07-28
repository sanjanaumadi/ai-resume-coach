from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.resume_repository import ResumeRepository
from app.repositories.rewrite_repository import RewriteRepository
from app.schemas.rewrite import RewriteListResponse, RewriteRequest, RewriteResponse
from app.services.rewrite_service import RewriteService

router = APIRouter(prefix="/rewrite", tags=["Resume Rewriting"])


def get_rewrite_service(db: AsyncSession = Depends(get_db)) -> RewriteService:
    return RewriteService(RewriteRepository(db), ResumeRepository(db))


@router.post("", response_model=RewriteResponse, status_code=201)
async def rewrite_section(
    payload: RewriteRequest,
    current_user: User = Depends(get_current_user),
    service: RewriteService = Depends(get_rewrite_service),
):
    return await service.rewrite_section(
        current_user.id, payload.resume_id, payload.section, payload.text, payload.job_description
    )


@router.get("", response_model=RewriteListResponse)
async def list_rewrites(
    current_user: User = Depends(get_current_user),
    service: RewriteService = Depends(get_rewrite_service),
):
    rewrites = await service.list_rewrites(current_user.id)
    return RewriteListResponse(rewrites=rewrites, total=len(rewrites))

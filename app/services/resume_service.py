import uuid

from app.core.config import settings
from app.models.resume import Resume
from app.repositories.resume_repository import ResumeRepository
from app.services import file_storage, text_extraction
from app.utils.exceptions import AppError
from app.utils.logger import get_logger

logger = get_logger(__name__)


class FileTooLargeError(AppError):
    status_code = 413


class ResumeNotFoundError(AppError):
    status_code = 404


class ResumeService:
    def __init__(self, resume_repo: ResumeRepository):
        self.resume_repo = resume_repo

    async def upload_and_extract(self, user_id: uuid.UUID, filename: str, file_bytes: bytes) -> Resume:
        max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if len(file_bytes) > max_bytes:
            raise FileTooLargeError(f"File exceeds the {settings.MAX_UPLOAD_SIZE_MB}MB limit")

        # Extraction happens before storage - no point saving a file we can't read
        file_type, extracted_text = text_extraction.extract_text(filename, file_bytes)

        stored_filename = file_storage.save_file(filename, file_bytes)

        resume = Resume(
            user_id=user_id,
            original_filename=filename,
            stored_filename=stored_filename,
            file_type=file_type,
            file_size_bytes=len(file_bytes),
            extracted_text=extracted_text,
            char_count=len(extracted_text),
        )
        resume = await self.resume_repo.create(resume)
        logger.info("Resume uploaded: user=%s file=%s chars=%d", user_id, filename, len(extracted_text))
        return resume

    async def get_resume(self, resume_id: uuid.UUID, user_id: uuid.UUID) -> Resume:
        resume = await self.resume_repo.get_by_id(resume_id, user_id)
        if not resume:
            raise ResumeNotFoundError("Resume not found")
        return resume

    async def list_resumes(self, user_id: uuid.UUID) -> list[Resume]:
        return await self.resume_repo.list_for_user(user_id)

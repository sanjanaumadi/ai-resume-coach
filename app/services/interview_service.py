import uuid

from app.models.interview import InterviewSession
from app.repositories.interview_repository import InterviewRepository
from app.repositories.resume_repository import ResumeRepository
from app.services.gemini_client import generate_text
from app.services.interview_prompts import (
    build_answer_evaluation_prompt,
    build_question_generation_prompt,
    parse_evaluation_response,
    parse_questions_response,
)
from app.services.resume_service import ResumeNotFoundError
from app.utils.exceptions import AppError
from app.utils.logger import get_logger

logger = get_logger(__name__)


class InterviewNotFoundError(AppError):
    status_code = 404


class InterviewAlreadyCompletedError(AppError):
    status_code = 409


class QuestionNotFoundError(AppError):
    status_code = 404


class QuestionAlreadyAnsweredError(AppError):
    status_code = 409


class InterviewService:
    def __init__(self, interview_repo: InterviewRepository, resume_repo: ResumeRepository):
        self.interview_repo = interview_repo
        self.resume_repo = resume_repo

    async def start_interview(
        self, user_id: uuid.UUID, resume_id: uuid.UUID, job_description: str | None
    ) -> InterviewSession:
        resume = await self.resume_repo.get_by_id(resume_id, user_id)
        if not resume:
            raise ResumeNotFoundError("Resume not found")

        prompt = build_question_generation_prompt(resume.extracted_text, job_description)
        raw_response = generate_text(prompt, temperature=0.8)
        questions = parse_questions_response(raw_response)

        session = InterviewSession(
            user_id=user_id,
            resume_id=resume_id,
            job_description=job_description,
            status="in_progress",
            questions=questions,
            answers=[],
        )
        session = await self.interview_repo.create(session)
        logger.info("Interview started: user=%s resume=%s questions=%d", user_id, resume_id, len(questions))
        return session

    async def submit_answer(
        self, user_id: uuid.UUID, session_id: uuid.UUID, question_id: str, answer_text: str
    ) -> InterviewSession:
        session = await self._get_active_session(session_id, user_id)

        question = next((q for q in session.questions if q["id"] == question_id), None)
        if not question:
            raise QuestionNotFoundError(f"Question {question_id} not found in this session")

        if any(a["question_id"] == question_id for a in session.answers):
            raise QuestionAlreadyAnsweredError(f"Question {question_id} has already been answered")

        prompt = build_answer_evaluation_prompt(question["question"], answer_text, question["category"])
        raw_response = generate_text(prompt, temperature=0.3)
        evaluation = parse_evaluation_response(raw_response)

        new_answer = {
            "question_id": question_id,
            "answer": answer_text,
            **evaluation,
        }
        # Reassigning (not .append()) so SQLAlchemy's change tracking picks up the mutation on this JSON column
        session.answers = [*session.answers, new_answer]

        session = await self.interview_repo.save(session)
        logger.info("Answer evaluated: session=%s question=%s", session_id, question_id)
        return session

    async def finish_interview(self, user_id: uuid.UUID, session_id: uuid.UUID) -> InterviewSession:
        session = await self._get_active_session(session_id, user_id)

        def avg(key: str) -> int:
            if not session.answers:
                return 0
            return round(sum(a[key] for a in session.answers) / len(session.answers))

        avg_communication = avg("communication_score")
        avg_technical = avg("technical_accuracy_score")
        avg_relevance = avg("relevance_score")
        overall = round((avg_communication + avg_technical + avg_relevance) / 3) if session.answers else 0

        session.final_report = {
            "avg_communication_score": avg_communication,
            "avg_technical_accuracy_score": avg_technical,
            "avg_relevance_score": avg_relevance,
            "overall_score": overall,
            "questions_answered": len(session.answers),
            "questions_total": len(session.questions),
        }
        session.status = "completed"

        session = await self.interview_repo.save(session)
        logger.info("Interview completed: session=%s overall_score=%d", session_id, overall)
        return session

    async def get_session(self, user_id: uuid.UUID, session_id: uuid.UUID) -> InterviewSession:
        session = await self.interview_repo.get_by_id(session_id, user_id)
        if not session:
            raise InterviewNotFoundError("Interview session not found")
        return session

    async def list_sessions(self, user_id: uuid.UUID) -> list[InterviewSession]:
        return await self.interview_repo.list_for_user(user_id)

    async def _get_active_session(self, session_id: uuid.UUID, user_id: uuid.UUID) -> InterviewSession:
        session = await self.get_session(user_id, session_id)
        if session.status == "completed":
            raise InterviewAlreadyCompletedError("This interview session is already completed")
        return session

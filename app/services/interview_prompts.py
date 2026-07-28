import json
import re
from typing import TypedDict


class Question(TypedDict):
    id: str
    category: str  # "hr" | "technical" | "behavioral" | "resume_specific"
    question: str


class Evaluation(TypedDict):
    communication_score: int
    technical_accuracy_score: int
    relevance_score: int
    feedback: str
    suggested_improvement: str


CATEGORIES = ["hr", "technical", "behavioral", "resume_specific"]


def build_question_generation_prompt(
    resume_text: str, job_description: str | None, questions_per_category: int = 2
) -> str:
    parts = [
        "You are an experienced technical interviewer preparing questions for a candidate "
        "based on their resume.",
        f"Generate exactly {questions_per_category} questions for EACH of these four categories: "
        "hr, technical, behavioral, resume_specific.",
        "- hr: general fit/motivation questions (why this role, career goals, etc.)",
        "- technical: questions testing the specific technologies/skills mentioned in the resume",
        "- behavioral: situational questions (e.g. 'tell me about a time...')",
        "- resume_specific: questions that reference specific projects or experience named in the resume",
        "",
        "Candidate's resume:",
        "---",
        resume_text.strip()[:4000],
        "---",
    ]

    if job_description and job_description.strip():
        parts.extend([
            "",
            "Tailor technical questions toward this target job description:",
            "---",
            job_description.strip()[:2000],
            "---",
        ])

    parts.extend([
        "",
        "Return ONLY a JSON array, no markdown fences, no commentary, in this exact shape:",
        '[{"category": "hr", "question": "..."}, {"category": "technical", "question": "..."}, ...]',
    ])

    return "\n".join(parts)


def build_answer_evaluation_prompt(question: str, answer: str, category: str) -> str:
    return "\n".join([
        "You are an interview coach evaluating a candidate's spoken answer to an interview question.",
        f"Question category: {category}",
        f"Question: {question}",
        f"Candidate's answer: {answer.strip()[:3000]}",
        "",
        "Score the answer from 0-100 on each of these dimensions:",
        "- communication_score: clarity, structure, conciseness",
        "- technical_accuracy_score: correctness of any technical claims (score 100 if not applicable, e.g. for HR questions)",
        "- relevance_score: how directly the answer addresses the question asked",
        "",
        "Also give brief, specific feedback (2-3 sentences) and one concrete suggested improvement.",
        "",
        "Return ONLY a JSON object, no markdown fences, no commentary, in this exact shape:",
        '{"communication_score": 0, "technical_accuracy_score": 0, "relevance_score": 0, '
        '"feedback": "...", "suggested_improvement": "..."}',
    ])


def _extract_json_block(raw_text: str) -> str:
    """LLMs frequently wrap JSON in ```json ... ``` fences or add stray text around it.
    This strips markdown fences and extracts the first balanced [...] or {...} block."""
    text = raw_text.strip()

    # Strip markdown code fences if present
    fence_match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    if fence_match:
        text = fence_match.group(1).strip()

    return text


class QuestionParsingError(Exception):
    pass


class EvaluationParsingError(Exception):
    pass


def parse_questions_response(raw_text: str) -> list[Question]:
    cleaned = _extract_json_block(raw_text)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise QuestionParsingError(f"Could not parse questions JSON: {exc}") from exc

    if not isinstance(data, list):
        raise QuestionParsingError("Expected a JSON array of questions")

    questions: list[Question] = []
    for i, item in enumerate(data):
        if not isinstance(item, dict) or "category" not in item or "question" not in item:
            continue  # skip malformed entries rather than failing the whole batch
        category = str(item["category"]).lower().strip()
        if category not in CATEGORIES:
            category = "hr"  # fall back rather than reject a usable question over a label mismatch
        questions.append({
            "id": f"q{i + 1}",
            "category": category,
            "question": str(item["question"]).strip(),
        })

    if not questions:
        raise QuestionParsingError("No valid questions found in response")

    return questions


def parse_evaluation_response(raw_text: str) -> Evaluation:
    cleaned = _extract_json_block(raw_text)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise EvaluationParsingError(f"Could not parse evaluation JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise EvaluationParsingError("Expected a JSON object for evaluation")

    def _clamp_score(value: object) -> int:
        try:
            return max(0, min(100, int(value)))  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return 0

    return {
        "communication_score": _clamp_score(data.get("communication_score")),
        "technical_accuracy_score": _clamp_score(data.get("technical_accuracy_score")),
        "relevance_score": _clamp_score(data.get("relevance_score")),
        "feedback": str(data.get("feedback", "")).strip(),
        "suggested_improvement": str(data.get("suggested_improvement", "")).strip(),
    }

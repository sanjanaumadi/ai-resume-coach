import json
import re
from typing import TypedDict


class LearningStep(TypedDict):
    skill: str
    reason: str


class CareerSuggestions(TypedDict):
    suitable_roles: list[str]
    missing_technologies: list[str]
    learning_roadmap: list[LearningStep]
    resume_readiness_score: int
    readiness_summary: str


def build_career_suggestions_prompt(resume_text: str, target_role: str | None = None) -> str:
    parts = [
        "You are a career advisor helping a candidate understand their job market fit "
        "based on their resume.",
        "",
        "Candidate's resume:",
        "---",
        resume_text.strip()[:4000],
        "---",
    ]

    if target_role and target_role.strip():
        parts.extend([
            "",
            f"The candidate is specifically interested in roles like: {target_role.strip()}",
        ])

    parts.extend([
        "",
        "Provide:",
        "1. suitable_roles: 3-5 specific job titles this candidate is realistically qualified for "
        "right now, based on what's actually in their resume (not aspirational titles beyond their level)",
        "2. missing_technologies: 3-6 specific technologies/skills that would make them more competitive "
        "for those roles, that are NOT already in their resume",
        "3. learning_roadmap: 3-5 ordered steps, each with a 'skill' to learn and a one-sentence 'reason' "
        "why it matters for their target roles, in priority order",
        "4. resume_readiness_score: 0-100, how ready this resume is for job applications right now "
        "(consider completeness, specificity, and market competitiveness - not just formatting)",
        "5. readiness_summary: 2-3 sentences explaining the readiness score honestly",
        "",
        "Return ONLY a JSON object, no markdown fences, no commentary, in this exact shape:",
        '{"suitable_roles": ["..."], "missing_technologies": ["..."], '
        '"learning_roadmap": [{"skill": "...", "reason": "..."}], '
        '"resume_readiness_score": 0, "readiness_summary": "..."}',
    ])

    return "\n".join(parts)


def _extract_json_block(raw_text: str) -> str:
    text = raw_text.strip()
    fence_match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    if fence_match:
        text = fence_match.group(1).strip()
    return text


class CareerSuggestionsParsingError(Exception):
    pass


def _as_string_list(value: object, limit: int) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()][:limit]


def _as_roadmap(value: object, limit: int) -> list[LearningStep]:
    if not isinstance(value, list):
        return []
    steps: list[LearningStep] = []
    for item in value:
        if not isinstance(item, dict) or "skill" not in item:
            continue
        steps.append({
            "skill": str(item["skill"]).strip(),
            "reason": str(item.get("reason", "")).strip(),
        })
    return steps[:limit]


def parse_career_suggestions_response(raw_text: str) -> CareerSuggestions:
    cleaned = _extract_json_block(raw_text)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise CareerSuggestionsParsingError(f"Could not parse career suggestions JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise CareerSuggestionsParsingError("Expected a JSON object for career suggestions")

    suitable_roles = _as_string_list(data.get("suitable_roles"), limit=5)
    missing_technologies = _as_string_list(data.get("missing_technologies"), limit=6)
    learning_roadmap = _as_roadmap(data.get("learning_roadmap"), limit=5)

    if not suitable_roles and not learning_roadmap:
        # If both core fields are empty, the response is unusable - a partial result
        # (e.g. missing readiness_summary) is fine, but no roles AND no roadmap means
        # something went badly wrong upstream.
        raise CareerSuggestionsParsingError("Response contained no usable suggestions")

    try:
        readiness_score = max(0, min(100, int(data.get("resume_readiness_score", 0))))
    except (TypeError, ValueError):
        readiness_score = 0

    return {
        "suitable_roles": suitable_roles,
        "missing_technologies": missing_technologies,
        "learning_roadmap": learning_roadmap,
        "resume_readiness_score": readiness_score,
        "readiness_summary": str(data.get("readiness_summary", "")).strip(),
    }

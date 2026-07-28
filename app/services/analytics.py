from collections import Counter
from typing import TypedDict


class ScorePoint(TypedDict):
    date: str
    score: int


class SkillFrequency(TypedDict):
    skill: str
    count: int


class AnalyticsSummary(TypedDict):
    ats_score_trend: list[ScorePoint]
    interview_score_trend: list[ScorePoint]
    skills_frequency: list[SkillFrequency]
    total_resumes: int
    total_analyses: int
    total_interviews: int
    latest_ats_score: int | None
    latest_interview_score: int | None


def build_ats_score_trend(analyses: list[dict]) -> list[ScorePoint]:
    """analyses: list of {ats_score: int, created_at: datetime-like with .isoformat()},
    ordered newest-first (matches repository query order) - reversed here to oldest-first
    for a left-to-right chart."""
    ordered = list(reversed(analyses))
    return [{"date": a["created_at"].isoformat(), "score": a["ats_score"]} for a in ordered]


def build_interview_score_trend(interview_sessions: list[dict]) -> list[ScorePoint]:
    """Only completed sessions have a final_report with an overall_score."""
    completed = [
        s for s in reversed(interview_sessions)
        if s.get("status") == "completed" and s.get("final_report")
    ]
    return [{"date": s["created_at"].isoformat(), "score": s["final_report"]["overall_score"]} for s in completed]


def build_skills_frequency(analyses: list[dict], top_n: int = 15) -> list[SkillFrequency]:
    """Counts how often each skill appears across all of a user's analyses -
    shows which skills are consistently present vs. one-offs."""
    counter: Counter[str] = Counter()
    for analysis in analyses:
        matched_skills = analysis.get("result", {}).get("matched_skills", [])
        counter.update(matched_skills)

    return [
        {"skill": skill, "count": count}
        for skill, count in counter.most_common(top_n)
    ]


def build_analytics_summary(
    resume_count: int,
    analyses: list[dict],
    interview_sessions: list[dict],
) -> AnalyticsSummary:
    ats_trend = build_ats_score_trend(analyses)
    interview_trend = build_interview_score_trend(interview_sessions)

    return {
        "ats_score_trend": ats_trend,
        "interview_score_trend": interview_trend,
        "skills_frequency": build_skills_frequency(analyses),
        "total_resumes": resume_count,
        "total_analyses": len(analyses),
        "total_interviews": len(interview_sessions),
        "latest_ats_score": ats_trend[-1]["score"] if ats_trend else None,
        "latest_interview_score": interview_trend[-1]["score"] if interview_trend else None,
    }

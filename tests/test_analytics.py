from datetime import datetime, timezone

from app.services.analytics import (
    build_analytics_summary,
    build_ats_score_trend,
    build_interview_score_trend,
    build_skills_frequency,
)


def _dt(day: int) -> datetime:
    return datetime(2026, 1, day, tzinfo=timezone.utc)


def test_ats_score_trend_reverses_to_oldest_first():
    # repository returns newest-first (created_at DESC)
    analyses = [
        {"ats_score": 90, "created_at": _dt(3)},
        {"ats_score": 80, "created_at": _dt(2)},
        {"ats_score": 70, "created_at": _dt(1)},
    ]
    trend = build_ats_score_trend(analyses)
    assert [p["score"] for p in trend] == [70, 80, 90]


def test_ats_score_trend_empty_list():
    assert build_ats_score_trend([]) == []


def test_interview_score_trend_only_includes_completed_sessions():
    sessions = [
        {"status": "completed", "final_report": {"overall_score": 85}, "created_at": _dt(2)},
        {"status": "in_progress", "final_report": None, "created_at": _dt(1)},
    ]
    trend = build_interview_score_trend(sessions)
    assert len(trend) == 1
    assert trend[0]["score"] == 85


def test_interview_score_trend_handles_all_in_progress():
    sessions = [{"status": "in_progress", "final_report": None, "created_at": _dt(1)}]
    assert build_interview_score_trend(sessions) == []


def test_interview_score_trend_empty_list():
    assert build_interview_score_trend([]) == []


def test_skills_frequency_counts_across_analyses():
    analyses = [
        {"result": {"matched_skills": ["python", "react"]}},
        {"result": {"matched_skills": ["python", "docker"]}},
        {"result": {"matched_skills": ["python"]}},
    ]
    freq = build_skills_frequency(analyses)
    assert freq[0] == {"skill": "python", "count": 3}


def test_skills_frequency_respects_top_n_limit():
    analyses = [{"result": {"matched_skills": [f"skill{i}" for i in range(20)]}}]
    freq = build_skills_frequency(analyses, top_n=5)
    assert len(freq) == 5


def test_skills_frequency_handles_missing_matched_skills_key():
    analyses = [{"result": {}}, {"result": {"matched_skills": ["python"]}}]
    freq = build_skills_frequency(analyses)
    assert freq == [{"skill": "python", "count": 1}]


def test_skills_frequency_empty_analyses():
    assert build_skills_frequency([]) == []


def test_build_analytics_summary_full_data():
    analyses = [
        {"ats_score": 90, "created_at": _dt(2), "result": {"matched_skills": ["python"]}},
        {"ats_score": 70, "created_at": _dt(1), "result": {"matched_skills": ["python", "java"]}},
    ]
    sessions = [
        {"status": "completed", "final_report": {"overall_score": 80}, "created_at": _dt(2)},
    ]
    summary = build_analytics_summary(resume_count=3, analyses=analyses, interview_sessions=sessions)

    assert summary["total_resumes"] == 3
    assert summary["total_analyses"] == 2
    assert summary["total_interviews"] == 1
    assert summary["latest_ats_score"] == 90  # most recent by date, not most recent in list order
    assert summary["latest_interview_score"] == 80


def test_build_analytics_summary_handles_no_data_at_all():
    summary = build_analytics_summary(resume_count=0, analyses=[], interview_sessions=[])
    assert summary["latest_ats_score"] is None
    assert summary["latest_interview_score"] is None
    assert summary["ats_score_trend"] == []
    assert summary["skills_frequency"] == []

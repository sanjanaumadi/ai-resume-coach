import pytest

from app.services.career_prompts import (
    CareerSuggestionsParsingError,
    build_career_suggestions_prompt,
    parse_career_suggestions_response,
)

CLEAN_RESPONSE = """
{"suitable_roles": ["Backend Engineer", "Full-Stack Developer"],
"missing_technologies": ["Kubernetes", "GraphQL"],
"learning_roadmap": [{"skill": "Kubernetes", "reason": "Widely required for backend roles"}],
"resume_readiness_score": 75,
"readiness_summary": "Solid technical foundation, needs more quantified impact."}
"""


def test_build_prompt_includes_resume_text():
    prompt = build_career_suggestions_prompt("Skilled in Python and Django.")
    assert "Skilled in Python and Django." in prompt


def test_build_prompt_includes_target_role_when_provided():
    prompt = build_career_suggestions_prompt("resume text", target_role="Machine Learning Engineer")
    assert "Machine Learning Engineer" in prompt


def test_parse_clean_response():
    result = parse_career_suggestions_response(CLEAN_RESPONSE)
    assert result["suitable_roles"] == ["Backend Engineer", "Full-Stack Developer"]
    assert result["missing_technologies"] == ["Kubernetes", "GraphQL"]
    assert result["learning_roadmap"] == [{"skill": "Kubernetes", "reason": "Widely required for backend roles"}]
    assert result["resume_readiness_score"] == 75


def test_parse_strips_markdown_fences():
    raw = f"```json\n{CLEAN_RESPONSE}\n```"
    result = parse_career_suggestions_response(raw)
    assert result["resume_readiness_score"] == 75


def test_parse_clamps_out_of_range_readiness_score():
    raw = '{"suitable_roles": ["Engineer"], "resume_readiness_score": 150, "learning_roadmap": [], "missing_technologies": [], "readiness_summary": "x"}'
    result = parse_career_suggestions_response(raw)
    assert result["resume_readiness_score"] == 100


def test_parse_handles_negative_readiness_score():
    raw = '{"suitable_roles": ["Engineer"], "resume_readiness_score": -10, "learning_roadmap": [], "missing_technologies": [], "readiness_summary": "x"}'
    result = parse_career_suggestions_response(raw)
    assert result["resume_readiness_score"] == 0


def test_parse_handles_non_numeric_readiness_score():
    raw = '{"suitable_roles": ["Engineer"], "resume_readiness_score": "high", "learning_roadmap": [], "missing_technologies": [], "readiness_summary": "x"}'
    result = parse_career_suggestions_response(raw)
    assert result["resume_readiness_score"] == 0


def test_parse_truncates_lists_over_limit():
    raw_roles = [f"Role {i}" for i in range(10)]
    import json
    raw = json.dumps({
        "suitable_roles": raw_roles, "missing_technologies": [], "learning_roadmap": [],
        "resume_readiness_score": 50, "readiness_summary": "x"
    })
    result = parse_career_suggestions_response(raw)
    assert len(result["suitable_roles"]) == 5


def test_parse_skips_malformed_roadmap_entries():
    raw = '{"suitable_roles": ["Engineer"], "missing_technologies": [], "learning_roadmap": [{"skill": "Docker", "reason": "y"}, {"no_skill_field": true}], "resume_readiness_score": 50, "readiness_summary": "x"}'
    result = parse_career_suggestions_response(raw)
    assert len(result["learning_roadmap"]) == 1
    assert result["learning_roadmap"][0]["skill"] == "Docker"

def test_parse_defaults_missing_reason_to_empty_string():
    raw = '{"suitable_roles": ["Engineer"], "missing_technologies": [], "learning_roadmap": [{"skill": "Docker"}], "resume_readiness_score": 50, "readiness_summary": "x"}'
    result = parse_career_suggestions_response(raw)
    assert result["learning_roadmap"][0]["reason"] == ""


def test_parse_raises_when_both_roles_and_roadmap_empty():
    raw = '{"suitable_roles": [], "missing_technologies": [], "learning_roadmap": [], "resume_readiness_score": 50, "readiness_summary": "x"}'
    with pytest.raises(CareerSuggestionsParsingError):
        parse_career_suggestions_response(raw)


def test_parse_succeeds_with_only_roadmap_and_no_roles():
    raw = '{"suitable_roles": [], "missing_technologies": [], "learning_roadmap": [{"skill": "Docker", "reason": "y"}], "resume_readiness_score": 50, "readiness_summary": "x"}'
    result = parse_career_suggestions_response(raw)
    assert result["learning_roadmap"][0]["skill"] == "Docker"


def test_parse_raises_on_invalid_json():
    with pytest.raises(CareerSuggestionsParsingError):
        parse_career_suggestions_response("Not valid JSON at all")


def test_parse_raises_when_response_is_array_not_object():
    with pytest.raises(CareerSuggestionsParsingError):
        parse_career_suggestions_response('[{"suitable_roles": ["Engineer"]}]')


def test_parse_handles_missing_readiness_summary_gracefully():
    raw = '{"suitable_roles": ["Engineer"], "missing_technologies": [], "learning_roadmap": [], "resume_readiness_score": 50}'
    result = parse_career_suggestions_response(raw)
    assert result["readiness_summary"] == ""

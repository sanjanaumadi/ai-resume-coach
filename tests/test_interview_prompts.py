import pytest

from app.services.interview_prompts import (
    EvaluationParsingError,
    QuestionParsingError,
    build_answer_evaluation_prompt,
    build_question_generation_prompt,
    parse_evaluation_response,
    parse_questions_response,
)

# --- prompt building (pure, no API calls) ---


def test_build_question_prompt_includes_resume_text():
    prompt = build_question_generation_prompt("Skilled in Python and React.", None)
    assert "Skilled in Python and React." in prompt


def test_build_question_prompt_includes_jd_when_provided():
    prompt = build_question_generation_prompt("resume text", "Looking for a backend engineer.")
    assert "Looking for a backend engineer." in prompt


def test_build_question_prompt_omits_jd_section_when_absent():
    prompt = build_question_generation_prompt("resume text", None)
    assert "Tailor technical questions" not in prompt


def test_build_evaluation_prompt_includes_question_and_answer():
    prompt = build_answer_evaluation_prompt("Why do you want this role?", "I love building things.", "hr")
    assert "Why do you want this role?" in prompt
    assert "I love building things." in prompt


# --- question response parsing: happy path ---


def test_parse_questions_clean_json():
    raw = '[{"category": "hr", "question": "Why this role?"}, {"category": "technical", "question": "Explain REST."}]'
    result = parse_questions_response(raw)
    assert len(result) == 2
    assert result[0]["category"] == "hr"
    assert result[0]["question"] == "Why this role?"
    assert result[0]["id"] == "q1"


# --- question response parsing: realistic LLM messiness ---


def test_parse_questions_strips_markdown_fences():
    raw = '```json\n[{"category": "hr", "question": "Why this role?"}]\n```'
    result = parse_questions_response(raw)
    assert len(result) == 1
    assert result[0]["question"] == "Why this role?"


def test_parse_questions_strips_fences_without_json_language_tag():
    raw = '```\n[{"category": "technical", "question": "Explain Docker."}]\n```'
    result = parse_questions_response(raw)
    assert result[0]["question"] == "Explain Docker."


def test_parse_questions_normalizes_unexpected_category_instead_of_failing():
    raw = '[{"category": "general", "question": "Tell me about yourself."}]'
    result = parse_questions_response(raw)
    # unknown category falls back to "hr" rather than dropping a usable question
    assert result[0]["category"] == "hr"


def test_parse_questions_skips_malformed_entries_but_keeps_valid_ones():
    raw = '[{"category": "hr", "question": "Valid question"}, {"category": "technical"}, {"not_a_question_field": true}]'
    result = parse_questions_response(raw)
    assert len(result) == 1
    assert result[0]["question"] == "Valid question"


def test_parse_questions_raises_on_completely_invalid_json():
    with pytest.raises(QuestionParsingError):
        parse_questions_response("This is not JSON at all, sorry!")


def test_parse_questions_raises_when_response_is_object_not_array():
    with pytest.raises(QuestionParsingError):
        parse_questions_response('{"category": "hr", "question": "Why this role?"}')


def test_parse_questions_raises_when_all_entries_malformed():
    with pytest.raises(QuestionParsingError):
        parse_questions_response('[{"foo": "bar"}, {"baz": "qux"}]')


def test_parse_questions_assigns_sequential_ids():
    raw = '[{"category": "hr", "question": "Q1"}, {"category": "hr", "question": "Q2"}]'
    result = parse_questions_response(raw)
    assert result[0]["id"] == "q1"
    assert result[1]["id"] == "q2"


# --- evaluation response parsing ---


def test_parse_evaluation_clean_json():
    raw = '{"communication_score": 80, "technical_accuracy_score": 90, "relevance_score": 85, "feedback": "Good answer.", "suggested_improvement": "Add a specific example."}'
    result = parse_evaluation_response(raw)
    assert result["communication_score"] == 80
    assert result["technical_accuracy_score"] == 90
    assert result["relevance_score"] == 85
    assert result["feedback"] == "Good answer."


def test_parse_evaluation_strips_markdown_fences():
    raw = '```json\n{"communication_score": 70, "technical_accuracy_score": 60, "relevance_score": 75, "feedback": "OK", "suggested_improvement": "Be concise"}\n```'
    result = parse_evaluation_response(raw)
    assert result["communication_score"] == 70


def test_parse_evaluation_clamps_out_of_range_scores():
    raw = '{"communication_score": 150, "technical_accuracy_score": -20, "relevance_score": 50, "feedback": "x", "suggested_improvement": "y"}'
    result = parse_evaluation_response(raw)
    assert result["communication_score"] == 100
    assert result["technical_accuracy_score"] == 0


def test_parse_evaluation_defaults_missing_score_to_zero_instead_of_crashing():
    raw = '{"communication_score": 80, "feedback": "x", "suggested_improvement": "y"}'
    result = parse_evaluation_response(raw)
    assert result["technical_accuracy_score"] == 0
    assert result["relevance_score"] == 0


def test_parse_evaluation_handles_non_numeric_score_gracefully():
    raw = '{"communication_score": "high", "technical_accuracy_score": 80, "relevance_score": 80, "feedback": "x", "suggested_improvement": "y"}'
    result = parse_evaluation_response(raw)
    assert result["communication_score"] == 0


def test_parse_evaluation_raises_on_invalid_json():
    with pytest.raises(EvaluationParsingError):
        parse_evaluation_response("Not valid JSON")


def test_parse_evaluation_raises_when_response_is_array_not_object():
    with pytest.raises(EvaluationParsingError):
        parse_evaluation_response('[{"communication_score": 80}]')

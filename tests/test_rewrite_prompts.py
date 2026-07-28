from app.services.rewrite_prompts import build_prompt, parse_bullets


def test_build_prompt_includes_original_text():
    prompt = build_prompt("summary", "I am a hard worker.")
    assert "I am a hard worker." in prompt


def test_build_prompt_includes_section_specific_instruction():
    summary_prompt = build_prompt("summary", "some text")
    bullets_prompt = build_prompt("bullets", "some text")
    assert "career summary" in summary_prompt.lower()
    assert "bullet points" in bullets_prompt.lower()
    assert summary_prompt != bullets_prompt


def test_build_prompt_includes_job_description_when_provided():
    prompt = build_prompt("summary", "original", job_description="Looking for a Python developer.")
    assert "Looking for a Python developer." in prompt
    assert "Tailor the rewrite" in prompt


def test_build_prompt_omits_jd_section_when_not_provided():
    prompt = build_prompt("summary", "original", job_description=None)
    assert "Tailor the rewrite" not in prompt


def test_build_prompt_omits_jd_section_when_blank_string():
    prompt = build_prompt("summary", "original", job_description="   ")
    assert "Tailor the rewrite" not in prompt


def test_parse_bullets_strips_dash_markers():
    raw = "- Built a REST API\n- Improved performance by 30%"
    result = parse_bullets(raw)
    assert result == ["Built a REST API", "Improved performance by 30%"]


def test_parse_bullets_strips_bullet_point_markers():
    raw = "• Built a REST API\n• Improved performance"
    result = parse_bullets(raw)
    assert result == ["Built a REST API", "Improved performance"]


def test_parse_bullets_ignores_blank_lines():
    raw = "- First bullet\n\n- Second bullet\n"
    result = parse_bullets(raw)
    assert result == ["First bullet", "Second bullet"]

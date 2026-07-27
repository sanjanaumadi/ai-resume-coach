from app.services.ats_analyzer import (
    analyze_resume,
    check_contact_info,
    check_formatting,
    check_sections,
    extract_skills,
)

GOOD_RESUME = """
Jane Doe
jane.doe@email.com | 9876543210 | linkedin.com/in/janedoe

EDUCATION
B.E. Computer Science, XYZ University, 2024

SKILLS
Python, React, AWS, Docker, Git, REST API

PROJECTS
E-commerce Platform
- Built a full-stack app using React and FastAPI
- Deployed on AWS using Docker containers
"""

BAD_RESUME = """
Jane Doe is a person who writes a lot of paragraphs without any bullet points at all
and does not mention an email or phone number anywhere in this extremely long block of
text that goes on and on without any structure or clear sections that an ATS could parse
easily, making it very hard for automated systems to extract meaningful information from
this particular document which unfortunately lacks the standard formatting conventions.
"""


def test_extract_skills_finds_known_skills():
    skills = extract_skills("I know Python, React, and AWS very well.")
    assert "python" in skills
    assert "react" in skills
    assert "aws" in skills


def test_extract_skills_avoids_partial_word_matches():
    # "r" is not in our skills db, but this guards against future single-letter entries
    # matching inside unrelated words like "for" or "car"
    skills = extract_skills("I drove a car for a long time.")
    assert "r" not in skills


def test_check_sections_detects_all_sections_in_good_resume():
    sections = check_sections(GOOD_RESUME)
    assert sections["education"] is True
    assert sections["skills"] is True
    assert sections["experience_or_projects"] is True
    assert sections["contact"] is True


def test_check_sections_flags_missing_sections_in_bad_resume():
    sections = check_sections(BAD_RESUME)
    assert sections["education"] is False
    assert sections["skills"] is False


def test_check_contact_info_detects_email_and_phone():
    contact = check_contact_info(GOOD_RESUME)
    assert contact["has_email"] is True
    assert contact["has_phone"] is True


def test_check_contact_info_missing_in_bad_resume():
    contact = check_contact_info(BAD_RESUME)
    assert contact["has_email"] is False


def test_check_formatting_flags_missing_bullets():
    issues = check_formatting(BAD_RESUME)
    assert any("bullet" in issue.lower() for issue in issues)


def test_check_formatting_clean_for_good_resume():
    issues = check_formatting(GOOD_RESUME)
    assert not any("bullet" in issue.lower() for issue in issues)


def test_analyze_resume_good_resume_scores_higher_than_bad():
    good_result = analyze_resume(GOOD_RESUME)
    bad_result = analyze_resume(BAD_RESUME)
    assert good_result["ats_score"] > bad_result["ats_score"]


def test_analyze_resume_without_jd_has_no_jd_match():
    result = analyze_resume(GOOD_RESUME)
    assert result["jd_match"] is None


def test_analyze_resume_with_jd_computes_match_percentage():
    jd = "Looking for a Python developer with React and Kubernetes experience."
    result = analyze_resume(GOOD_RESUME, jd)
    assert result["jd_match"] is not None
    assert "kubernetes" in result["jd_match"]["missing_skills"]
    assert result["jd_match"]["match_percentage"] > 0


def test_analyze_resume_full_jd_match_when_all_skills_present():
    jd = "Need someone who knows Python and React."
    result = analyze_resume(GOOD_RESUME, jd)
    assert result["jd_match"]["match_percentage"] == 100
    assert result["jd_match"]["missing_skills"] == []

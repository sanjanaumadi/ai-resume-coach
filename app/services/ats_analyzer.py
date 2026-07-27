import re

from app.services.skills_data import all_skills

REQUIRED_SECTIONS = {
    "contact": [r"email|phone|linkedin|@"],
    "education": [r"\beducation\b|\bdegree\b|\bb\.?e\.?\b|\bb\.?tech\b|\buniversity\b|\bcollege\b"],
    "experience_or_projects": [r"\bexperience\b|\bprojects?\b|\binternship\b"],
    "skills": [r"\bskills?\b|\btechnologies\b|\btechnical\b"],
}

EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_PATTERN = re.compile(r"(\+?\d{1,3}[\s-]?)?\d{10}|\d{3}[\s-]\d{3}[\s-]\d{4}")
BULLET_PATTERN = re.compile(r"^\s*[•\-\*▪◦]\s+", re.MULTILINE)


def extract_skills(text: str) -> set[str]:
    text_lower = text.lower()
    found = set()
    for skill in all_skills():
        # word-boundary match to avoid partial matches (e.g. "r" matching inside "for")
        pattern = r"(?<![a-zA-Z0-9])" + re.escape(skill) + r"(?![a-zA-Z0-9])"
        if re.search(pattern, text_lower):
            found.add(skill)
    return found


def check_sections(text: str) -> dict[str, bool]:
    text_lower = text.lower()
    return {
        section: bool(re.search(patterns[0], text_lower))
        for section, patterns in REQUIRED_SECTIONS.items()
    }


def check_contact_info(text: str) -> dict[str, bool]:
    return {
        "has_email": bool(EMAIL_PATTERN.search(text)),
        "has_phone": bool(PHONE_PATTERN.search(text)),
    }


def check_formatting(text: str) -> list[str]:
    issues = []

    if not BULLET_PATTERN.search(text):
        issues.append(
            "No bullet points detected. ATS systems and recruiters scan bullet points "
            "far more easily than paragraphs — convert dense text into concise bullets."
        )

    word_count = len(text.split())
    if word_count < 150:
        issues.append(f"Resume seems short ({word_count} words). Consider adding more detail on projects/experience.")
    elif word_count > 1000:
        issues.append(f"Resume seems long ({word_count} words). Aim for 1 page (~400-600 words) unless you have 5+ years experience.")

    lines = [l for l in text.split("\n") if l.strip()]
    long_lines = [l for l in lines if len(l) > 300]
    if long_lines:
        issues.append("Some lines are unusually long/dense — break them into shorter bullet points for readability.")

    return issues


def compute_ats_score(
    sections: dict[str, bool],
    contact: dict[str, bool],
    formatting_issues: list[str],
    matched_skill_count: int,
) -> int:
    score = 0

    # Sections: 40 points total
    score += sum(10 for present in sections.values() if present)

    # Contact info: 15 points total
    score += 10 if contact["has_email"] else 0
    score += 5 if contact["has_phone"] else 0

    # Skills presence: up to 25 points, scaled
    score += min(matched_skill_count * 2, 25)

    # Formatting: start at 20, deduct per issue
    formatting_score = max(20 - len(formatting_issues) * 5, 0)
    score += formatting_score

    return min(score, 100)


def build_recommendations(
    sections: dict[str, bool],
    contact: dict[str, bool],
    formatting_issues: list[str],
    matched_skill_count: int,
) -> list[str]:
    recs = []

    for section, present in sections.items():
        if not present:
            readable = section.replace("_", " ")
            recs.append(f"Add a clear '{readable}' section — ATS parsers look for standard section headers.")

    if not contact["has_email"]:
        recs.append("Add a professional email address near the top of your resume.")
    if not contact["has_phone"]:
        recs.append("Add a phone number so recruiters can reach you directly.")

    if matched_skill_count < 5:
        recs.append("List more relevant technical skills explicitly — ATS keyword matching relies on exact terms.")

    recs.extend(formatting_issues)

    return recs


def analyze_resume(text: str, job_description: str | None = None) -> dict:
    sections = check_sections(text)
    contact = check_contact_info(text)
    formatting_issues = check_formatting(text)
    matched_skills = extract_skills(text)

    ats_score = compute_ats_score(sections, contact, formatting_issues, len(matched_skills))
    recommendations = build_recommendations(sections, contact, formatting_issues, len(matched_skills))

    result = {
        "ats_score": ats_score,
        "matched_skills": sorted(matched_skills),
        "sections_found": sections,
        "contact_info": contact,
        "formatting_issues": formatting_issues,
        "recommendations": recommendations,
        "jd_match": None,
    }

    if job_description and job_description.strip():
        jd_skills = extract_skills(job_description)
        missing_skills = sorted(jd_skills - matched_skills)
        match_pct = (
            round(len(jd_skills & matched_skills) / len(jd_skills) * 100)
            if jd_skills else 0
        )
        result["jd_match"] = {
            "jd_skills_found": sorted(jd_skills),
            "missing_skills": missing_skills,
            "match_percentage": match_pct,
        }
        if missing_skills:
            result["recommendations"].append(
                f"Job description mentions {len(missing_skills)} skill(s) not found in your resume: "
                f"{', '.join(missing_skills[:8])}{'...' if len(missing_skills) > 8 else ''}."
            )

    return result

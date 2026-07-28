from typing import Literal

RewriteSection = Literal["summary", "bullets", "skills"]

_SECTION_INSTRUCTIONS: dict[RewriteSection, str] = {
    "summary": (
        "Rewrite this resume career summary/objective to be more compelling and specific. "
        "Keep it to 2-3 sentences. Avoid generic phrases like 'motivated' or 'hard-working' "
        "unless backed by a concrete example. Write in first person implied (no 'I'), "
        "the way resume summaries are conventionally written."
    ),
    "bullets": (
        "Rewrite these resume bullet points to be more impactful. For each bullet: "
        "start with a strong action verb, quantify the impact with a number, percentage, "
        "or scale wherever it can be reasonably inferred (and clearly mark inferred numbers "
        "with [estimate] so the person can verify them), and keep each bullet to one line. "
        "Return the same number of bullets as given, each on its own line starting with '- '."
    ),
    "skills": (
        "Reorganize and tighten this technical skills section. Group related skills together "
        "under short category labels (e.g. 'Languages:', 'Frameworks:'). Remove vague or "
        "non-technical filler. Keep every genuine technical skill mentioned - do not invent new ones."
    ),
}


def build_prompt(section: RewriteSection, original_text: str, job_description: str | None = None) -> str:
    instruction = _SECTION_INSTRUCTIONS[section]

    prompt_parts = [
        "You are an expert resume writer helping a candidate improve their resume.",
        instruction,
        "",
        "Original text:",
        "---",
        original_text.strip(),
        "---",
    ]

    if job_description and job_description.strip():
        prompt_parts.extend([
            "",
            "Tailor the rewrite toward this target job description where honestly possible "
            "(do not fabricate experience the candidate doesn't have):",
            "---",
            job_description.strip(),
            "---",
        ])

    prompt_parts.extend([
        "",
        "Return ONLY the rewritten text, with no preamble, no explanation, and no markdown formatting "
        "other than what was requested above.",
    ])

    return "\n".join(prompt_parts)


def parse_bullets(raw_text: str) -> list[str]:
    """Splits a Gemini bullets response into a clean list, stripping leading '- ' or '• ' markers."""
    lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
    return [line.lstrip("-•").strip() for line in lines]

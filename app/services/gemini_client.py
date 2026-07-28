import google.generativeai as genai

from app.core.config import settings
from app.utils.exceptions import AppError
from app.utils.logger import get_logger

logger = get_logger(__name__)

MODEL_NAME = "gemini-flash-latest"
_configured = False


class GeminiNotConfiguredError(AppError):
    status_code = 503


class GeminiRequestError(AppError):
    status_code = 502


def _ensure_configured() -> None:
    global _configured
    if _configured:
        return
    if not settings.GEMINI_API_KEY:
        raise GeminiNotConfiguredError(
            "GEMINI_API_KEY is not set. Add it to your .env file to use AI-powered features."
        )
    genai.configure(api_key=settings.GEMINI_API_KEY)
    _configured = True


def generate_text(prompt: str, temperature: float = 0.7) -> str:
    """Sends a prompt to Gemini and returns the raw text response.
    Raises GeminiNotConfiguredError if no API key, GeminiRequestError on API failure."""
    _ensure_configured()

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(temperature=temperature),
        )
        return response.text.strip()
    except Exception as exc:
        logger.error("Gemini request failed: %s", exc)
        raise GeminiRequestError(f"AI request failed: {exc}") from exc

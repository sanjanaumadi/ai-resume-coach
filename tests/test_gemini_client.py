from unittest.mock import MagicMock, patch

import pytest

import app.services.gemini_client as gemini_client
from app.services.gemini_client import (
    GeminiNotConfiguredError,
    GeminiRequestError,
    generate_text,
)


@pytest.fixture(autouse=True)
def reset_configured_state():
    """gemini_client caches configuration in a module-level flag - reset it
    between tests so each test controls its own configured/unconfigured state."""
    gemini_client._configured = False
    yield
    gemini_client._configured = False


def test_generate_text_raises_when_no_api_key(monkeypatch):
    monkeypatch.setattr("app.services.gemini_client.settings.GEMINI_API_KEY", "")
    with pytest.raises(GeminiNotConfiguredError):
        generate_text("some prompt")


def test_generate_text_returns_response_text_on_success(monkeypatch):
    monkeypatch.setattr("app.services.gemini_client.settings.GEMINI_API_KEY", "fake-key-for-test")

    mock_response = MagicMock()
    mock_response.text = "  Rewritten text here.  "

    with patch("google.generativeai.GenerativeModel") as MockModel, patch("google.generativeai.configure"):
        MockModel.return_value.generate_content.return_value = mock_response
        result = generate_text("some prompt")

    assert result == "Rewritten text here."


def test_generate_text_wraps_api_errors(monkeypatch):
    monkeypatch.setattr("app.services.gemini_client.settings.GEMINI_API_KEY", "fake-key-for-test")

    with patch("google.generativeai.GenerativeModel") as MockModel, patch("google.generativeai.configure"):
        MockModel.return_value.generate_content.side_effect = Exception("API quota exceeded")
        with pytest.raises(GeminiRequestError):
            generate_text("some prompt")

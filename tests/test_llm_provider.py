"""Unit tests for the LLM provider factory (core.rag.llm_provider)."""

import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

# Add src directories to path so we can import modules
SRC_DIR = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))
sys.path.insert(0, str(SRC_DIR / "core"))

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_settings(**overrides):
    """Create a mock settings object with default values."""
    defaults = {
        "LLM_PROVIDER": "openai",
        "OPENAI_MODEL_ID": "gpt-4o-mini",
        "OPENAI_API_KEY": "sk-test-openai-key",
        "MINIMAX_API_KEY": "mm-test-key",
        "MINIMAX_MODEL_ID": "MiniMax-M3",
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


# ---------------------------------------------------------------------------
# Tests for get_chat_model
# ---------------------------------------------------------------------------

class TestGetChatModel:
    """Tests for the get_chat_model factory function."""

    @patch("core.rag.llm_provider.ChatOpenAI")
    @patch("core.rag.llm_provider.settings", _make_settings(LLM_PROVIDER="openai"))
    def test_openai_provider_default(self, mock_chat):
        from core.rag.llm_provider import get_chat_model
        get_chat_model(temperature=0)

        mock_chat.assert_called_once_with(
            model="gpt-4o-mini",
            api_key="sk-test-openai-key",
            temperature=0,
        )

    @patch("core.rag.llm_provider.ChatOpenAI")
    @patch("core.rag.llm_provider.settings", _make_settings(LLM_PROVIDER="minimax"))
    def test_minimax_provider(self, mock_chat):
        from core.rag.llm_provider import get_chat_model
        get_chat_model(temperature=0)

        mock_chat.assert_called_once_with(
            model="MiniMax-M3",
            api_key="mm-test-key",
            base_url="https://api.minimax.io/v1",
            temperature=0.0,
        )

    @patch("core.rag.llm_provider.ChatOpenAI")
    @patch("core.rag.llm_provider.settings", _make_settings(LLM_PROVIDER="minimax"))
    def test_minimax_temperature_clamping_high(self, mock_chat):
        from core.rag.llm_provider import get_chat_model
        get_chat_model(temperature=2.0)

        call_kwargs = mock_chat.call_args[1]
        assert call_kwargs["temperature"] == 1.0

    @patch("core.rag.llm_provider.ChatOpenAI")
    @patch("core.rag.llm_provider.settings", _make_settings(LLM_PROVIDER="minimax"))
    def test_minimax_temperature_clamping_negative(self, mock_chat):
        from core.rag.llm_provider import get_chat_model
        get_chat_model(temperature=-0.5)

        call_kwargs = mock_chat.call_args[1]
        assert call_kwargs["temperature"] == 0.0

    @patch("core.rag.llm_provider.ChatOpenAI")
    @patch("core.rag.llm_provider.settings", _make_settings(LLM_PROVIDER="minimax"))
    def test_minimax_no_temperature(self, mock_chat):
        from core.rag.llm_provider import get_chat_model
        get_chat_model()

        call_kwargs = mock_chat.call_args[1]
        assert call_kwargs.get("temperature") is None

    @patch("core.rag.llm_provider.ChatOpenAI")
    @patch("core.rag.llm_provider.settings", _make_settings(
        LLM_PROVIDER="minimax", MINIMAX_MODEL_ID="MiniMax-M2.7-highspeed"
    ))
    def test_minimax_custom_model(self, mock_chat):
        from core.rag.llm_provider import get_chat_model
        get_chat_model()

        call_kwargs = mock_chat.call_args[1]
        assert call_kwargs["model"] == "MiniMax-M2.7-highspeed"

    @patch("core.rag.llm_provider.ChatOpenAI")
    @patch("core.rag.llm_provider.settings", _make_settings(LLM_PROVIDER="MINIMAX"))
    def test_provider_case_insensitive(self, mock_chat):
        from core.rag.llm_provider import get_chat_model
        get_chat_model()

        call_kwargs = mock_chat.call_args[1]
        assert call_kwargs["model"] == "MiniMax-M3"
        assert call_kwargs["base_url"] == "https://api.minimax.io/v1"

    @patch("core.rag.llm_provider.ChatOpenAI")
    @patch("core.rag.llm_provider.settings", _make_settings(LLM_PROVIDER="openai"))
    def test_openai_no_base_url(self, mock_chat):
        from core.rag.llm_provider import get_chat_model
        get_chat_model()

        call_kwargs = mock_chat.call_args[1]
        assert "base_url" not in call_kwargs


# ---------------------------------------------------------------------------
# Tests for get_openai_client
# ---------------------------------------------------------------------------

class TestGetOpenAIClient:
    """Tests for the get_openai_client factory function."""

    @patch("core.rag.llm_provider.OpenAI")
    @patch("core.rag.llm_provider.settings", _make_settings(LLM_PROVIDER="openai"))
    def test_openai_client(self, mock_openai):
        from core.rag.llm_provider import get_openai_client
        get_openai_client()

        mock_openai.assert_called_once_with(api_key="sk-test-openai-key")

    @patch("core.rag.llm_provider.OpenAI")
    @patch("core.rag.llm_provider.settings", _make_settings(LLM_PROVIDER="minimax"))
    def test_minimax_client(self, mock_openai):
        from core.rag.llm_provider import get_openai_client
        get_openai_client()

        mock_openai.assert_called_once_with(
            api_key="mm-test-key",
            base_url="https://api.minimax.io/v1",
        )


# ---------------------------------------------------------------------------
# Tests for get_model_id
# ---------------------------------------------------------------------------

class TestGetModelId:
    """Tests for the get_model_id helper function."""

    @patch("core.rag.llm_provider.settings", _make_settings(LLM_PROVIDER="openai"))
    def test_openai_model_id(self):
        from core.rag.llm_provider import get_model_id
        assert get_model_id() == "gpt-4o-mini"

    @patch("core.rag.llm_provider.settings", _make_settings(LLM_PROVIDER="minimax"))
    def test_minimax_model_id(self):
        from core.rag.llm_provider import get_model_id
        assert get_model_id() == "MiniMax-M3"

    @patch("core.rag.llm_provider.settings", _make_settings(
        LLM_PROVIDER="minimax", MINIMAX_MODEL_ID="MiniMax-M2.7-highspeed"
    ))
    def test_minimax_custom_model_id(self):
        from core.rag.llm_provider import get_model_id
        assert get_model_id() == "MiniMax-M2.7-highspeed"


# ---------------------------------------------------------------------------
# Tests for config
# ---------------------------------------------------------------------------

class TestConfig:
    """Tests for config settings related to MiniMax."""

    def test_default_provider_is_openai(self):
        """Verify the default LLM provider is OpenAI."""
        settings = _make_settings()
        assert settings.LLM_PROVIDER == "openai"

    def test_minimax_config_fields_exist(self):
        """Verify MiniMax config fields can be set."""
        settings = _make_settings(
            LLM_PROVIDER="minimax",
            MINIMAX_API_KEY="test-key",
            MINIMAX_MODEL_ID="MiniMax-M3",
        )
        assert settings.MINIMAX_API_KEY == "test-key"
        assert settings.MINIMAX_MODEL_ID == "MiniMax-M3"

    def test_minimax_provider_setting(self):
        """Verify LLM_PROVIDER can be set to minimax."""
        settings = _make_settings(LLM_PROVIDER="minimax")
        assert settings.LLM_PROVIDER == "minimax"


# ---------------------------------------------------------------------------
# Tests for GptCommunicator with MiniMax
# ---------------------------------------------------------------------------

class TestGptCommunicator:
    """Tests for the GptCommunicator class with multi-provider support."""

    @patch("core.rag.llm_provider.settings", _make_settings(LLM_PROVIDER="openai"))
    def test_communicator_uses_openai_model_id(self):
        from core.rag.llm_provider import get_model_id
        model_id = get_model_id()
        assert model_id == "gpt-4o-mini"

    @patch("core.rag.llm_provider.settings", _make_settings(LLM_PROVIDER="minimax"))
    def test_communicator_uses_minimax_model_id(self):
        from core.rag.llm_provider import get_model_id
        model_id = get_model_id()
        assert model_id == "MiniMax-M3"

    @patch("core.rag.llm_provider.OpenAI")
    @patch("core.rag.llm_provider.settings", _make_settings(LLM_PROVIDER="minimax"))
    def test_communicator_minimax_client_has_base_url(self, mock_openai):
        from core.rag.llm_provider import get_openai_client
        get_openai_client()
        call_kwargs = mock_openai.call_args[1]
        assert call_kwargs["base_url"] == "https://api.minimax.io/v1"

    @patch("core.rag.llm_provider.OpenAI")
    @patch("core.rag.llm_provider.settings", _make_settings(LLM_PROVIDER="openai"))
    def test_communicator_openai_client_no_base_url(self, mock_openai):
        from core.rag.llm_provider import get_openai_client
        get_openai_client()
        call_kwargs = mock_openai.call_args[1]
        assert "base_url" not in call_kwargs


# ---------------------------------------------------------------------------
# Tests for bonus superlinked RAG provider
# ---------------------------------------------------------------------------

class TestBonusLlmProvider:
    """Tests for the bonus superlinked RAG llm_provider module."""

    @patch("config.settings", _make_settings(LLM_PROVIDER="minimax"))
    def test_bonus_provider_minimax(self):
        bonus_dir = str(SRC_DIR / "bonus_superlinked_rag")
        if bonus_dir not in sys.path:
            sys.path.insert(0, bonus_dir)

        with patch("langchain_openai.ChatOpenAI") as mock_chat:
            # Re-import to pick up the patched settings
            import importlib
            import llm.llm_provider as bonus_provider
            importlib.reload(bonus_provider)
            bonus_provider.get_chat_model(temperature=0.5)

            call_kwargs = mock_chat.call_args[1]
            assert call_kwargs["model"] == "MiniMax-M3"
            assert call_kwargs["base_url"] == "https://api.minimax.io/v1"
            assert call_kwargs["temperature"] == 0.5

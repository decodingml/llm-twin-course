"""Integration tests for MiniMax LLM provider.

These tests make real API calls to the MiniMax API.
They require the MINIMAX_API_KEY environment variable to be set.

Run with: pytest tests/test_llm_provider_integration.py -v
"""

import os
import sys
from pathlib import Path

import pytest

SRC_DIR = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))
sys.path.insert(0, str(SRC_DIR / "core"))

MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY")
skip_no_key = pytest.mark.skipif(
    not MINIMAX_API_KEY,
    reason="MINIMAX_API_KEY not set",
)


@skip_no_key
class TestMiniMaxIntegration:
    """Integration tests that call the MiniMax API."""

    def test_chat_completion(self):
        """Test a basic chat completion via MiniMax's OpenAI-compatible API."""
        from openai import OpenAI

        client = OpenAI(
            api_key=MINIMAX_API_KEY,
            base_url="https://api.minimax.io/v1",
        )
        response = client.chat.completions.create(
            model="MiniMax-M3",
            messages=[{"role": "user", "content": "Say hello in one word."}],
            temperature=0,
            max_tokens=10,
        )
        assert response.choices[0].message.content is not None
        assert len(response.choices[0].message.content.strip()) > 0

    def test_langchain_chat_model(self):
        """Test ChatOpenAI with MiniMax base_url."""
        from langchain_openai import ChatOpenAI

        model = ChatOpenAI(
            model="MiniMax-M3",
            api_key=MINIMAX_API_KEY,
            base_url="https://api.minimax.io/v1",
            temperature=0,
            max_tokens=10,
        )
        response = model.invoke("Say hello in one word.")
        assert response.content is not None
        assert len(response.content.strip()) > 0

    def test_provider_factory_minimax(self):
        """Test the get_chat_model factory with MiniMax provider."""
        from unittest.mock import patch
        from types import SimpleNamespace

        settings = SimpleNamespace(
            LLM_PROVIDER="minimax",
            MINIMAX_API_KEY=MINIMAX_API_KEY,
            MINIMAX_MODEL_ID="MiniMax-M3",
            OPENAI_MODEL_ID="gpt-4o-mini",
            OPENAI_API_KEY=None,
        )

        with patch("core.rag.llm_provider.settings", settings):
            from core.rag.llm_provider import get_chat_model
            model = get_chat_model(temperature=0, max_tokens=10)
            response = model.invoke("Say hello in one word.")
            assert response.content is not None
            assert len(response.content.strip()) > 0

"""Unit tests for harness base models and the factory.

Uses pytest-httpx to mock HTTP calls — no live Ollama needed.
"""

import json
import pytest
import httpx
from pytest_httpx import HTTPXMock

from devmentor.harness.base import ChatMessage, HarnessResponse
from devmentor.harness.ollama import OllamaHarness
from devmentor.harness.openai_compat import OpenAICompatHarness


# ── ChatMessage ───────────────────────────────────────────────────────────────

class TestChatMessage:
    def test_valid_roles(self):
        for role in ("system", "user", "assistant"):
            msg = ChatMessage(role=role, content="hello")
            assert msg.role == role

    def test_content_stored(self):
        msg = ChatMessage(role="user", content="review my code")
        assert msg.content == "review my code"


# ── HarnessResponse ───────────────────────────────────────────────────────────

class TestHarnessResponse:
    def test_minimal_response(self):
        r = HarnessResponse(text="looks good", model="mistral:7b")
        assert r.text == "looks good"
        assert r.model == "mistral:7b"
        assert r.prompt_tokens is None

    def test_full_response(self):
        r = HarnessResponse(
            text="output",
            model="mistral:7b",
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
        )
        assert r.total_tokens == 150


# ── OllamaHarness (mocked) ────────────────────────────────────────────────────

OLLAMA_CHAT_RESPONSE = {
    "model": "mistral:7b",
    "message": {"role": "assistant", "content": "Your code looks fine."},
    "prompt_eval_count": 42,
    "eval_count": 10,
    "done": True,
}

OLLAMA_TAGS_RESPONSE = {
    "models": [{"name": "mistral:7b"}, {"name": "llama3:8b"}]
}


@pytest.mark.asyncio
async def test_ollama_chat(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url="http://localhost:11434/api/chat",
        json=OLLAMA_CHAT_RESPONSE,
    )
    harness = OllamaHarness(base_url="http://localhost:11434", model="mistral:7b")
    messages = [ChatMessage(role="user", content="review this")]
    response = await harness.chat(messages)
    assert response.text == "Your code looks fine."
    assert response.model == "mistral:7b"
    assert response.prompt_tokens == 42
    assert response.completion_tokens == 10
    await harness.close()


@pytest.mark.asyncio
async def test_ollama_health_check_ok(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url="http://localhost:11434/api/tags",
        json=OLLAMA_TAGS_RESPONSE,
    )
    harness = OllamaHarness(base_url="http://localhost:11434", model="mistral:7b")
    assert await harness.health_check() is True
    await harness.close()


@pytest.mark.asyncio
async def test_ollama_health_check_unreachable():
    harness = OllamaHarness(base_url="http://localhost:19999", model="mistral:7b")
    # Port 19999 should not be listening — health check must return False
    result = await harness.health_check()
    assert result is False
    await harness.close()

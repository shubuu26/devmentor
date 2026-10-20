"""Unit tests for DevMentorAgent using a mock harness."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from devmentor.agent.core import DevMentorAgent, AnalysisRequest, AnalysisMode
from devmentor.harness.base import BaseHarness, ChatMessage, HarnessResponse


def make_mock_harness(response_text: str = "All looks good!") -> BaseHarness:
    """Build a mock harness that returns a fixed response."""
    harness = MagicMock(spec=BaseHarness)
    harness.model_name = "mock-model"
    harness.chat = AsyncMock(return_value=HarnessResponse(
        text=response_text,
        model="mock-model",
        prompt_tokens=50,
        completion_tokens=20,
        total_tokens=70,
    ))
    harness.health_check = AsyncMock(return_value=True)

    async def mock_stream(*args, **kwargs):
        for token in response_text.split():
            yield token

    harness.stream_chat = mock_stream
    return harness


class TestDevMentorAgent:
    @pytest.mark.asyncio
    async def test_analyze_review(self):
        agent = DevMentorAgent(make_mock_harness("Code looks clean."))
        request = AnalysisRequest(mode=AnalysisMode.REVIEW, code="x = 1", language="python")
        response = await agent.analyze(request)
        assert response.result == "Code looks clean."
        assert response.mode == "review"
        assert response.model == "mock-model"
        assert response.latency_ms is not None

    @pytest.mark.asyncio
    async def test_analyze_all_modes(self):
        for mode in AnalysisMode:
            agent = DevMentorAgent(make_mock_harness(f"Result for {mode}"))
            request = AnalysisRequest(
                mode=mode,
                code="print('hello')",
                language="python",
                question="test question",
            )
            response = await agent.analyze(request)
            assert response.mode == mode.value

    @pytest.mark.asyncio
    async def test_stream_analyze(self):
        agent = DevMentorAgent(make_mock_harness("hello world"))
        request = AnalysisRequest(mode=AnalysisMode.EXPLAIN, code="x=1", language="python")
        tokens = []
        async for token in agent.stream_analyze(request):
            tokens.append(token)
        assert len(tokens) > 0
        assert "hello" in tokens

    @pytest.mark.asyncio
    async def test_health_ok(self):
        agent = DevMentorAgent(make_mock_harness())
        result = await agent.health()
        assert result["status"] == "ok"

    def test_extract_code_blocks(self):
        text = "Here:\n```python\nprint('hi')\n```\nDone."
        blocks = DevMentorAgent.extract_code_blocks(text)
        assert len(blocks) == 1
        assert "print('hi')" in blocks[0]

    def test_extract_multiple_code_blocks(self):
        text = "```python\nx=1\n```\nand\n```javascript\nconsole.log(1)\n```"
        blocks = DevMentorAgent.extract_code_blocks(text)
        assert len(blocks) == 2

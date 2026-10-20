"""Core DevMentor agent — orchestrates harness + prompt construction.

This is the single entry point for all analysis operations.
It is used by both the FastAPI server and the CLI.
"""

from __future__ import annotations

import re
import time
from enum import Enum
from typing import AsyncIterator, Optional

from pydantic import BaseModel, Field

from devmentor.config import settings
from devmentor.harness.base import BaseHarness, ChatMessage
from devmentor.agent.prompts import SYSTEM_PROMPT, build_user_prompt


class AnalysisMode(str, Enum):
    REVIEW = "review"
    EXPLAIN = "explain"
    DEBUG = "debug"
    IMPROVE = "improve"
    SECURITY = "security"
    COMPLEXITY = "complexity"
    GENERATE = "generate"


class AnalysisRequest(BaseModel):
    """Input payload for a DevMentor analysis."""

    mode: AnalysisMode = Field(
        ...,
        description="Type of analysis to perform",
        examples=["review", "debug", "explain"],
    )
    code: str = Field(
        default="",
        description="The code snippet to analyse (may be empty for pure generation tasks)",
        max_length=50_000,
    )
    language: str = Field(
        default="python",
        description="Programming language of the code",
        max_length=64,
    )
    question: str = Field(
        default="",
        description="Optional specific question or context from the developer",
        max_length=2_000,
    )
    max_new_tokens: Optional[int] = Field(
        default=None,
        ge=64,
        le=8192,
        description="Override the default max_new_tokens from settings",
    )
    temperature: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=2.0,
        description="Override the default temperature from settings",
    )


class AnalysisResponse(BaseModel):
    """Structured response from a DevMentor analysis."""

    mode: str
    language: str
    result: str
    model: str
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    latency_ms: Optional[float] = None


class DevMentorAgent:
    """The main agent that wires prompts to the LLM harness."""

    def __init__(self, harness: BaseHarness) -> None:
        self._harness = harness

    @property
    def harness(self) -> BaseHarness:
        return self._harness

    async def analyze(self, request: AnalysisRequest) -> AnalysisResponse:
        """Run a full (non-streaming) analysis and return a structured response."""
        messages = self._build_messages(request)

        t0 = time.monotonic()
        response = await self._harness.chat(
            messages=messages,
            max_new_tokens=request.max_new_tokens or settings.max_new_tokens,
            temperature=request.temperature if request.temperature is not None else settings.temperature,
        )
        latency_ms = (time.monotonic() - t0) * 1000

        return AnalysisResponse(
            mode=request.mode.value,
            language=request.language,
            result=response.text.strip(),
            model=response.model,
            prompt_tokens=response.prompt_tokens,
            completion_tokens=response.completion_tokens,
            latency_ms=round(latency_ms, 1),
        )

    async def stream_analyze(self, request: AnalysisRequest) -> AsyncIterator[str]:
        """Stream tokens for a real-time chat experience."""
        messages = self._build_messages(request)
        async for token in self._harness.stream_chat(
            messages=messages,
            max_new_tokens=request.max_new_tokens or settings.max_new_tokens,
            temperature=request.temperature if request.temperature is not None else settings.temperature,
        ):
            yield token

    async def health(self) -> dict:
        """Check that the underlying harness is reachable."""
        ok = await self._harness.health_check()
        return {
            "status": "ok" if ok else "unreachable",
            "backend": type(self._harness).__name__,
            "model": self._harness.model_name,
        }

    # ── Private helpers ────────────────────────────────────────────────────────

    def _build_messages(self, request: AnalysisRequest) -> list[ChatMessage]:
        """Construct the full message list for the harness."""
        user_prompt = build_user_prompt(
            mode=request.mode.value,
            code=request.code,
            language=request.language,
            question=request.question,
        )
        return [
            ChatMessage(role="system", content=SYSTEM_PROMPT),
            ChatMessage(role="user", content=user_prompt),
        ]

    @staticmethod
    def extract_code_blocks(text: str) -> list[str]:
        """Pull fenced code blocks out of an LLM response for downstream use."""
        pattern = r"```(?:\w+)?\n(.*?)```"
        return re.findall(pattern, text, re.DOTALL)

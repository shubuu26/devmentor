"""Abstract base class for all model harness backends.

Every backend must implement the `chat` and `health_check` coroutines.
This keeps the agent layer completely decoupled from the underlying
inference engine (Ollama, vLLM, HuggingFace, etc.).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional

from pydantic import BaseModel


class ChatMessage(BaseModel):
    """A single turn in a conversation."""

    role: str  # "system" | "user" | "assistant"
    content: str


class HarnessResponse(BaseModel):
    """Structured response returned by any harness backend."""

    text: str
    model: str
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    # Backend-specific raw response, useful for debugging
    raw: Optional[dict] = None


class BaseHarness(ABC):
    """Abstract base class every harness backend must implement."""

    @abstractmethod
    async def chat(
        self,
        messages: list[ChatMessage],
        max_new_tokens: int = 2048,
        temperature: float = 0.2,
    ) -> HarnessResponse:
        """Send a list of chat messages and return a structured response."""
        ...

    @abstractmethod
    async def stream_chat(
        self,
        messages: list[ChatMessage],
        max_new_tokens: int = 2048,
        temperature: float = 0.2,
    ) -> AsyncIterator[str]:
        """Stream tokens one chunk at a time."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Return True if the backend is reachable and ready."""
        ...

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Human-readable model identifier."""
        ...

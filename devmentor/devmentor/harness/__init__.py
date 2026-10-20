"""Model harness — pluggable backends for open-weight LLM inference."""

from devmentor.harness.base import BaseHarness, ChatMessage, HarnessResponse
from devmentor.harness.ollama import OllamaHarness
from devmentor.harness.openai_compat import OpenAICompatHarness
from devmentor.harness.factory import get_harness

__all__ = [
    "BaseHarness",
    "ChatMessage",
    "HarnessResponse",
    "OllamaHarness",
    "OpenAICompatHarness",
    "get_harness",
]

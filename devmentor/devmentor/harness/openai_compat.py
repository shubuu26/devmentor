"""OpenAI-compatible harness.

Works with any server that implements the OpenAI Chat Completions API:
  - LM Studio (local GUI, Windows/Mac/Linux)
  - vLLM          `python -m vllm.entrypoints.openai.api_server ...`
  - Together AI   https://api.together.xyz/v1
  - Anyscale, Groq, Perplexity, etc.
  - Any self-hosted model served via litellm proxy

Set OPENAI_COMPAT_BASE_URL and OPENAI_COMPAT_MODEL in your .env.
"""

from __future__ import annotations

import json
from typing import AsyncIterator

import httpx

from devmentor.harness.base import BaseHarness, ChatMessage, HarnessResponse


class OpenAICompatHarness(BaseHarness):
    """Harness for OpenAI-compatible /v1/chat/completions endpoints."""

    def __init__(
        self,
        base_url: str = "http://localhost:1234/v1",
        model: str = "mistral-7b-instruct",
        api_key: str = "not-needed",
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers=self._headers,
            timeout=120.0,
        )

    @property
    def model_name(self) -> str:
        return self._model

    async def health_check(self) -> bool:
        try:
            resp = await self._client.get("/models")
            return resp.status_code == 200
        except httpx.ConnectError:
            return False

    async def chat(
        self,
        messages: list[ChatMessage],
        max_new_tokens: int = 2048,
        temperature: float = 0.2,
    ) -> HarnessResponse:
        payload = {
            "model": self._model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "max_tokens": max_new_tokens,
            "temperature": temperature,
            "stream": False,
        }
        resp = await self._client.post("/chat/completions", json=payload)
        resp.raise_for_status()
        data = resp.json()

        choice = data["choices"][0]
        usage = data.get("usage", {})
        return HarnessResponse(
            text=choice["message"]["content"],
            model=data.get("model", self._model),
            prompt_tokens=usage.get("prompt_tokens"),
            completion_tokens=usage.get("completion_tokens"),
            total_tokens=usage.get("total_tokens"),
            raw=data,
        )

    async def stream_chat(
        self,
        messages: list[ChatMessage],
        max_new_tokens: int = 2048,
        temperature: float = 0.2,
    ) -> AsyncIterator[str]:
        payload = {
            "model": self._model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "max_tokens": max_new_tokens,
            "temperature": temperature,
            "stream": True,
        }
        async with self._client.stream("POST", "/chat/completions", json=payload) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line.startswith("data: "):
                    continue
                payload_str = line[6:].strip()
                if payload_str == "[DONE]":
                    break
                chunk = json.loads(payload_str)
                delta = chunk["choices"][0].get("delta", {})
                token = delta.get("content", "")
                if token:
                    yield token

    async def close(self) -> None:
        await self._client.aclose()

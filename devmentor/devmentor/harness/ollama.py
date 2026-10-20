"""Ollama harness — connects to a local Ollama server for open-weight LLM inference.

Ollama supports Mistral, LLaMA 3, CodeLlama, Phi-3, DeepSeek-Coder and many more.
Run `ollama pull mistral:7b` to get started.

API reference: https://github.com/ollama/ollama/blob/main/docs/api.md
"""

from __future__ import annotations

import json
from typing import AsyncIterator

import httpx

from devmentor.harness.base import BaseHarness, ChatMessage, HarnessResponse


class OllamaHarness(BaseHarness):
    """Harness that speaks the Ollama HTTP API."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "mistral:7b") -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        # Shared async client — reuse connections for lower latency
        self._client = httpx.AsyncClient(base_url=self._base_url, timeout=120.0)

    @property
    def model_name(self) -> str:
        return self._model

    async def health_check(self) -> bool:
        """Ping the Ollama server and verify the model is available."""
        try:
            resp = await self._client.get("/api/tags")
            if resp.status_code != 200:
                return False
            models = [m["name"] for m in resp.json().get("models", [])]
            # Accept partial match so "mistral:7b" matches "mistral:7b-instruct-q4_K_M"
            return any(self._model.split(":")[0] in m for m in models)
        except httpx.ConnectError:
            return False

    async def chat(
        self,
        messages: list[ChatMessage],
        max_new_tokens: int = 2048,
        temperature: float = 0.2,
    ) -> HarnessResponse:
        """Non-streaming chat completion via Ollama /api/chat."""
        payload = {
            "model": self._model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "stream": False,
            "options": {
                "num_predict": max_new_tokens,
                "temperature": temperature,
            },
        }
        resp = await self._client.post("/api/chat", json=payload)
        resp.raise_for_status()
        data = resp.json()

        return HarnessResponse(
            text=data["message"]["content"],
            model=data.get("model", self._model),
            prompt_tokens=data.get("prompt_eval_count"),
            completion_tokens=data.get("eval_count"),
            total_tokens=(
                (data.get("prompt_eval_count") or 0) + (data.get("eval_count") or 0)
            ) or None,
            raw=data,
        )

    async def stream_chat(
        self,
        messages: list[ChatMessage],
        max_new_tokens: int = 2048,
        temperature: float = 0.2,
    ) -> AsyncIterator[str]:
        """Stream tokens from Ollama using NDJSON chunked responses."""
        payload = {
            "model": self._model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "stream": True,
            "options": {
                "num_predict": max_new_tokens,
                "temperature": temperature,
            },
        }
        async with self._client.stream("POST", "/api/chat", json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line.strip():
                    continue
                chunk = json.loads(line)
                token = chunk.get("message", {}).get("content", "")
                if token:
                    yield token
                if chunk.get("done"):
                    break

    async def list_models(self) -> list[str]:
        """Return all model tags available on this Ollama instance."""
        resp = await self._client.get("/api/tags")
        resp.raise_for_status()
        return [m["name"] for m in resp.json().get("models", [])]

    async def pull_model(self, model: str) -> None:
        """Pull a model if not already present (blocking until complete)."""
        async with self._client.stream(
            "POST", "/api/pull", json={"name": model, "stream": True}
        ) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if line.strip():
                    data = json.loads(line)
                    status = data.get("status", "")
                    if status:
                        print(f"[ollama pull] {status}")

    async def close(self) -> None:
        await self._client.aclose()

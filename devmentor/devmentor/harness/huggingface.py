"""HuggingFace local inference harness (optional backend).

Loads any instruction-tuned model directly from HuggingFace Hub or a
local directory using the `transformers` pipeline.

Requires: pip install transformers accelerate torch
GPU recommended but CPU works for small models (phi-3-mini, TinyLlama, etc.)
"""

from __future__ import annotations

from typing import AsyncIterator

from devmentor.harness.base import BaseHarness, ChatMessage, HarnessResponse


class HuggingFaceHarness(BaseHarness):
    """Run open-weight models locally via the HuggingFace transformers library."""

    def __init__(self, model_id: str = "mistralai/Mistral-7B-Instruct-v0.3", device: str = "cpu") -> None:
        self._model_id = model_id
        self._device = device
        self._pipe = None  # lazy-loaded on first use

    def _load(self) -> None:
        """Lazy-load the pipeline to avoid import overhead at startup."""
        if self._pipe is not None:
            return
        try:
            import torch
            from transformers import pipeline
        except ImportError as exc:
            raise ImportError(
                "transformers and torch are required for HuggingFace backend. "
                "Install: pip install transformers accelerate torch"
            ) from exc

        self._pipe = pipeline(
            "text-generation",
            model=self._model_id,
            device_map=self._device,
            torch_dtype="auto",
            trust_remote_code=False,
        )

    @property
    def model_name(self) -> str:
        return self._model_id

    async def health_check(self) -> bool:
        """Always True — local model is always available once loaded."""
        return True

    async def chat(
        self,
        messages: list[ChatMessage],
        max_new_tokens: int = 2048,
        temperature: float = 0.2,
    ) -> HarnessResponse:
        import asyncio

        self._load()

        # transformers pipeline is synchronous; run in thread pool
        formatted = [{"role": m.role, "content": m.content} for m in messages]

        def _generate() -> str:
            outputs = self._pipe(
                formatted,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                do_sample=temperature > 0,
                pad_token_id=self._pipe.tokenizer.eos_token_id,
            )
            # The pipeline returns the full conversation; extract last assistant turn
            return outputs[0]["generated_text"][-1]["content"]

        text = await asyncio.get_event_loop().run_in_executor(None, _generate)
        return HarnessResponse(text=text, model=self._model_id)

    async def stream_chat(
        self,
        messages: list[ChatMessage],
        max_new_tokens: int = 2048,
        temperature: float = 0.2,
    ) -> AsyncIterator[str]:
        """HuggingFace streaming via TextIteratorStreamer."""
        import asyncio
        import threading

        self._load()

        try:
            from transformers import TextIteratorStreamer
        except ImportError as exc:
            raise ImportError("transformers is required") from exc

        streamer = TextIteratorStreamer(self._pipe.tokenizer, skip_prompt=True)
        formatted = [{"role": m.role, "content": m.content} for m in messages]

        def _generate() -> None:
            self._pipe(
                formatted,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                do_sample=temperature > 0,
                streamer=streamer,
                pad_token_id=self._pipe.tokenizer.eos_token_id,
            )

        thread = threading.Thread(target=_generate)
        thread.start()

        loop = asyncio.get_event_loop()
        for token in streamer:
            yield token
            await asyncio.sleep(0)  # yield control back to event loop

        thread.join()

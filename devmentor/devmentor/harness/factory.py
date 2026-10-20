"""Factory function that instantiates the correct harness from settings."""

from __future__ import annotations

from devmentor.config import Backend, settings
from devmentor.harness.base import BaseHarness


def get_harness() -> BaseHarness:
    """Return the configured harness backend singleton.

    Selection order:
      1. DEVMENTOR_BACKEND env var (explicit override)
      2. Defaults to Ollama
    """
    backend = settings.devmentor_backend

    if backend == Backend.OLLAMA:
        from devmentor.harness.ollama import OllamaHarness
        return OllamaHarness(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
        )

    if backend == Backend.OPENAI_COMPAT:
        from devmentor.harness.openai_compat import OpenAICompatHarness
        return OpenAICompatHarness(
            base_url=settings.openai_compat_base_url,
            model=settings.openai_compat_model,
            api_key=settings.openai_compat_api_key,
        )

    if backend == Backend.HUGGINGFACE:
        try:
            from devmentor.harness.huggingface import HuggingFaceHarness
        except ImportError as e:
            raise ImportError(
                "HuggingFace backend requires extra dependencies. "
                "Install them with: pip install transformers accelerate torch"
            ) from e
        return HuggingFaceHarness(
            model_id=settings.hf_model_id,
            device=settings.hf_device,
        )

    raise ValueError(f"Unknown backend: {backend}")

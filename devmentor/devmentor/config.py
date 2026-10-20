"""Centralised settings loaded from environment / .env file."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Backend(str, Enum):
    OLLAMA = "ollama"
    OPENAI_COMPAT = "openai_compat"
    HUGGINGFACE = "huggingface"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Backend selection ─────────────────────────────────────────────────────
    devmentor_backend: Backend = Backend.OLLAMA

    # ── Ollama ────────────────────────────────────────────────────────────────
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "mistral:7b"

    # ── OpenAI-compatible endpoint ────────────────────────────────────────────
    openai_compat_base_url: str = "http://localhost:1234/v1"
    openai_compat_api_key: str = "not-needed"
    openai_compat_model: str = "mistral-7b-instruct"

    # ── HuggingFace ───────────────────────────────────────────────────────────
    hf_model_id: str = "mistralai/Mistral-7B-Instruct-v0.3"
    hf_device: str = "cpu"

    # ── API server ────────────────────────────────────────────────────────────
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = False

    # ── Generation parameters ─────────────────────────────────────────────────
    max_new_tokens: int = Field(default=2048, ge=64, le=8192)
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    context_window: int = Field(default=8192, ge=512, le=131072)

    @field_validator("temperature", mode="before")
    @classmethod
    def clamp_temperature(cls, v: float) -> float:
        return max(0.0, min(float(v), 2.0))


# Singleton instance used across the application
settings = Settings()

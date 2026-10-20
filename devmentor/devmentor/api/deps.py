"""FastAPI dependency injection — shared harness and agent instances."""

from __future__ import annotations

from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from devmentor.harness.factory import get_harness
from devmentor.harness.base import BaseHarness
from devmentor.agent.core import DevMentorAgent


@lru_cache(maxsize=1)
def _harness_singleton() -> BaseHarness:
    """Create the harness once and reuse it for every request."""
    return get_harness()


@lru_cache(maxsize=1)
def _agent_singleton() -> DevMentorAgent:
    return DevMentorAgent(_harness_singleton())


def get_agent() -> DevMentorAgent:
    return _agent_singleton()


AgentDep = Annotated[DevMentorAgent, Depends(get_agent)]

"""Unit tests for the prompt-building layer.

These tests run without a live LLM — they verify that prompts are
assembled correctly for every mode.
"""

import pytest
from devmentor.agent.prompts import build_user_prompt, PROMPTS, SYSTEM_PROMPT


SAMPLE_CODE = """
def add(a, b):
    return a + b
"""


class TestSystemPrompt:
    def test_system_prompt_not_empty(self):
        assert len(SYSTEM_PROMPT) > 100

    def test_system_prompt_mentions_devmentor(self):
        assert "DevMentor" in SYSTEM_PROMPT


class TestBuildUserPrompt:
    @pytest.mark.parametrize("mode", list(PROMPTS.keys()))
    def test_all_modes_produce_nonempty_output(self, mode):
        prompt = build_user_prompt(
            mode=mode,
            code=SAMPLE_CODE,
            language="python",
            question="Is this correct?",
        )
        assert len(prompt) > 50

    def test_review_contains_code(self):
        prompt = build_user_prompt("review", SAMPLE_CODE, "python")
        assert "def add" in prompt

    def test_review_contains_language(self):
        prompt = build_user_prompt("review", SAMPLE_CODE, "typescript")
        assert "typescript" in prompt

    def test_explain_includes_question(self):
        q = "What does this return for negative numbers?"
        prompt = build_user_prompt("explain", SAMPLE_CODE, "python", question=q)
        assert q in prompt

    def test_generate_works_with_empty_code(self):
        prompt = build_user_prompt("generate", "", "rust", question="write a hello world")
        assert "rust" in prompt.lower()
        assert "hello world" in prompt

    def test_unknown_mode_raises(self):
        with pytest.raises(ValueError, match="Unknown mode"):
            build_user_prompt("invalid_mode", SAMPLE_CODE, "python")

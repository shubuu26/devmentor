"""System and user prompt templates for every analysis mode.

All prompts are designed for instruction-tuned open-weight models
(Mistral-Instruct, LLaMA-3-Instruct, CodeLlama-Instruct, etc.).
"""

from __future__ import annotations

SYSTEM_PROMPT = """\
You are DevMentor, an expert software engineer and patient coding tutor.
You help developers write better code by providing accurate, actionable, and educational feedback.
You are powered by a locally-running open-weight language model — you never send code to external servers.

Rules:
- Be concise but complete. No filler or padding.
- Always provide corrected/improved code when relevant.
- Use plain language; avoid jargon unless the user uses it first.
- Reference specific line numbers when discussing issues.
- Never hallucinate API names, library functions, or language features.
- If you are uncertain, say so clearly and explain your reasoning.
- Structure your response with clear headings and numbered lists.
"""

# ── Per-mode user prompt templates ────────────────────────────────────────────
# Use {language}, {code}, {question} as interpolation keys.

PROMPTS: dict[str, str] = {
    "review": """\
Please perform a thorough code review of the following {language} code.

```{language}
{code}
```

Provide:
1. **Overall assessment** (1–2 sentences)
2. **Issues found** — numbered list, each tagged [critical], [warning], or [info], with line references
3. **Corrected code** — apply all fixes in a single clean code block
4. **Learning tips** — 1–2 key takeaways about the patterns or anti-patterns found
""",

    "explain": """\
Please explain the following {language} code clearly.
{question_section}

```{language}
{code}
```

Cover:
1. **What it does** — high-level summary (1–2 sentences)
2. **How it works** — step-by-step walkthrough of the logic
3. **Key concepts** — data structures, algorithms, or patterns used
4. **Gotchas** — any non-obvious behaviour the developer should know
""",

    "debug": """\
The following {language} code has a bug or is not working correctly.
{question_section}

```{language}
{code}
```

Please:
1. **Identify the root cause** — be precise about what is wrong and why
2. **Explain the impact** — what behaviour does the bug cause?
3. **Fixed code** — provide the complete corrected version
4. **Prevention tip** — how to avoid this class of bug in future
""",

    "improve": """\
Please refactor and improve the following {language} code.
{question_section}

```{language}
{code}
```

Focus on:
1. **Readability** — naming, structure, comments
2. **Maintainability** — SOLID, DRY, separation of concerns
3. **Performance** — algorithmic improvements where applicable
4. **Modern idioms** — use language features that clarify intent

Provide the improved code with inline comments explaining each significant change.
""",

    "security": """\
Please perform a security audit of the following {language} code.

```{language}
{code}
```

For each issue found:
1. **Vulnerability name** and CWE ID if applicable
2. **Attack vector** — how an attacker could exploit it
3. **Impact** — what damage could result
4. **Patched code** — the complete fixed version
5. **Security best practices** relevant to this code

Only report real vulnerabilities. Do not invent issues.
""",

    "complexity": """\
Please analyse the algorithmic complexity of the following {language} code.

```{language}
{code}
```

Provide:
1. **Time complexity** — Big-O for each function/method with justification
2. **Space complexity** — Big-O with justification
3. **Bottleneck** — identify the most expensive operation
4. **Optimisation** — suggest a more efficient algorithm or data structure if one exists,
   including its complexity and a code example
""",

    "generate": """\
Please write clean, production-quality {language} code for the following task:

{question}

Requirements:
- Solve exactly the stated task
- Handle edge cases and errors gracefully
- Follow idiomatic {language} conventions
- Include brief inline comments for non-obvious logic
- Keep it simple — do not over-engineer

{code_section}
""",
}


def build_user_prompt(mode: str, code: str, language: str, question: str = "") -> str:
    """Fill in the template for the given mode."""
    template = PROMPTS.get(mode)
    if template is None:
        raise ValueError(f"Unknown mode: {mode!r}. Valid modes: {list(PROMPTS)}")

    question_section = f"\nDeveloper's question: {question}\n" if question else ""
    code_section = f"Existing code to build upon:\n```{language}\n{code}\n```\n" if code else ""

    return template.format(
        language=language or "code",
        code=code,
        question=question,
        question_section=question_section,
        code_section=code_section,
    )

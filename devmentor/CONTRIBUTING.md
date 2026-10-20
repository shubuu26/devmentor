# Contributing to DevMentor

Thanks for your interest in contributing! DevMentor is an open-source project built for
Hacktoberfest 2026 and maintained by the community.

---

## Ways to contribute

- **Bug reports** — open a GitHub Issue with steps to reproduce
- **Feature requests** — open an Issue tagged `enhancement`
- **Bug fixes** — fork → fix → PR
- **New harness backends** — add support for a new inference engine in `devmentor/harness/`
- **New agent modes** — add a new analysis mode to `devmentor/agent/prompts.py` and `core.py`
- **New skills** — add a new skill directory under `skills/`
- **Documentation** — improve the README, add tutorials, fix typos

---

## Development setup

```bash
# 1. Clone the repo
git clone https://github.com/your-username/devmentor.git
cd devmentor

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
.\.venv\Scripts\Activate         # Windows PowerShell

# 3. Install in editable mode with dev dependencies
pip install -e ".[dev]"

# 4. Copy and edit the environment file
cp .env.example .env
# Edit .env to point at your local Ollama or other backend

# 5. Install pre-commit hooks
pre-commit install
```

---

## Running tests

```bash
# All tests (no live LLM needed)
pytest

# With coverage
pytest --cov=devmentor --cov-report=term-missing

# A specific file
pytest tests/test_agent.py -v
```

---

## Adding a new harness backend

1. Create `devmentor/harness/your_backend.py`
2. Subclass `BaseHarness` and implement `chat`, `stream_chat`, `health_check`, `model_name`
3. Add a new `Backend` enum value in `devmentor/config.py`
4. Handle the new backend in `devmentor/harness/factory.py`
5. Add tests in `tests/test_harness.py`

---

## Adding a new analysis mode

1. Add a prompt template to the `PROMPTS` dict in `devmentor/agent/prompts.py`
2. Add the mode to the `AnalysisMode` enum in `devmentor/agent/core.py`
3. Add a CLI command in `devmentor/cli/main.py`
4. Update `SKILL.md` mode table
5. Add a test in `tests/test_prompts.py`

---

## Pull request checklist

- [ ] Tests pass: `pytest`
- [ ] Linter passes: `ruff check .`
- [ ] Type check passes: `mypy devmentor/`
- [ ] New features have tests
- [ ] SKILL.md updated if new modes were added
- [ ] CHANGELOG entry added (or note in PR description)

---

## Code style

- **Formatter / linter:** `ruff` (configured in `pyproject.toml`)
- **Type hints:** encouraged, not strictly required for contributions
- **Docstrings:** one-line for simple functions, full for public API
- **Line length:** 100 characters

---

## Licence

By contributing, you agree that your contributions will be licensed under the MIT License.

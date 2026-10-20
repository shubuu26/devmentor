# DevMentor 🧑‍💻

> **Open-source AI coding assistant powered by open-weight LLMs — built for Hacktoberfest 2026**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://python.org)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-Open%20Standard-green)](https://agentskills.io)
[![Hacktoberfest 2026](https://img.shields.io/badge/Hacktoberfest-2026-orange)](https://hacktoberfest.com)

DevMentor is a fully open-source AI agent that reviews, debugs, explains, and improves your code — **entirely on your machine**, using open-weight models via [Ollama](https://ollama.ai). No API keys. No data leaves your computer.

It ships as:
- A **FastAPI REST server** — call it from any language or tool
- A **CLI** — run `devmentor review myfile.py` from your terminal
- An **Agent Skill** — compatible with the [Agent Skills Open Standard](https://agentskills.io), so it works in Claude Code, GitHub Copilot, Cursor, VS Code, and 40+ other tools out of the box
- A **pluggable model harness** — swap between Ollama, LM Studio, vLLM, HuggingFace, or any OpenAI-compatible endpoint

---

## Features

| Mode | What it does |
|------|-------------|
| `review` | Full code review with severity-tagged issues and a corrected code block |
| `explain` | Plain-English walkthrough of what code does and how |
| `debug` | Root-cause analysis and fixed code |
| `improve` | Refactoring and idiomatic rewrites with inline explanations |
| `security` | Vulnerability audit with CWE IDs and patched code |
| `complexity` | Big-O time and space analysis with optimisation suggestions |
| `generate` | Write new code from a natural language description |

---

## Quick start

### 1. Install Ollama and pull a model

```bash
# Install from https://ollama.ai
ollama pull mistral:7b        # ~4GB, great for code tasks
# Alternatives: llama3:8b, codellama:7b, deepseek-coder:6.7b, phi3:mini
```

### 2. Install DevMentor

```bash
git clone https://github.com/your-username/devmentor.git
cd devmentor
pip install -e .
```

### 3. Configure (optional)

```bash
cp .env.example .env
# Edit .env to change the model or backend
```

### 4. Use it

```bash
# Review a file
devmentor review myfile.py

# Explain a snippet inline
devmentor explain --code "sorted(d.items(), key=lambda x: x[1])" --language python

# Debug with context
devmentor debug myfile.py --question "throws KeyError on line 12"

# Security audit
devmentor security myfile.py

# Generate code
devmentor generate "a thread-safe LRU cache in Python" --language python

# Start the REST API server
devmentor serve
```

---

## REST API

Start the server once, then call it from any language:

```bash
devmentor serve   # starts on http://localhost:8000
# or
uvicorn devmentor.api.main:app --port 8000
```

```bash
# Review code via HTTP
curl -s http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "review",
    "code": "def div(a,b): return a/b",
    "language": "python"
  }' | python -m json.tool

# Stream the response token by token
curl -N http://localhost:8000/api/v1/analyze/stream \
  -H "Content-Type: application/json" \
  -d '{"mode": "debug", "code": "...", "language": "javascript"}'
```

Interactive API docs: **http://localhost:8000/docs**

---

## Docker (batteries included)

Starts Ollama + pulls the default model + starts the API server in one command:

```bash
docker compose up -d
docker compose exec ollama ollama pull mistral:7b   # first-time only
curl http://localhost:8000/health
```

---

## Agent Skill (Agent Skills Open Standard)

DevMentor ships a fully spec-compliant Agent Skill at `skills/code-mentor/`.

### Install in Claude Code

```bash
cp -r skills/code-mentor ~/.claude/skills/
```

### Install in any compatible tool

Copy the `skills/code-mentor/` folder to your agent tool's skills directory.
The skill works in: Claude Code, GitHub Copilot (VS Code), Cursor, Gemini CLI,
OpenCode, JetBrains Junie, AWS Kiro, and 40+ other tools.

### Skill structure

```
skills/code-mentor/
├── SKILL.md                        # Required: metadata + instructions
├── scripts/
│   └── call_devmentor.py           # Helper script agents can invoke
├── references/
│   ├── prompt-templates.md         # Prompt templates per mode
│   └── troubleshooting.md          # Debug guide for agents
└── assets/
    └── example-review-output.md    # Example output for agents
```

---

## Model harness

DevMentor's model harness is a clean abstraction over multiple inference backends.
Switch backends by changing one line in `.env`:

```bash
# Use Ollama (default, recommended)
DEVMENTOR_BACKEND=ollama
OLLAMA_MODEL=mistral:7b

# Use LM Studio / vLLM / any OpenAI-compatible server
DEVMENTOR_BACKEND=openai_compat
OPENAI_COMPAT_BASE_URL=http://localhost:1234/v1
OPENAI_COMPAT_MODEL=mistral-7b-instruct

# Use HuggingFace local inference
DEVMENTOR_BACKEND=huggingface
HF_MODEL_ID=microsoft/Phi-3-mini-4k-instruct
HF_DEVICE=cpu
```

### Recommended open-weight models

| Model | Size | Strengths |
|-------|------|-----------|
| `mistral:7b` | 4GB | Fast, great all-rounder |
| `codellama:7b` | 4GB | Best for code-specific tasks |
| `deepseek-coder:6.7b` | 4GB | Excellent code generation |
| `llama3:8b` | 5GB | Strong reasoning and explanation |
| `phi3:mini` | 2GB | Fastest, best for low-RAM machines |

---

## Project structure

```
devmentor/
├── devmentor/
│   ├── agent/
│   │   ├── core.py          # DevMentorAgent — main orchestration
│   │   └── prompts.py       # Per-mode prompt templates
│   ├── api/
│   │   ├── main.py          # FastAPI app factory
│   │   ├── routes.py        # All HTTP routes
│   │   └── deps.py          # Dependency injection
│   ├── cli/
│   │   └── main.py          # Typer CLI (devmentor command)
│   ├── harness/
│   │   ├── base.py          # Abstract BaseHarness
│   │   ├── ollama.py        # Ollama backend
│   │   ├── openai_compat.py # OpenAI-compatible backend
│   │   ├── huggingface.py   # HuggingFace local backend
│   │   └── factory.py       # Backend factory function
│   └── config.py            # Pydantic settings
├── skills/
│   └── code-mentor/         # Agent Skill (Open Standard)
│       ├── SKILL.md
│       ├── scripts/
│       ├── references/
│       └── assets/
├── tests/                   # Pytest test suite
├── examples/                # Jupyter notebooks and demo scripts
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

---

## Development

```bash
pip install -e ".[dev]"
pytest                           # run all tests (no live LLM needed)
ruff check .                     # lint
mypy devmentor/                  # type check
```

---

## Contributing

Contributions are very welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).

Ideas for contributions:
- New harness backends (llama.cpp, Groq, Together AI)
- New analysis modes (test generation, documentation, migration)
- IDE plugins that consume the REST API
- New Agent Skills for specialised domains

---

## Why open-weight AI?

This project is built entirely on open-weight models for three reasons:

1. **Privacy** — your code never leaves your machine
2. **Cost** — zero inference cost after setup
3. **Reproducibility** — pin a model version and get consistent results forever

The model harness is designed to be swapped — if a better open-weight code model is released
tomorrow, change one line in `.env` and DevMentor uses it.

---

## License

MIT — see [LICENSE](LICENSE).

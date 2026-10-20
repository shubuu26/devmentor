# Troubleshooting Guide

## The DevMentor API is not reachable

**Symptoms:** `curl http://localhost:8000/health` returns a connection error.

**Fix:**
```bash
# 1. Check if the server process is running
# On Linux/macOS:
ps aux | grep uvicorn
# On Windows PowerShell:
Get-Process python -ErrorAction SilentlyContinue

# 2. Start the server manually
cd /path/to/devmentor
uvicorn devmentor.api.main:app --host 0.0.0.0 --port 8000

# 3. Or use the CLI
devmentor serve
```

---

## Ollama is not running

**Symptoms:** `{"error": "Ollama unreachable at http://localhost:11434"}`

**Fix:**
```bash
# Install Ollama from https://ollama.ai
# Then start it:
ollama serve        # Linux/macOS
# On Windows, Ollama runs as a system tray app — click the icon to start

# Pull a model if you haven't already:
ollama pull mistral:7b
# Other options: llama3:8b, codellama:7b, deepseek-coder:6.7b, phi3:mini
```

---

## Model not found

**Symptoms:** `{"error": "model 'mistral:7b' not found"}`

**Fix:**
```bash
# List available models
ollama list

# Pull the default model
ollama pull mistral:7b

# Or change the model in your .env file:
OLLAMA_MODEL=llama3:8b
```

---

## Response is slow

**Possible causes:**
- Running a large model on CPU only
- Insufficient RAM (7B models need ~8GB, 13B need ~16GB)

**Fix:**
```bash
# Use a smaller/quantised model
ollama pull phi3:mini          # ~2GB, fast on CPU
ollama pull deepseek-coder:1.3b  # smallest code model

# Update .env
OLLAMA_MODEL=phi3:mini
MAX_NEW_TOKENS=1024  # reduce output length
```

---

## Python version errors

**Requirement:** Python 3.10 or higher.

```bash
python --version
# If < 3.10, install a newer version from https://python.org

# Use a virtual environment
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.\.venv\Scripts\Activate    # Windows PowerShell
pip install -e .
```

---

## Import errors after install

```bash
# Reinstall in editable mode
pip install -e ".[dev]"

# Check the package is importable
python -c "import devmentor; print(devmentor.__version__)"
```

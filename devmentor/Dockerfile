# ── Stage 1: builder ──────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build tools
RUN pip install --no-cache-dir hatchling

# Copy dependency manifest first (better layer caching)
COPY pyproject.toml .
COPY devmentor/__init__.py devmentor/__init__.py

# Install runtime dependencies into a prefix we can copy to the final stage
RUN pip install --no-cache-dir --prefix=/install .

# ── Stage 2: runtime ──────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

LABEL org.opencontainers.image.title="DevMentor" \
      org.opencontainers.image.description="Open-source AI coding assistant powered by open-weight LLMs" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.source="https://github.com/your-username/devmentor"

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy the application source
COPY devmentor/ devmentor/
COPY skills/ skills/
COPY .env.example .env.example

# Non-root user for security
RUN useradd -m -u 1001 devmentor && chown -R devmentor:devmentor /app
USER devmentor

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEVMENTOR_BACKEND=ollama \
    API_HOST=0.0.0.0 \
    API_PORT=8000

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "devmentor.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

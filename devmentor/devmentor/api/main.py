"""FastAPI application factory for DevMentor.

Start the server:
    uvicorn devmentor.api.main:app --host 0.0.0.0 --port 8000
    # or
    devmentor serve
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from devmentor import __version__
from devmentor.api.routes import router
from devmentor.api.deps import _harness_singleton


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: warm up the harness singleton and verify the backend is reachable."""
    harness = _harness_singleton()
    ok = await harness.health_check()
    if not ok:
        import warnings
        warnings.warn(
            f"LLM backend ({type(harness).__name__}) is not reachable at startup. "
            "Requests will fail until the backend is available.",
            stacklevel=1,
        )
    yield
    # Shutdown: close HTTP clients
    if hasattr(harness, "close"):
        await harness.close()


def create_app() -> FastAPI:
    app = FastAPI(
        title="DevMentor",
        description=(
            "An open-source AI coding assistant agent powered by open-weight LLMs. "
            "Supports code review, debugging, explanation, refactoring, security audits, "
            "and complexity analysis. Compatible with the Agent Skills Open Standard."
        ),
        version=__version__,
        license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
        contact={"name": "DevMentor Contributors", "url": "https://github.com/your-username/devmentor"},
        lifespan=lifespan,
    )

    # Allow all origins in development — restrict in production
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)
    return app


# Module-level app instance for uvicorn
app = create_app()

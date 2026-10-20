"""DevMentor CLI — interact with the agent from your terminal.

Usage examples:
    devmentor review myfile.py
    devmentor debug myfile.py --question "Why does this throw KeyError?"
    devmentor explain --code "lambda x: x*2" --language python
    devmentor generate --question "write a binary search function in Rust"
    devmentor serve
    devmentor health
    devmentor models
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.table import Table

from devmentor import __version__

app = typer.Typer(
    name="devmentor",
    help="DevMentor — open-source AI coding assistant powered by open-weight LLMs",
    rich_markup_mode="rich",
    no_args_is_help=True,
)
console = Console()
err_console = Console(stderr=True, style="bold red")


def _get_agent():
    """Lazily import and build the agent (avoids slow imports at CLI startup)."""
    from devmentor.harness.factory import get_harness
    from devmentor.agent.core import DevMentorAgent
    return DevMentorAgent(get_harness())


def _read_code(file: Optional[Path], code: Optional[str]) -> str:
    """Resolve code from a file path or inline --code flag."""
    if file and file.exists():
        return file.read_text(encoding="utf-8")
    if code:
        return code
    if not sys.stdin.isatty():
        return sys.stdin.read()
    err_console.print("Provide a FILE argument, --code, or pipe code via stdin.")
    raise typer.Exit(1)


def _run(coro):
    """Run an async coroutine from a sync CLI command."""
    return asyncio.run(coro)


# ── Commands ──────────────────────────────────────────────────────────────────

@app.command()
def review(
    file: Optional[Path] = typer.Argument(None, help="Path to source file"),
    code: Optional[str] = typer.Option(None, "--code", "-c", help="Inline code snippet"),
    language: str = typer.Option("python", "--language", "-l", help="Programming language"),
    stream: bool = typer.Option(False, "--stream", help="Stream tokens as they generate"),
):
    """Review code for bugs, style, and best-practice issues."""
    _analyze_cmd("review", file, code, language, "", stream)


@app.command()
def explain(
    file: Optional[Path] = typer.Argument(None, help="Path to source file"),
    code: Optional[str] = typer.Option(None, "--code", "-c", help="Inline code snippet"),
    language: str = typer.Option("python", "--language", "-l", help="Programming language"),
    question: str = typer.Option("", "--question", "-q", help="Specific question to answer"),
    stream: bool = typer.Option(False, "--stream", help="Stream tokens"),
):
    """Explain what a piece of code does in plain English."""
    _analyze_cmd("explain", file, code, language, question, stream)


@app.command()
def debug(
    file: Optional[Path] = typer.Argument(None, help="Path to source file"),
    code: Optional[str] = typer.Option(None, "--code", "-c", help="Inline code snippet"),
    language: str = typer.Option("python", "--language", "-l", help="Programming language"),
    question: str = typer.Option("", "--question", "-q", help="Describe the bug/symptom"),
    stream: bool = typer.Option(False, "--stream", help="Stream tokens"),
):
    """Find and fix bugs in your code."""
    _analyze_cmd("debug", file, code, language, question, stream)


@app.command()
def improve(
    file: Optional[Path] = typer.Argument(None, help="Path to source file"),
    code: Optional[str] = typer.Option(None, "--code", "-c", help="Inline code snippet"),
    language: str = typer.Option("python", "--language", "-l", help="Programming language"),
    question: str = typer.Option("", "--question", "-q", help="Focus area (e.g. performance)"),
    stream: bool = typer.Option(False, "--stream", help="Stream tokens"),
):
    """Refactor and improve code quality."""
    _analyze_cmd("improve", file, code, language, question, stream)


@app.command()
def security(
    file: Optional[Path] = typer.Argument(None, help="Path to source file"),
    code: Optional[str] = typer.Option(None, "--code", "-c", help="Inline code snippet"),
    language: str = typer.Option("python", "--language", "-l", help="Programming language"),
    stream: bool = typer.Option(False, "--stream", help="Stream tokens"),
):
    """Audit code for security vulnerabilities."""
    _analyze_cmd("security", file, code, language, "", stream)


@app.command()
def complexity(
    file: Optional[Path] = typer.Argument(None, help="Path to source file"),
    code: Optional[str] = typer.Option(None, "--code", "-c", help="Inline code snippet"),
    language: str = typer.Option("python", "--language", "-l", help="Programming language"),
    stream: bool = typer.Option(False, "--stream", help="Stream tokens"),
):
    """Analyse time and space complexity (Big-O)."""
    _analyze_cmd("complexity", file, code, language, "", stream)


@app.command()
def generate(
    question: str = typer.Argument(..., help="What to generate, e.g. 'a binary search in Rust'"),
    language: str = typer.Option("python", "--language", "-l", help="Target language"),
    existing_code: Optional[str] = typer.Option(None, "--code", "-c", help="Existing code to build upon"),
    stream: bool = typer.Option(False, "--stream", help="Stream tokens"),
):
    """Generate new code from a natural language description."""
    _analyze_cmd("generate", None, existing_code or "", language, question, stream)


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", help="Bind host"),
    port: int = typer.Option(8000, help="Bind port"),
    reload: bool = typer.Option(False, "--reload", help="Auto-reload on code changes (dev only)"),
):
    """Start the DevMentor REST API server."""
    try:
        import uvicorn
    except ImportError:
        err_console.print("uvicorn is required. Install: pip install uvicorn[standard]")
        raise typer.Exit(1)

    console.print(Panel(
        f"[bold green]DevMentor API server starting[/]\n"
        f"  Host : {host}\n"
        f"  Port : {port}\n"
        f"  Docs : http://localhost:{port}/docs\n"
        f"  [dim]Press Ctrl+C to stop[/]",
        title="DevMentor",
        border_style="green",
    ))
    uvicorn.run("devmentor.api.main:app", host=host, port=port, reload=reload)


@app.command()
def health():
    """Check that the LLM backend is reachable."""
    agent = _get_agent()
    result = _run(agent.health())
    status = result.get("status", "unknown")
    color = "green" if status == "ok" else "red"
    console.print(Panel(
        f"[bold {color}]Status:[/] {status}\n"
        f"Backend: {result.get('backend')}\n"
        f"Model  : {result.get('model')}",
        title="Health Check",
        border_style=color,
    ))
    if status != "ok":
        raise typer.Exit(1)


@app.command()
def models():
    """List models available on the Ollama backend."""
    from devmentor.harness.factory import get_harness
    from devmentor.config import Backend, settings

    if settings.devmentor_backend != Backend.OLLAMA:
        err_console.print("The `models` command only works with the Ollama backend.")
        raise typer.Exit(1)

    harness = get_harness()
    model_list = _run(harness.list_models())

    table = Table(title="Available Ollama Models", header_style="bold cyan")
    table.add_column("Model", style="green")
    for m in model_list:
        table.add_row(m)
    console.print(table)


@app.command()
def version():
    """Print DevMentor version."""
    console.print(f"DevMentor [bold green]{__version__}[/]")


# ── Shared helper ─────────────────────────────────────────────────────────────

def _analyze_cmd(
    mode: str,
    file: Optional[Path],
    code: Optional[str],
    language: str,
    question: str,
    stream: bool,
) -> None:
    from devmentor.agent.core import AnalysisRequest

    # For generate mode, code can be empty
    if mode == "generate":
        source = code or ""
    else:
        source = _read_code(file, code)

    # Show the input code panel
    if source:
        console.print(Panel(
            Syntax(source[:3000], language, theme="monokai", line_numbers=True),
            title=f"[bold]{language.upper()} Code[/]",
            border_style="blue",
        ))

    request = AnalysisRequest(
        mode=mode,
        code=source,
        language=language,
        question=question,
    )

    agent = _get_agent()

    console.print(f"\n[bold cyan]DevMentor[/] [dim]({mode})[/] — thinking...\n")

    if stream:
        async def _stream():
            async for token in agent.stream_analyze(request):
                console.print(token, end="")
            console.print()

        _run(_stream())
    else:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(f"Running {mode} analysis with {agent.harness.model_name}…", total=None)
            response = _run(agent.analyze(request))

        console.print(Panel(
            Markdown(response.result),
            title=f"[bold green]DevMentor — {mode.upper()}[/]",
            border_style="green",
        ))
        console.print(
            f"[dim]Model: {response.model} | "
            f"Tokens: {response.completion_tokens or '?'} | "
            f"Latency: {response.latency_ms}ms[/]"
        )

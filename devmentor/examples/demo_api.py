#!/usr/bin/env python3
"""DevMentor REST API Demo

Demonstrates every analysis mode via direct HTTP calls.
Requires: devmentor server running on localhost:8000
Start it: devmentor serve   (or: uvicorn devmentor.api.main:app --port 8000)
"""

import asyncio
import json
import httpx
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax

BASE_URL = "http://localhost:8000"
console = Console()


async def call(client: httpx.AsyncClient, mode: str, code: str, language: str = "python", question: str = "") -> dict:
    """Call the DevMentor API and return the response dict."""
    resp = await client.post(
        "/api/v1/analyze",
        json={"mode": mode, "code": code, "language": language, "question": question},
        timeout=120.0,
    )
    resp.raise_for_status()
    return resp.json()


async def stream_call(client: httpx.AsyncClient, mode: str, code: str, language: str = "python") -> None:
    """Stream a response and print tokens as they arrive."""
    async with client.stream(
        "POST",
        "/api/v1/analyze/stream",
        json={"mode": mode, "code": code, "language": language},
        timeout=120.0,
    ) as resp:
        resp.raise_for_status()
        async for token in resp.aiter_text():
            console.print(token, end="")
    console.print()


def show(title: str, result: dict) -> None:
    console.print(Panel(
        Markdown(result["result"]),
        title=f"[bold green]{title}[/]",
        border_style="green",
    ))
    console.print(
        f"[dim]Model: {result['model']} | "
        f"Completion tokens: {result.get('completion_tokens', '?')} | "
        f"Latency: {result.get('latency_ms')}ms[/]\n"
    )


async def main() -> None:
    async with httpx.AsyncClient(base_url=BASE_URL) as client:

        # ── Health check ──────────────────────────────────────────────────────
        console.rule("[bold cyan]Health Check[/]")
        health = (await client.get("/health")).json()
        console.print(health)

        # ── Code Review ───────────────────────────────────────────────────────
        console.rule("[bold cyan]Code Review[/]")
        sql_code = '''
import sqlite3

def get_user(id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE id = {id}")
    return cursor.fetchone()
'''
        result = await call(client, "review", sql_code, "python")
        show("Review — SQL Injection Example", result)

        # ── Debug ─────────────────────────────────────────────────────────────
        console.rule("[bold cyan]Debug[/]")
        broken_code = '''
def calculate_average(numbers):
    total = 0
    for i in range(len(numbers) + 1):   # off-by-one
        total += numbers[i]
    return total / len(numbers)
'''
        result = await call(client, "debug", broken_code, "python", "throws IndexError")
        show("Debug — Off-by-One Error", result)

        # ── Explain ───────────────────────────────────────────────────────────
        console.rule("[bold cyan]Explain[/]")
        code = "result = list(map(lambda x: x**2, filter(lambda x: x % 2 == 0, range(20))))"
        result = await call(client, "explain", code, "python", "What does this produce?")
        show("Explain — Functional One-liner", result)

        # ── Improve ───────────────────────────────────────────────────────────
        console.rule("[bold cyan]Improve[/]")
        messy_code = '''
def p(x):
    r = []
    for i in range(0, len(x)):
        if x[i] % 2 == 0:
            r = r + [x[i] * x[i]]
    return r
'''
        result = await call(client, "improve", messy_code, "python")
        show("Improve — Refactoring Suggestion", result)

        # ── Security ──────────────────────────────────────────────────────────
        console.rule("[bold cyan]Security Audit[/]")
        insecure_code = '''
from flask import Flask, request, render_template_string

app = Flask(__name__)

@app.route("/greet")
def greet():
    name = request.args.get("name", "World")
    template = f"<h1>Hello, {name}!</h1>"
    return render_template_string(template)
'''
        result = await call(client, "security", insecure_code, "python")
        show("Security — Flask SSTI Vulnerability", result)

        # ── Complexity ────────────────────────────────────────────────────────
        console.rule("[bold cyan]Complexity Analysis[/]")
        bubble_sort = '''
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr
'''
        result = await call(client, "complexity", bubble_sort, "python")
        show("Complexity — Bubble Sort Analysis", result)

        # ── Generate (streaming) ─────────────────────────────────────────────
        console.rule("[bold cyan]Generate (streaming)[/]")
        console.print("[bold]Generating: a thread-safe LRU cache in Python...[/]\n")
        await stream_call(
            client,
            "generate",
            "",
            "python",
        )

    console.rule("[bold green]Demo complete![/]")


if __name__ == "__main__":
    asyncio.run(main())

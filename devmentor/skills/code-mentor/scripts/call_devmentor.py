#!/usr/bin/env python3
"""CLI helper script bundled with the code-mentor skill.

Agents can invoke this script directly to call the DevMentor API without
needing to know the full HTTP request shape.

Usage:
    python call_devmentor.py --mode review --code "def foo(): pass" --language python
    python call_devmentor.py --mode debug --code "..." --question "Why is this slow?"
"""

import argparse
import json
import sys
import urllib.request
import urllib.error

BASE_URL = "http://localhost:8000"


def call_api(mode: str, code: str, language: str = "python", question: str = "") -> dict:
    payload = json.dumps({
        "mode": mode,
        "code": code,
        "language": language,
        "question": question,
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{BASE_URL}/api/v1/analyze",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        return {"error": f"Cannot reach DevMentor API at {BASE_URL}: {e.reason}"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Call the DevMentor API from the command line")
    parser.add_argument("--mode", required=True,
                        choices=["review", "explain", "debug", "improve", "security", "complexity", "generate"],
                        help="Analysis mode")
    parser.add_argument("--code", required=True, help="Code snippet to analyse")
    parser.add_argument("--language", default="python", help="Programming language")
    parser.add_argument("--question", default="", help="Optional specific question")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    result = call_api(args.mode, args.code, args.language, args.question)

    if args.json:
        print(json.dumps(result, indent=2))
    elif "error" in result:
        print(f"ERROR: {result['error']}", file=sys.stderr)
        sys.exit(1)
    else:
        print(result.get("result", result))


if __name__ == "__main__":
    main()

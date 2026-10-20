#!/usr/bin/env bash
# DevMentor CLI Demo Script
# Run: bash examples/demo_cli.sh
# Requires: devmentor installed, Ollama running with mistral:7b

set -e

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

header() { echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"; echo -e "${GREEN}$1${NC}"; echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"; }

# ── 1. Health check ────────────────────────────────────────────────────────────
header "1. Health check"
devmentor health

# ── 2. Code review ────────────────────────────────────────────────────────────
header "2. Code Review — spotting SQL injection + connection leak"
devmentor review --language python --code '
import sqlite3

def get_user(id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE id = {id}")
    return cursor.fetchone()
'

# ── 3. Debug ──────────────────────────────────────────────────────────────────
header "3. Debug — off-by-one error"
devmentor debug --language python \
  --question "This throws IndexError on the last element" \
  --code '
def last_item(lst):
    return lst[len(lst)]
'

# ── 4. Explain ────────────────────────────────────────────────────────────────
header "4. Explain — Python one-liner"
devmentor explain \
  --code "result = {k: v for k, v in sorted(d.items(), key=lambda x: x[1], reverse=True)}" \
  --language python \
  --question "What does this do and when would I use it?"

# ── 5. Security audit ────────────────────────────────────────────────────────
header "5. Security Audit — hardcoded credentials"
devmentor security --language python --code '
import requests

API_KEY = "sk-prod-abc123xyz"
SECRET  = "my_super_secret_password"

def fetch_data(endpoint):
    return requests.get(endpoint, headers={"Authorization": f"Bearer {API_KEY}"})
'

# ── 6. Complexity analysis ────────────────────────────────────────────────────
header "6. Complexity Analysis — nested loop"
devmentor complexity --language python --code '
def find_duplicates(nums):
    duplicates = []
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] == nums[j] and nums[i] not in duplicates:
                duplicates.append(nums[i])
    return duplicates
'

# ── 7. Generate ───────────────────────────────────────────────────────────────
header "7. Generate — LRU cache in Python"
devmentor generate "a thread-safe LRU cache with a configurable max size" --language python

echo -e "\n${GREEN}✓ Demo complete!${NC}"

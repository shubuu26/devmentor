# Example: Code Review Output

This is a sample output from DevMentor to give agents an idea of the expected response format.

---

**Input code (Python):**
```python
def get_user(id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE id = {id}")
    return cursor.fetchone()
```

---

**DevMentor output:**

**Summary:** This function has a critical SQL injection vulnerability and leaks database connections.

1. **[critical]** SQL Injection — Line 4: The `id` parameter is interpolated directly into the SQL string using an f-string. An attacker can pass `id = "1 OR 1=1"` to dump all users. Fix: use parameterised queries: `cursor.execute("SELECT * FROM users WHERE id = ?", (id,))`

2. **[critical]** Connection leak — Line 2: `conn` is never closed. Under load this exhausts SQLite file handles. Fix: use a `with` statement or call `conn.close()` in a `finally` block.

3. **[warning]** No error handling — If the database file doesn't exist or `id` is invalid, the exception propagates uncaught. Wrap in `try/except sqlite3.Error`.

4. **[info]** Type hint missing — Add `id: int` and `-> tuple | None` to make the signature self-documenting.

**Fixed code:**
```python
import sqlite3
from typing import Optional

def get_user(user_id: int) -> Optional[tuple]:
    try:
        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            return cursor.fetchone()
    except sqlite3.Error as e:
        raise RuntimeError(f"Database error: {e}") from e
```

**Learning tips:**
- Always use parameterised queries (`?` placeholders) — never f-strings or `%s` with user input. This is the #1 cause of SQL injection.
- Python's `sqlite3.connect()` as a context manager automatically commits/rolls back but does **not** close the connection — always pair it with `conn.close()` or use a connection pool.

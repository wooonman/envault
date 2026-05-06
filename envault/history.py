"""Vault history: record snapshots of env state with timestamps."""

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

HISTORY_FILE = ".env.vault.history"


def load_history(history_path: str = HISTORY_FILE) -> List[Dict[str, Any]]:
    """Load history entries from disk. Returns empty list if file missing."""
    p = Path(history_path)
    if not p.exists():
        return []
    with p.open("r") as f:
        return json.load(f)


def save_history(
    entries: List[Dict[str, Any]], history_path: str = HISTORY_FILE
) -> None:
    """Persist history entries to disk."""
    with open(history_path, "w") as f:
        json.dump(entries, f, indent=2)


def record_snapshot(
    label: str,
    keys: List[str],
    diff_summary: str,
    history_path: str = HISTORY_FILE,
) -> None:
    """Append a snapshot entry to the history file."""
    entries = load_history(history_path)
    entries.append(
        {
            "timestamp": time.time(),
            "label": label,
            "keys": keys,
            "diff": diff_summary,
        }
    )
    save_history(entries, history_path)


def format_history(entries: List[Dict[str, Any]]) -> str:
    """Return a printable summary of history entries."""
    if not entries:
        return "No history recorded yet."
    lines = []
    for i, e in enumerate(entries, 1):
        ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(e["timestamp"]))
        key_count = len(e.get("keys", []))
        lines.append(f"[{i}] {ts}  label={e['label']}  keys={key_count}")
        if e.get("diff"):
            for dl in e["diff"].splitlines():
                lines.append(f"      {dl}")
    return "\n".join(lines)

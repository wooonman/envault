"""Audit log for envault — tracks who did what and when."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any

DEFAULT_AUDIT_FILE = ".envault_audit.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_audit(audit_path: str = DEFAULT_AUDIT_FILE) -> List[Dict[str, Any]]:
    """Load existing audit log entries, returning empty list if file missing."""
    p = Path(audit_path)
    if not p.exists():
        return []
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_audit(entries: List[Dict[str, Any]], audit_path: str = DEFAULT_AUDIT_FILE) -> None:
    """Persist audit log entries to disk."""
    with open(audit_path, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2)
        f.write("\n")


def record_event(
    action: str,
    details: Dict[str, Any] | None = None,
    audit_path: str = DEFAULT_AUDIT_FILE,
    user: str | None = None,
) -> Dict[str, Any]:
    """Append a single audit event and return it."""
    entries = load_audit(audit_path)
    event: Dict[str, Any] = {
        "timestamp": _now_iso(),
        "action": action,
        "user": user or os.environ.get("USER") or os.environ.get("USERNAME") or "unknown",
        "details": details or {},
    }
    entries.append(event)
    save_audit(entries, audit_path)
    return event


def format_audit_log(entries: List[Dict[str, Any]]) -> str:
    """Return a human-readable audit log string."""
    if not entries:
        return "No audit events recorded."
    lines = []
    for e in entries:
        detail_str = ", ".join(f"{k}={v}" for k, v in e.get("details", {}).items())
        detail_part = f" ({detail_str})" if detail_str else ""
        lines.append(f"[{e['timestamp']}] {e['user']} — {e['action']}{detail_part}")
    return "\n".join(lines)

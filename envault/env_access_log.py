"""Track per-key access events (reads/writes) with timestamps."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from envault.audit import _now_iso

ACCESS_LOG_KEY = "__access_log__"


@dataclass
class AccessEntry:
    key: str
    action: str  # 'read' | 'write' | 'delete'
    timestamp: str

    def __str__(self) -> str:
        return f"[{self.timestamp}] {self.action.upper():6s}  {self.key}"


def _get_log(vault: dict) -> List[dict]:
    meta = vault.get("__meta__", {})
    return list(meta.get(ACCESS_LOG_KEY, []))


def _set_log(vault: dict, log: List[dict]) -> None:
    vault.setdefault("__meta__", {})[ACCESS_LOG_KEY] = log


def record_access(vault_path: Path, key: str, action: str) -> AccessEntry:
    """Append an access event for *key* to the vault's embedded access log."""
    from envault.vault import load_vault, save_vault

    if action not in ("read", "write", "delete"):
        raise ValueError(f"Unknown action: {action!r}")

    vault = load_vault(vault_path)
    log = _get_log(vault)
    entry = {"key": key, "action": action, "timestamp": _now_iso()}
    log.append(entry)
    _set_log(vault, log)
    save_vault(vault_path, vault)
    return AccessEntry(**entry)


def get_access_log(
    vault_path: Path,
    key: Optional[str] = None,
    action: Optional[str] = None,
) -> List[AccessEntry]:
    """Return access log entries, optionally filtered by key and/or action."""
    from envault.vault import load_vault

    vault = load_vault(vault_path)
    raw = _get_log(vault)
    entries = [AccessEntry(**r) for r in raw]
    if key:
        entries = [e for e in entries if e.key == key]
    if action:
        entries = [e for e in entries if e.action == action]
    return entries


def format_access_log(entries: List[AccessEntry]) -> str:
    if not entries:
        return "No access log entries."
    return "\n".join(str(e) for e in entries)

"""TTL (time-to-live) support for vault entries."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional


class TTLError(Exception):
    pass


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.isoformat()


def get_ttl_data(vault_path: str | Path) -> dict:
    """Return the ttl metadata dict from the vault, or empty dict."""
    vault_path = Path(vault_path)
    if not vault_path.exists():
        return {}
    data = json.loads(vault_path.read_text())
    return data.get("_ttl", {})


def set_expiry(vault_path: str | Path, key: str, seconds: int) -> datetime:
    """Set an expiry on a key. Returns the expiry datetime."""
    vault_path = Path(vault_path)
    data = json.loads(vault_path.read_text())
    if key not in data.get("entries", {}):
        raise TTLError(f"Key '{key}' not found in vault.")
    if seconds <= 0:
        raise TTLError("TTL must be a positive number of seconds.")
    expires_at = _now() + timedelta(seconds=seconds)
    ttl = data.setdefault("_ttl", {})
    ttl[key] = _iso(expires_at)
    vault_path.write_text(json.dumps(data, indent=2))
    return expires_at


def clear_expiry(vault_path: str | Path, key: str) -> bool:
    """Remove TTL from a key. Returns True if there was one to remove."""
    vault_path = Path(vault_path)
    data = json.loads(vault_path.read_text())
    ttl = data.get("_ttl", {})
    if key not in ttl:
        return False
    del ttl[key]
    vault_path.write_text(json.dumps(data, indent=2))
    return True


def is_expired(vault_path: str | Path, key: str) -> bool:
    """Return True if the key has a TTL and it has passed."""
    ttl_data = get_ttl_data(vault_path)
    if key not in ttl_data:
        return False
    expires_at = datetime.fromisoformat(ttl_data[key])
    return _now() >= expires_at


def purge_expired(vault_path: str | Path) -> list[str]:
    """Delete all expired keys from the vault. Returns list of removed keys."""
    vault_path = Path(vault_path)
    data = json.loads(vault_path.read_text())
    ttl = data.get("_ttl", {})
    removed = []
    for key, expiry_str in list(ttl.items()):
        expires_at = datetime.fromisoformat(expiry_str)
        if _now() >= expires_at:
            data.get("entries", {}).pop(key, None)
            del ttl[key]
            removed.append(key)
    vault_path.write_text(json.dumps(data, indent=2))
    return removed


def format_ttl_report(ttl_data: dict) -> str:
    """Format TTL metadata into a human-readable report."""
    if not ttl_data:
        return "No TTL entries set."
    now = _now()
    lines = []
    for key, expiry_str in sorted(ttl_data.items()):
        expires_at = datetime.fromisoformat(expiry_str)
        status = "EXPIRED" if now >= expires_at else "active"
        lines.append(f"  {key}: expires {expiry_str} [{status}]")
    return "\n".join(lines)

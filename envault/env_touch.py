"""Touch (refresh timestamp) for vault entries without changing their value."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from envault.vault import load_vault, save_vault
from envault.audit import record_event


class TouchError(Exception):
    pass


@dataclass
class TouchResult:
    touched: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        lines = []
        if self.touched:
            lines.append(f"Touched ({len(self.touched)}): {', '.join(self.touched)}")
        if self.skipped:
            lines.append(f"Not found ({len(self.skipped)}): {', '.join(self.skipped)}")
        return "\n".join(lines) if lines else "Nothing to touch."


def touch_key(vault_path: str, key: str, password: str) -> TouchResult:
    """Refresh the 'updated_at' timestamp of a single key."""
    return touch_keys(vault_path, [key], password)


def touch_keys(vault_path: str, keys: List[str], password: str) -> TouchResult:
    """Refresh the 'updated_at' timestamp for one or more keys."""
    from datetime import datetime, timezone

    vault = load_vault(vault_path)
    entries = vault.get("entries", {})
    result = TouchResult()

    for key in keys:
        if key not in entries:
            result.skipped.append(key)
            continue
        entries[key]["updated_at"] = datetime.now(timezone.utc).isoformat()
        result.touched.append(key)

    if result.touched:
        vault["entries"] = entries
        save_vault(vault_path, vault)
        record_event(
            vault_path,
            "touch",
            {"keys": result.touched},
            password,
        )

    return result


def format_touch_report(result: TouchResult) -> str:
    return str(result)

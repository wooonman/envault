"""Check and report the lock/encryption status of vault entries."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from envault.vault import load_vault
from envault.lock_unlock_helpers import vault_keys


@dataclass
class LockStatusEntry:
    key: str
    is_encrypted: bool
    has_tags: bool
    has_note: bool
    is_pinned: bool
    is_archived: bool

    def __str__(self) -> str:
        flags = []
        if self.is_encrypted:
            flags.append("encrypted")
        if self.has_tags:
            flags.append("tagged")
        if self.has_note:
            flags.append("noted")
        if self.is_pinned:
            flags.append("pinned")
        if self.is_archived:
            flags.append("archived")
        flag_str = ", ".join(flags) if flags else "plain"
        return f"{self.key}: [{flag_str}]"


@dataclass
class LockStatusResult:
    entries: list[LockStatusEntry] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.entries)

    @property
    def encrypted_count(self) -> int:
        return sum(1 for e in self.entries if e.is_encrypted)

    def __str__(self) -> str:
        lines = [str(e) for e in self.entries]
        lines.append(f"\nTotal: {self.total} | Encrypted: {self.encrypted_count}")
        return "\n".join(lines)


def check_lock_status(vault_path: str) -> LockStatusResult:
    """Return lock/encryption status for every entry in the vault."""
    vault = load_vault(vault_path)
    entries_data = vault.get("entries", {})
    tags_map = vault.get("_tags", {})
    notes_map = vault.get("_notes", {})
    pins = set(vault.get("_pins", []))
    archived = set(vault.get("_archive", {}).keys())

    results: list[LockStatusEntry] = []
    for key in sorted(entries_data.keys()):
        entry = entries_data[key]
        is_encrypted = isinstance(entry, dict) and "ct" in entry
        results.append(
            LockStatusEntry(
                key=key,
                is_encrypted=is_encrypted,
                has_tags=bool(tags_map.get(key)),
                has_note=bool(notes_map.get(key)),
                is_pinned=key in pins,
                is_archived=key in archived,
            )
        )
    return LockStatusResult(entries=results)


def format_status_report(result: LockStatusResult) -> str:
    """Human-readable status report."""
    if not result.entries:
        return "Vault is empty."
    return str(result)

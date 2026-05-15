"""Archive (soft-delete) and restore keys in the vault."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from envault.vault import load_vault, save_vault

_ARCHIVE_KEY = "__archive__"


class ArchiveError(Exception):
    pass


@dataclass
class ArchiveResult:
    key: str
    action: str  # 'archived' | 'restored'

    def __str__(self) -> str:
        return f"{self.action}: {self.key}"


def _get_archive(vault: dict) -> dict:
    meta = vault.get("__meta__", {})
    return meta.get(_ARCHIVE_KEY, {})


def _set_archive(vault: dict, archive: dict) -> None:
    vault.setdefault("__meta__", {})[_ARCHIVE_KEY] = archive


def list_archived(vault_path: str) -> List[str]:
    """Return sorted list of archived key names."""
    vault = load_vault(vault_path)
    return sorted(_get_archive(vault).keys())


def archive_key(vault_path: str, key: str) -> ArchiveResult:
    """Move *key* from active entries into the archive section."""
    vault = load_vault(vault_path)
    if key not in vault.get("entries", {}):
        raise ArchiveError(f"Key not found: {key}")
    entry = vault["entries"].pop(key)
    archive = _get_archive(vault)
    archive[key] = entry
    _set_archive(vault, archive)
    save_vault(vault_path, vault)
    return ArchiveResult(key=key, action="archived")


def restore_key(vault_path: str, key: str) -> ArchiveResult:
    """Move *key* from the archive back into active entries."""
    vault = load_vault(vault_path)
    archive = _get_archive(vault)
    if key not in archive:
        raise ArchiveError(f"Archived key not found: {key}")
    if key in vault.get("entries", {}):
        raise ArchiveError(f"Key already exists in active entries: {key}")
    entry = archive.pop(key)
    _set_archive(vault, archive)
    vault.setdefault("entries", {})[key] = entry
    save_vault(vault_path, vault)
    return ArchiveResult(key=key, action="restored")


def format_archive_list(keys: List[str]) -> str:
    if not keys:
        return "No archived keys."
    lines = ["Archived keys:"]
    for k in keys:
        lines.append(f"  - {k}")
    return "\n".join(lines)

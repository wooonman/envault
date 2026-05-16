"""Trim whitespace from vault entry values."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from envault.vault import load_vault, save_vault
from envault.crypto import encrypt_to_b64, decrypt_from_b64


class TrimError(Exception):
    pass


@dataclass
class TrimResult:
    trimmed: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        lines = []
        if self.trimmed:
            lines.append(f"Trimmed {len(self.trimmed)} key(s): {', '.join(self.trimmed)}")
        else:
            lines.append("No keys needed trimming.")
        if self.skipped:
            lines.append(f"Skipped {len(self.skipped)} key(s) (already clean): {', '.join(self.skipped)}")
        return "\n".join(lines)


def trim_entries(
    vault_path: str,
    password: str,
    keys: List[str] | None = None,
    dry_run: bool = False,
) -> TrimResult:
    """Decrypt each entry, strip leading/trailing whitespace, re-encrypt if changed.

    Args:
        vault_path: Path to the vault JSON file.
        password: Master password used to decrypt/re-encrypt entries.
        keys: Optional list of specific keys to process; None means all keys.
        dry_run: If True, report what would change without writing.

    Returns:
        TrimResult listing which keys were trimmed and which were already clean.
    """
    vault = load_vault(vault_path)
    entries: dict = vault.get("entries", {})

    target_keys = keys if keys is not None else list(entries.keys())
    missing = [k for k in target_keys if k not in entries]
    if missing:
        raise TrimError(f"Key(s) not found in vault: {', '.join(missing)}")

    result = TrimResult()

    for key in target_keys:
        raw = decrypt_from_b64(entries[key], password)
        stripped = raw.strip()
        if stripped != raw:
            result.trimmed.append(key)
            if not dry_run:
                entries[key] = encrypt_to_b64(stripped, password)
        else:
            result.skipped.append(key)

    if result.trimmed and not dry_run:
        vault["entries"] = entries
        save_vault(vault_path, vault)

    return result

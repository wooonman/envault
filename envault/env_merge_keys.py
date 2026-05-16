"""Merge specific keys from one vault into another, with conflict handling."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from envault.vault import load_vault, save_vault
from envault.crypto import decrypt_from_b64, encrypt_to_b64


class MergeKeysError(Exception):
    pass


@dataclass
class MergeKeysResult:
    copied: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    overwritten: List[str] = field(default_factory=list)
    missing: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        lines = []
        if self.copied:
            lines.append(f"Copied:      {', '.join(self.copied)}")
        if self.overwritten:
            lines.append(f"Overwritten: {', '.join(self.overwritten)}")
        if self.skipped:
            lines.append(f"Skipped:     {', '.join(self.skipped)}")
        if self.missing:
            lines.append(f"Not found:   {', '.join(self.missing)}")
        if not lines:
            return "Nothing to merge."
        return "\n".join(lines)


def merge_keys(
    src_path: str,
    dest_path: str,
    keys: List[str],
    src_password: str,
    dest_password: str,
    overwrite: bool = False,
) -> MergeKeysResult:
    """Copy specific keys from src vault into dest vault.

    Values are re-encrypted under dest_password.
    """
    src = load_vault(src_path)
    dest = load_vault(dest_path)

    src_entries = src.get("entries", {})
    dest_entries = dest.get("entries", {})

    result = MergeKeysResult()

    for key in keys:
        if key not in src_entries:
            result.missing.append(key)
            continue

        try:
            plaintext = decrypt_from_b64(src_entries[key], src_password)
        except Exception as exc:
            raise MergeKeysError(f"Failed to decrypt '{key}' from source: {exc}") from exc

        if key in dest_entries and not overwrite:
            result.skipped.append(key)
            continue

        try:
            dest_entries[key] = encrypt_to_b64(plaintext, dest_password)
        except Exception as exc:
            raise MergeKeysError(f"Failed to encrypt '{key}' for destination: {exc}") from exc

        if key in dest_entries and overwrite and key not in result.missing:
            result.overwritten.append(key)
        else:
            result.copied.append(key)

    dest["entries"] = dest_entries
    save_vault(dest_path, dest)
    return result

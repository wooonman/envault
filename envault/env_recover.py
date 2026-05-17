"""Recover vault entries from a backup file into the active vault."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from envault.vault import load_vault, save_vault
from envault.crypto import decrypt_from_b64, encrypt_to_b64


class RecoverError(Exception):
    pass


@dataclass
class RecoverResult:
    recovered: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    overwritten: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        lines = []
        if self.recovered:
            lines.append(f"Recovered ({len(self.recovered)}): {', '.join(self.recovered)}")
        if self.overwritten:
            lines.append(f"Overwritten ({len(self.overwritten)}): {', '.join(self.overwritten)}")
        if self.skipped:
            lines.append(f"Skipped ({len(self.skipped)}): {', '.join(self.skipped)}")
        if not lines:
            return "Nothing to recover."
        return "\n".join(lines)


def recover_entries(
    backup_path: str | Path,
    vault_path: str | Path,
    backup_password: str,
    vault_password: str,
    keys: Optional[List[str]] = None,
    overwrite: bool = False,
) -> RecoverResult:
    """Recover entries from *backup_path* into *vault_path*.

    Args:
        backup_path: Path to the source backup vault file.
        vault_path: Path to the destination (active) vault file.
        backup_password: Password used to decrypt the backup vault.
        vault_password: Password used to encrypt into the active vault.
        keys: If given, only recover these specific keys.
        overwrite: If True, overwrite existing keys in the active vault.

    Returns:
        A RecoverResult describing what happened.

    Raises:
        RecoverError: If the backup file does not exist or a key cannot be decrypted.
    """
    backup_path = Path(backup_path)
    if not backup_path.exists():
        raise RecoverError(f"Backup file not found: {backup_path}")

    backup_vault = load_vault(str(backup_path))
    active_vault = load_vault(str(vault_path)) if Path(vault_path).exists() else {}

    backup_entries = {k: v for k, v in backup_vault.items() if not k.startswith("_")}
    target_keys = keys if keys is not None else list(backup_entries.keys())

    result = RecoverResult()

    for key in target_keys:
        if key not in backup_entries:
            raise RecoverError(f"Key '{key}' not found in backup vault.")

        try:
            plaintext = decrypt_from_b64(backup_entries[key], backup_password)
        except Exception as exc:
            raise RecoverError(f"Failed to decrypt '{key}' from backup: {exc}") from exc

        if key in active_vault and not key.startswith("_"):
            if not overwrite:
                result.skipped.append(key)
                continue
            result.overwritten.append(key)
        else:
            result.recovered.append(key)

        active_vault[key] = encrypt_to_b64(plaintext, vault_password)

    save_vault(str(vault_path), active_vault)
    return result

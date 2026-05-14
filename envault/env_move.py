"""Move (rename + copy to new key, removing old) entries between vaults or within the same vault."""

from dataclasses import dataclass
from typing import Optional

from envault.vault import load_vault, save_vault
from envault.crypto import decrypt_from_b64, encrypt_to_b64


class MoveError(Exception):
    pass


@dataclass
class MoveResult:
    source_key: str
    dest_key: str
    source_vault: str
    dest_vault: str
    cross_vault: bool

    def __str__(self) -> str:
        if self.cross_vault:
            return (
                f"Moved '{self.source_key}' from '{self.source_vault}' "
                f"to '{self.dest_key}' in '{self.dest_vault}'"
            )
        return f"Moved '{self.source_key}' -> '{self.dest_key}' in '{self.source_vault}'"


def move_key(
    src_vault_path: str,
    src_key: str,
    dest_key: str,
    password: str,
    dest_vault_path: Optional[str] = None,
    overwrite: bool = False,
) -> MoveResult:
    """Move src_key to dest_key, optionally across vaults.

    Decrypts with password and re-encrypts under dest_key.
    Raises MoveError on conflicts or missing keys.
    """
    dest_vault_path = dest_vault_path or src_vault_path
    cross_vault = dest_vault_path != src_vault_path

    src_data = load_vault(src_vault_path)
    dest_data = load_vault(dest_vault_path) if cross_vault else src_data

    entries = src_data.get("entries", {})
    dest_entries = dest_data.get("entries", {}) if cross_vault else entries

    if src_key not in entries:
        raise MoveError(f"Key '{src_key}' not found in '{src_vault_path}'")

    if src_key == dest_key and not cross_vault:
        raise MoveError("Source and destination key are the same within the same vault")

    if dest_key in dest_entries and not overwrite:
        raise MoveError(
            f"Key '{dest_key}' already exists in destination vault. Use overwrite=True to replace."
        )

    # Decrypt value from source, re-encrypt for destination
    plaintext = decrypt_from_b64(entries[src_key], password)
    dest_entries[dest_key] = encrypt_to_b64(plaintext, password)

    # Remove from source
    del entries[src_key]

    if cross_vault:
        src_data["entries"] = entries
        dest_data["entries"] = dest_entries
        save_vault(src_vault_path, src_data)
        save_vault(dest_vault_path, dest_data)
    else:
        src_data["entries"] = entries
        save_vault(src_vault_path, src_data)

    return MoveResult(
        source_key=src_key,
        dest_key=dest_key,
        source_vault=src_vault_path,
        dest_vault=dest_vault_path,
        cross_vault=cross_vault,
    )


def format_move_report(result: MoveResult) -> str:
    return str(result)

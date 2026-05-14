"""Bulk copy all entries from one vault to another (or within the same vault with a prefix/suffix)."""

from dataclasses import dataclass, field
from typing import Optional

from envault.vault import load_vault, save_vault
from envault.crypto import decrypt_from_b64, encrypt_to_b64


class BulkCopyError(Exception):
    pass


@dataclass
class BulkCopyResult:
    copied: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    source_vault: str = ""
    dest_vault: str = ""

    def __str__(self) -> str:
        lines = [f"Bulk copy: {self.source_vault} -> {self.dest_vault}"]
        if self.copied:
            lines.append(f"  Copied  ({len(self.copied)}): {', '.join(self.copied)}")
        if self.skipped:
            lines.append(f"  Skipped ({len(self.skipped)}): {', '.join(self.skipped)}")
        if not self.copied and not self.skipped:
            lines.append("  No entries found.")
        return "\n".join(lines)


def bulk_copy(
    src_path: str,
    dest_path: str,
    src_password: str,
    dest_password: str,
    prefix: str = "",
    suffix: str = "",
    overwrite: bool = False,
) -> BulkCopyResult:
    """Decrypt all entries from src vault and re-encrypt them into dest vault.

    Optionally rename keys with a prefix/suffix in the destination.
    """
    src_vault = load_vault(src_path)
    dest_vault = load_vault(dest_path)

    result = BulkCopyResult(source_vault=src_path, dest_vault=dest_path)

    src_entries = {
        k: v for k, v in src_vault.items() if not k.startswith("__")
    }

    for key, ciphertext in src_entries.items():
        dest_key = f"{prefix}{key}{suffix}"

        if dest_key in dest_vault and not overwrite:
            result.skipped.append(dest_key)
            continue

        try:
            plaintext = decrypt_from_b64(ciphertext, src_password)
        except Exception as exc:
            raise BulkCopyError(f"Failed to decrypt '{key}': {exc}") from exc

        dest_vault[dest_key] = encrypt_to_b64(plaintext, dest_password)
        result.copied.append(dest_key)

    save_vault(dest_path, dest_vault)
    return result

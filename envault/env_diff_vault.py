"""Compare two vault files and show a human-readable diff of their decrypted entries."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envault.vault import load_vault
from envault.crypto import decrypt_from_b64


@dataclass
class VaultDiffResult:
    added: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)
    changed: List[str] = field(default_factory=list)
    unchanged: List[str] = field(default_factory=list)

    def has_differences(self) -> bool:
        return bool(self.added or self.removed or self.changed)

    def __str__(self) -> str:
        return format_vault_diff(self)


class VaultDiffError(Exception):
    pass


def _decrypt_entries(vault: dict, password: str) -> Dict[str, str]:
    entries = {}
    for key, val in vault.items():
        if key.startswith("_"):
            continue
        try:
            entries[key] = decrypt_from_b64(val, password)
        except Exception as exc:
            raise VaultDiffError(f"Failed to decrypt key '{key}': {exc}") from exc
    return entries


def diff_vaults(
    vault_a_path: str,
    vault_b_path: str,
    password_a: str,
    password_b: Optional[str] = None,
) -> VaultDiffResult:
    """Diff two vault files. password_b defaults to password_a if not given."""
    if password_b is None:
        password_b = password_a

    vault_a = load_vault(vault_a_path)
    vault_b = load_vault(vault_b_path)

    entries_a = _decrypt_entries(vault_a, password_a)
    entries_b = _decrypt_entries(vault_b, password_b)

    keys_a = set(entries_a)
    keys_b = set(entries_b)

    result = VaultDiffResult()
    result.added = sorted(keys_b - keys_a)
    result.removed = sorted(keys_a - keys_b)

    for key in sorted(keys_a & keys_b):
        if entries_a[key] == entries_b[key]:
            result.unchanged.append(key)
        else:
            result.changed.append(key)

    return result


def format_vault_diff(result: VaultDiffResult) -> str:
    lines = []
    for key in result.added:
        lines.append(f"+ {key}")
    for key in result.removed:
        lines.append(f"- {key}")
    for key in result.changed:
        lines.append(f"~ {key}")
    for key in result.unchanged:
        lines.append(f"  {key}")
    if not lines:
        return "(no entries)"
    return "\n".join(lines)

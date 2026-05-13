"""In-place editing of an existing vault entry's value."""

from dataclasses import dataclass
from typing import Optional

from envault.vault import load_vault, save_vault
from envault.crypto import encrypt_to_b64, decrypt_from_b64


class EditError(Exception):
    pass


@dataclass
class EditResult:
    key: str
    old_value: str
    new_value: str

    def __str__(self) -> str:
        return f"Updated '{self.key}': (old value hidden) -> (new value hidden)"


def edit_entry(
    vault_path: str,
    key: str,
    new_value: str,
    password: str,
    *,
    create: bool = False,
) -> EditResult:
    """Edit the value of *key* in the vault.

    Args:
        vault_path: Path to the vault JSON file.
        key: The entry key to update.
        new_value: Plaintext value to store.
        password: Master password used for encryption/decryption.
        create: If True, create the key when it doesn't exist yet.

    Returns:
        EditResult with old and new plaintext values.

    Raises:
        EditError: If the key is missing and *create* is False, or if the
                   password is wrong when reading the old value.
    """
    vault = load_vault(vault_path)
    entries: dict = vault.get("entries", {})

    if key not in entries:
        if not create:
            raise EditError(
                f"Key '{key}' not found in vault. Use --create to add it."
            )
        old_value = ""
    else:
        old_value = decrypt_from_b64(entries[key], password)

    entries[key] = encrypt_to_b64(new_value, password)
    vault["entries"] = entries
    save_vault(vault_path, vault)

    return EditResult(key=key, old_value=old_value, new_value=new_value)


def format_edit_report(result: EditResult) -> str:
    """Return a human-readable single-line summary of an edit operation."""
    return f"✏  '{result.key}' updated successfully."

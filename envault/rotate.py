"""Key rotation: re-encrypt vault entries with a new password."""

from __future__ import annotations

from typing import Any

from envault.crypto import decrypt_from_b64, encrypt_to_b64
from envault.vault import load_vault, save_vault


def rotate_key(
    vault_path: str,
    old_password: str,
    new_password: str,
) -> list[str]:
    """Re-encrypt every entry in the vault with *new_password*.

    Returns the list of entry names that were rotated.
    Raises ValueError if any entry cannot be decrypted with *old_password*.
    """
    vault: dict[str, Any] = load_vault(vault_path)
    rotated: list[str] = []

    for name, payload in vault.items():
        if not isinstance(payload, dict) or "ciphertext" not in payload:
            continue
        try:
            plaintext: bytes = decrypt_from_b64(payload["ciphertext"], old_password)
        except Exception as exc:
            raise ValueError(
                f"Failed to decrypt entry '{name}' with the old password: {exc}"
            ) from exc

        payload["ciphertext"] = encrypt_to_b64(plaintext, new_password)
        rotated.append(name)

    save_vault(vault_path, vault)
    return rotated


def rotation_summary(rotated: list[str]) -> str:
    """Return a human-readable summary of a completed rotation."""
    if not rotated:
        return "No entries were rotated."
    names = ", ".join(rotated)
    return f"Rotated {len(rotated)} entr{'y' if len(rotated) == 1 else 'ies'}: {names}"

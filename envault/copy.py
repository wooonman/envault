"""Copy (duplicate) a key within a vault or across vaults."""

from __future__ import annotations

from typing import Optional

from envault.vault import load_vault, save_vault
from envault.crypto import decrypt_from_b64, encrypt_to_b64


class CopyError(Exception):
    pass


def copy_key(
    src_vault: str,
    src_key: str,
    dst_vault: str,
    dst_key: str,
    src_password: str,
    dst_password: Optional[str] = None,
    overwrite: bool = False,
) -> dict:
    """Copy src_key from src_vault into dst_vault as dst_key.

    If src_vault == dst_vault and src_password is reused for dst.
    Returns a small report dict.
    """
    if dst_password is None:
        dst_password = src_password

    src_data = load_vault(src_vault)
    if src_key not in src_data:
        raise CopyError(f"Key '{src_key}' not found in source vault.")

    # Decrypt from source
    plaintext = decrypt_from_b64(src_data[src_key], src_password)

    dst_data = load_vault(dst_vault) if src_vault != dst_vault else src_data

    if dst_key in dst_data and not overwrite:
        raise CopyError(
            f"Key '{dst_key}' already exists in destination vault. "
            "Use overwrite=True to replace it."
        )

    existed = dst_key in dst_data
    dst_data[dst_key] = encrypt_to_b64(plaintext, dst_password)

    if src_vault == dst_vault:
        save_vault(src_vault, dst_data)
    else:
        save_vault(dst_vault, dst_data)
        # src unchanged

    return {
        "src_vault": src_vault,
        "src_key": src_key,
        "dst_vault": dst_vault,
        "dst_key": dst_key,
        "overwritten": existed,
    }


def format_copy_report(report: dict) -> str:
    same_vault = report["src_vault"] == report["dst_vault"]
    location = "within the same vault" if same_vault else f"→ {report['dst_vault']}"
    action = "Overwrote" if report["overwritten"] else "Copied"
    return (
        f"{action} '{report['src_key']}' to '{report['dst_key']}' "
        f"({location})."
    )

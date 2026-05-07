"""Import entries into a vault from various sources."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

from envault.vault import load_vault, save_vault, lock


def parse_dotenv(text: str) -> Dict[str, str]:
    """Parse a .env-style string into a key/value dict."""
    result: Dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            result[key] = value
    return result


def parse_json_env(text: str) -> Dict[str, str]:
    """Parse a flat JSON object into a key/value dict."""
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("JSON source must be a top-level object")
    return {str(k): str(v) for k, v in data.items()}


def import_entries(
    vault_path: Path,
    password: str,
    entries: Dict[str, str],
    overwrite: bool = False,
) -> Tuple[List[str], List[str]]:
    """Import *entries* into the vault.

    Returns (imported_keys, skipped_keys).
    """
    vault = load_vault(vault_path)
    imported: List[str] = []
    skipped: List[str] = []

    for key, value in entries.items():
        if key in vault and not overwrite:
            skipped.append(key)
            continue
        # Re-encrypt each value under the vault password
        from envault.vault import lock as _lock
        # Write to a temp env text and lock it
        imported.append(key)

    # Rebuild vault: lock all entries together
    # Collect existing unlocked values first
    from envault.crypto import decrypt_from_b64
    existing: Dict[str, str] = {}
    for k, blob in vault.items():
        try:
            existing[k] = decrypt_from_b64(blob, password)
        except Exception:
            skipped.append(k)

    for key in imported:
        existing[key] = entries[key]

    env_text = "\n".join(f"{k}={v}" for k, v in existing.items())
    tmp = Path(str(vault_path) + ".import_tmp")
    tmp.write_text(env_text)
    try:
        lock(tmp, vault_path, password)
    finally:
        if tmp.exists():
            tmp.unlink()

    return imported, skipped


def format_import_report(imported: List[str], skipped: List[str]) -> str:
    lines = []
    if imported:
        lines.append(f"Imported ({len(imported)}): " + ", ".join(sorted(imported)))
    if skipped:
        lines.append(f"Skipped  ({len(skipped)}): " + ", ".join(sorted(skipped)))
    if not imported and not skipped:
        lines.append("Nothing to import.")
    return "\n".join(lines)

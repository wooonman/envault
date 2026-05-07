"""Backup and restore vault snapshots to/from archive files."""

import json
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def backup_vault(vault_path: str, backup_dir: str) -> str:
    """Copy the vault file to backup_dir with a timestamped name.
    Returns the path to the created backup file."""
    vault_path = Path(vault_path)
    if not vault_path.exists():
        raise FileNotFoundError(f"Vault not found: {vault_path}")

    backup_dir = Path(backup_dir)
    backup_dir.mkdir(parents=True, exist_ok=True)

    stem = vault_path.stem
    suffix = vault_path.suffix or ".json"
    timestamp = _now_iso()
    backup_name = f"{stem}.{timestamp}{suffix}"
    backup_path = backup_dir / backup_name

    shutil.copy2(vault_path, backup_path)
    return str(backup_path)


def list_backups(backup_dir: str, vault_stem: str = "vault") -> list[dict]:
    """List backup files in backup_dir matching vault_stem, sorted newest first."""
    backup_dir = Path(backup_dir)
    if not backup_dir.exists():
        return []

    entries = []
    for p in backup_dir.iterdir():
        if p.stem.startswith(vault_stem + ".") and p.suffix in (".json",):
            stat = p.stat()
            entries.append({
                "path": str(p),
                "name": p.name,
                "size": stat.st_size,
                "mtime": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
            })

    entries.sort(key=lambda e: e["name"], reverse=True)
    return entries


def restore_vault(backup_path: str, vault_path: str, overwrite: bool = False) -> None:
    """Restore a vault from a backup file."""
    backup_path = Path(backup_path)
    vault_path = Path(vault_path)

    if not backup_path.exists():
        raise FileNotFoundError(f"Backup not found: {backup_path}")
    if vault_path.exists() and not overwrite:
        raise FileExistsError(
            f"Vault already exists at {vault_path}. Use overwrite=True to replace it."
        )

    shutil.copy2(backup_path, vault_path)


def format_backup_list(entries: list[dict]) -> str:
    """Format backup list for display."""
    if not entries:
        return "No backups found."
    lines = []
    for e in entries:
        lines.append(f"  {e['name']}  ({e['size']} bytes)  {e['mtime']}")
    return "\n".join(lines)

"""Bulk export: decrypt all vault entries and write to a chosen format."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from envault.crypto import decrypt_from_b64
from envault.export import export_entries
from envault.vault import load_vault


class BulkExportError(Exception):
    pass


@dataclass
class BulkExportResult:
    path: Optional[Path]
    fmt: str
    keys_exported: List[str] = field(default_factory=list)
    content: str = ""

    def __str__(self) -> str:  # noqa: D105
        dest = str(self.path) if self.path else "<stdout>"
        return (
            f"Exported {len(self.keys_exported)} key(s) "
            f"as {self.fmt} to {dest}"
        )


SUPPORTED_FORMATS = ("dotenv", "json", "shell", "csv")


def bulk_export(
    vault_path: Path,
    password: str,
    fmt: str = "dotenv",
    output_path: Optional[Path] = None,
    tags: Optional[List[str]] = None,
) -> BulkExportResult:
    """Decrypt all entries (optionally filtered by tag) and export."""
    if fmt not in SUPPORTED_FORMATS:
        raise BulkExportError(
            f"Unsupported format '{fmt}'. Choose from: {', '.join(SUPPORTED_FORMATS)}"
        )

    vault = load_vault(vault_path)
    entries: Dict[str, str] = {}

    tag_set = set(tags) if tags else None

    for key, meta in vault.get("entries", {}).items():
        if tag_set:
            key_tags = set(vault.get("tags", {}).get(key, []))
            if not tag_set.intersection(key_tags):
                continue
        try:
            value = decrypt_from_b64(meta["value"], password)
        except Exception as exc:
            raise BulkExportError(f"Failed to decrypt '{key}': {exc}") from exc
        entries[key] = value

    content = export_entries(entries, fmt)

    if output_path is not None:
        output_path.write_text(content, encoding="utf-8")

    return BulkExportResult(
        path=output_path,
        fmt=fmt,
        keys_exported=sorted(entries.keys()),
        content=content,
    )

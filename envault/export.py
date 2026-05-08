"""Export decrypted .env entries to various formats."""

from __future__ import annotations

import json
from typing import Dict, List


def to_dotenv(entries: Dict[str, str]) -> str:
    """Render a dict of env vars as a .env formatted string."""
    lines: List[str] = []
    for key, value in sorted(entries.items()):
        # Quote values that contain spaces or special characters
        if any(c in value for c in (" ", "\t", "#", "'", '"')):
            escaped = value.replace('"', '\\"')
            lines.append(f'{key}="{escaped}"')
        else:
            lines.append(f"{key}={value}")
    return "\n".join(lines) + ("\n" if lines else "")


def to_json(entries: Dict[str, str], indent: int = 2) -> str:
    """Render a dict of env vars as a JSON string."""
    return json.dumps(entries, indent=indent, sort_keys=True) + "\n"


def to_shell_export(entries: Dict[str, str]) -> str:
    """Render a dict of env vars as shell export statements."""
    lines: List[str] = []
    for key, value in sorted(entries.items()):
        escaped = value.replace("'", "'\\''")
        lines.append(f"export {key}='{escaped}'")
    return "\n".join(lines) + ("\n" if lines else "")


def to_csv(entries: Dict[str, str]) -> str:
    """Render a dict of env vars as a CSV string with 'key,value' rows."""
    lines: List[str] = ["key,value"]
    for key, value in sorted(entries.items()):
        # Wrap value in quotes if it contains a comma, quote, or newline
        if any(c in value for c in (",", '"', "\n")):
            escaped = value.replace('"', '""')
            lines.append(f'{key},"{escaped}"')
        else:
            lines.append(f"{key},{value}")
    return "\n".join(lines) + "\n"


FORMATS = {
    "dotenv": to_dotenv,
    "json": to_json,
    "shell": to_shell_export,
    "csv": to_csv,
}


def export_entries(entries: Dict[str, str], fmt: str) -> str:
    """Export entries in the given format. Raises ValueError for unknown formats."""
    if fmt not in FORMATS:
        raise ValueError(
            f"Unknown export format '{fmt}'. Choose from: {', '.join(FORMATS)}"
        )
    return FORMATS[fmt](entries)

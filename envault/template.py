"""Template rendering: substitute vault entries into a template string."""

import re
from typing import Optional
from envault.vault import load_vault
from envault.crypto import decrypt_from_b64


class TemplateError(Exception):
    pass


_PLACEHOLDER = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}")


def render_template(template: str, entries: dict[str, str]) -> str:
    """Replace {{KEY}} placeholders with values from entries dict."""
    missing: list[str] = []

    def replacer(m: re.Match) -> str:
        key = m.group(1)
        if key not in entries:
            missing.append(key)
            return m.group(0)
        return entries[key]

    result = _PLACEHOLDER.sub(replacer, template)
    if missing:
        raise TemplateError(f"Missing keys in vault: {', '.join(sorted(missing))}")
    return result


def render_template_file(
    template_path: str,
    vault_path: str,
    password: str,
    output_path: Optional[str] = None,
) -> str:
    """Load a template file, decrypt vault, render, and optionally write output."""
    vault = load_vault(vault_path)
    entries: dict[str, str] = {}
    for key, payload in vault.get("entries", {}).items():
        entries[key] = decrypt_from_b64(payload, password)

    with open(template_path, "r") as fh:
        template = fh.read()

    rendered = render_template(template, entries)

    if output_path:
        with open(output_path, "w") as fh:
            fh.write(rendered)

    return rendered


def list_placeholders(template: str) -> list[str]:
    """Return sorted list of unique placeholder keys found in a template."""
    return sorted(set(_PLACEHOLDER.findall(template)))


def format_render_report(rendered: str, placeholders: list[str]) -> str:
    lines = [f"Rendered {len(placeholders)} placeholder(s):"]
    for p in placeholders:
        lines.append(f"  - {p}")
    lines.append(f"Output length: {len(rendered)} chars")
    return "\n".join(lines)

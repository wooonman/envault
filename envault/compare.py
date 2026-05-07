"""Compare two vault files or two named snapshots, showing a unified diff."""

from __future__ import annotations

from typing import Dict, List, Tuple

from envault.vault import load_vault
from envault.crypto import decrypt_from_b64
from envault.diff import parse_env_lines, diff_envs, format_diff


def _decrypt_vault_entries(vault_path: str, password: str) -> Dict[str, str]:
    """Load and decrypt all entries from a vault file into a plain dict."""
    vault = load_vault(vault_path)
    result: Dict[str, str] = {}
    for key, entry in vault.items():
        if key.startswith("_"):
            continue
        try:
            result[key] = decrypt_from_b64(entry["ciphertext"], password)
        except Exception:
            raise ValueError(f"Failed to decrypt entry '{key}' — wrong password?")
    return result


def compare_vaults(
    path_a: str,
    path_b: str,
    password_a: str,
    password_b: str | None = None,
) -> List[Tuple[str, str, str]]:
    """Compare two vault files and return diff tuples (status, key, detail).

    password_b defaults to password_a when both vaults share the same password.
    Returns a list of (status, key, detail) where status is one of:
      'added', 'removed', 'changed', 'unchanged'.
    """
    if password_b is None:
        password_b = password_a

    entries_a = _decrypt_vault_entries(path_a, password_a)
    entries_b = _decrypt_vault_entries(path_b, password_b)

    # Re-use existing diff logic by serialising to env-style lines
    lines_a = [f"{k}={v}" for k, v in sorted(entries_a.items())]
    lines_b = [f"{k}={v}" for k, v in sorted(entries_b.items())]

    env_a = parse_env_lines(lines_a)
    env_b = parse_env_lines(lines_b)

    return diff_envs(env_a, env_b)


def format_compare_report(
    diffs: List[Tuple[str, str, str]],
    label_a: str = "vault-a",
    label_b: str = "vault-b",
) -> str:
    """Return a human-readable comparison report."""
    header = f"--- {label_a}\n+++ {label_b}\n"
    body = format_diff(diffs)
    if not body.strip():
        return header + "(no differences)\n"
    return header + body

"""Search and filter entries within the vault."""

from __future__ import annotations

import fnmatch
import re
from typing import Dict, List, Optional, Tuple

from envault.vault import load_vault
from envault.crypto import decrypt_from_b64


def search_keys(
    vault_path: str,
    password: str,
    pattern: str,
    use_glob: bool = True,
) -> List[Tuple[str, str]]:
    """Return (key, value) pairs whose keys match *pattern*.

    Args:
        vault_path: Path to the .vault file.
        password:   Decryption password.
        pattern:    Glob pattern (default) or regex string.
        use_glob:   When True treat pattern as a shell glob, else as regex.

    Returns:
        Sorted list of (key, value) tuples.
    """
    vault = load_vault(vault_path)
    results: List[Tuple[str, str]] = []

    for key, ciphertext in vault.items():
        matched = (
            fnmatch.fnmatch(key, pattern)
            if use_glob
            else bool(re.search(pattern, key))
        )
        if matched:
            value = decrypt_from_b64(ciphertext, password)
            results.append((key, value))

    return sorted(results)


def search_values(
    vault_path: str,
    password: str,
    substring: str,
    case_sensitive: bool = False,
) -> List[Tuple[str, str]]:
    """Return (key, value) pairs whose decrypted values contain *substring*."""
    vault = load_vault(vault_path)
    results: List[Tuple[str, str]] = []
    needle = substring if case_sensitive else substring.lower()

    for key, ciphertext in vault.items():
        value = decrypt_from_b64(ciphertext, password)
        haystack = value if case_sensitive else value.lower()
        if needle in haystack:
            results.append((key, value))

    return sorted(results)


def format_search_results(
    results: List[Tuple[str, str]],
    reveal: bool = False,
) -> str:
    """Format search results for display.

    Args:
        results: List of (key, value) tuples.
        reveal:  When False, mask the value with asterisks.
    """
    if not results:
        return "No matches found."

    lines: List[str] = []
    for key, value in results:
        display = value if reveal else "*" * min(len(value), 8)
        lines.append(f"  {key}={display}")
    return "\n".join(lines)

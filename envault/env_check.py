"""Check vault entries against expected keys and flag missing or extra entries."""

from dataclasses import dataclass, field
from typing import Optional
from envault.vault import load_vault


@dataclass
class CheckResult:
    missing: list[str] = field(default_factory=list)
    extra: list[str] = field(default_factory=list)
    matched: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.missing and not self.extra


def check_entries(
    vault_path: str,
    expected_keys: list[str],
    strict: bool = False,
) -> CheckResult:
    """Compare vault keys against a list of expected keys.

    Args:
        vault_path: Path to the vault JSON file.
        expected_keys: Keys that must be present in the vault.
        strict: If True, extra keys in the vault are also flagged.

    Returns:
        CheckResult with missing, extra, and matched key lists.
    """
    vault = load_vault(vault_path)
    vault_keys = {
        k for k in vault.keys() if not k.startswith("__")
    }
    expected = set(expected_keys)

    missing = sorted(expected - vault_keys)
    extra = sorted(vault_keys - expected) if strict else []
    matched = sorted(expected & vault_keys)

    return CheckResult(missing=missing, extra=extra, matched=matched)


def format_check_report(result: CheckResult, strict: bool = False) -> str:
    """Render a human-readable check report."""
    lines: list[str] = []

    if result.matched:
        for k in result.matched:
            lines.append(f"  ok  {k}")

    if result.missing:
        for k in result.missing:
            lines.append(f" MISS {k}")

    if strict and result.extra:
        for k in result.extra:
            lines.append(f" XTRA {k}")

    summary_parts = [f"{len(result.matched)} matched"]
    if result.missing:
        summary_parts.append(f"{len(result.missing)} missing")
    if strict and result.extra:
        summary_parts.append(f"{len(result.extra)} extra")

    lines.append("\n" + ", ".join(summary_parts))
    return "\n".join(lines)

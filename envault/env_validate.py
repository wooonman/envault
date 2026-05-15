"""Validate vault entries against a schema of expected keys and rules."""

from dataclasses import dataclass, field
from typing import Optional
import re

from envault.vault import load_vault
from envault.crypto import decrypt_from_b64


@dataclass
class ValidationIssue:
    key: str
    rule: str
    message: str
    severity: str = "error"  # "error" or "warning"

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.key}: {self.message} (rule: {self.rule})"


@dataclass
class ValidationResult:
    issues: list = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not any(i.severity == "error" for i in self.issues)

    def __str__(self) -> str:
        if not self.issues:
            return "All entries valid."
        lines = [str(i) for i in self.issues]
        return "\n".join(lines)


def _check_rule(key: str, value: str, rule: dict) -> list:
    issues = []
    if "min_length" in rule and len(value) < rule["min_length"]:
        issues.append(ValidationIssue(key, "min_length",
            f"value length {len(value)} < {rule['min_length']}"))
    if "max_length" in rule and len(value) > rule["max_length"]:
        issues.append(ValidationIssue(key, "max_length",
            f"value length {len(value)} > {rule['max_length']}", "warning"))
    if "pattern" in rule and not re.fullmatch(rule["pattern"], value):
        issues.append(ValidationIssue(key, "pattern",
            f"value does not match pattern '{rule['pattern']}'"))
    if "not_empty" in rule and rule["not_empty"] and not value.strip():
        issues.append(ValidationIssue(key, "not_empty", "value must not be empty"))
    return issues


def validate_vault(vault_path: str, password: str, schema: dict) -> ValidationResult:
    """
    schema: {KEY: {"required": bool, "min_length": int, "pattern": str, ...}}
    """
    vault = load_vault(vault_path)
    entries = {k: v for k, v in vault.items() if not k.startswith("__")}
    issues = []

    for key, rule in schema.items():
        if key not in entries:
            if rule.get("required", False):
                issues.append(ValidationIssue(key, "required", "key is missing from vault"))
            continue
        value = decrypt_from_b64(entries[key], password)
        issues.extend(_check_rule(key, value, rule))

    return ValidationResult(issues=issues)


def format_validation_report(result: ValidationResult) -> str:
    if not result.issues:
        return "Validation passed: no issues found."
    errors = [i for i in result.issues if i.severity == "error"]
    warnings = [i for i in result.issues if i.severity == "warning"]
    parts = []
    if errors:
        parts.append(f"{len(errors)} error(s):")
        parts.extend(f"  {i}" for i in errors)
    if warnings:
        parts.append(f"{len(warnings)} warning(s):")
        parts.extend(f"  {i}" for i in warnings)
    return "\n".join(parts)

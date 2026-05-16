"""Bulk annotation: attach key=value metadata annotations to vault entries."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from envault.vault import load_vault, save_vault

_META_KEY = "__annotations__"


class AnnotateError(Exception):
    pass


@dataclass
class AnnotateResult:
    key: str
    annotation_key: str
    old_value: Optional[str]
    new_value: Optional[str]
    cleared: bool = False

    def __str__(self) -> str:
        if self.cleared:
            return f"cleared '{self.annotation_key}' from '{self.key}'"
        return (
            f"annotated '{self.key}': {self.annotation_key}="
            f"{self.new_value!r} (was {self.old_value!r})"
        )


def _get_annotations(vault: dict) -> dict:
    return vault.get(_META_KEY, {})


def _set_annotations(vault: dict, annotations: dict) -> None:
    vault[_META_KEY] = annotations


def get_annotation(vault_path: str, key: str, annotation_key: str) -> Optional[str]:
    vault = load_vault(vault_path)
    return _get_annotations(vault).get(key, {}).get(annotation_key)


def set_annotation(
    vault_path: str, key: str, annotation_key: str, value: str
) -> AnnotateResult:
    vault = load_vault(vault_path)
    if key not in vault and key != _META_KEY:
        raise AnnotateError(f"Key '{key}' not found in vault.")
    annotations = _get_annotations(vault)
    entry = annotations.get(key, {})
    old_value = entry.get(annotation_key)
    entry[annotation_key] = value
    annotations[key] = entry
    _set_annotations(vault, annotations)
    save_vault(vault_path, vault)
    return AnnotateResult(key=key, annotation_key=annotation_key, old_value=old_value, new_value=value)


def clear_annotation(vault_path: str, key: str, annotation_key: str) -> AnnotateResult:
    vault = load_vault(vault_path)
    annotations = _get_annotations(vault)
    entry = annotations.get(key, {})
    old_value = entry.pop(annotation_key, None)
    if entry:
        annotations[key] = entry
    elif key in annotations:
        del annotations[key]
    _set_annotations(vault, annotations)
    save_vault(vault_path, vault)
    return AnnotateResult(key=key, annotation_key=annotation_key, old_value=old_value, new_value=None, cleared=True)


def list_annotations(vault_path: str, key: str) -> dict:
    vault = load_vault(vault_path)
    return dict(_get_annotations(vault).get(key, {}))


def format_annotation_report(results: list[AnnotateResult]) -> str:
    if not results:
        return "No annotations changed."
    return "\n".join(str(r) for r in results)

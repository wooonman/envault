# `batch-delete` — Bulk key removal

Delete multiple keys from a vault in a single command.

## Basic usage

```bash
# Delete two keys at once
envault batch-delete vault.json FOO BAR
```

## Flags

| Flag | Description |
|------|-------------|
| `--skip-missing` | Silently record missing keys instead of raising an error |
| `--force-pinned` | Also delete keys that are currently pinned (default: skip them) |
| `--fail-on-missing` | Exit with code 2 if any requested key was absent (useful in CI) |

## Examples

```bash
# Skip keys that don't exist
envault batch-delete vault.json OLD_KEY ANOTHER_KEY --skip-missing

# Delete pinned keys too
envault batch-delete vault.json LEGACY_KEY --force-pinned

# CI-safe: fail if a key wasn't present
envault batch-delete vault.json MUST_EXIST --skip-missing --fail-on-missing
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | All requested (non-pinned) keys deleted successfully |
| 1 | Error — missing key without `--skip-missing`, or no keys given |
| 2 | One or more keys were absent and `--fail-on-missing` was set |

## Notes

- Pinned keys are **skipped by default** and listed in the output under `Skipped/pinned`.
- Use `--force-pinned` to override this protection.
- The vault is written only once regardless of how many keys are deleted, keeping I/O minimal.

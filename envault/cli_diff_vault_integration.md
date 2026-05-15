# `envault diff-vaults` — CLI Integration Guide

Compare two vault files at the key level and display a human-readable diff.

## Usage

```
envault diff-vaults <vault_a> <vault_b> [--same-password]
```

### Arguments

| Argument | Description |
|---|---|
| `vault_a` | Path to the first (base) vault file |
| `vault_b` | Path to the second (incoming) vault file |
| `--same-password` | Reuse the first vault's password for the second (skips the second prompt) |

## Output Format

Each key is prefixed with a symbol:

| Symbol | Meaning |
|---|---|
| `+` | Key exists only in `vault_b` (added) |
| `-` | Key exists only in `vault_a` (removed) |
| `~` | Key exists in both but values differ (changed) |
| ` ` | Key exists in both with identical values (unchanged) |

## Example

```
$ envault diff-vaults staging.vault.json prod.vault.json --same-password
Password for staging.vault.json:

Vault diff summary: 2 added, 1 removed, 1 changed, 4 unchanged

+ NEW_FEATURE_FLAG
+ SENTRY_DSN
- OLD_LEGACY_KEY
~ DATABASE_URL
  API_KEY
  APP_SECRET
  DEBUG
  LOG_LEVEL
```

## Programmatic API

```python
from envault.env_diff_vault import diff_vaults

result = diff_vaults("staging.vault.json", "prod.vault.json", password_a="s3cr3t")
print(result.added)    # ['NEW_FEATURE_FLAG', 'SENTRY_DSN']
print(result.changed)  # ['DATABASE_URL']
print(result.has_differences())  # True
```

Pass `password_b` explicitly when the two vaults use different passwords:

```python
result = diff_vaults("a.vault.json", "b.vault.json", password_a="pass1", password_b="pass2")
```

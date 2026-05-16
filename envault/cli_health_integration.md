# `envault health` — Vault Health Check

Run a comprehensive health check against a vault file to surface common issues before they become problems.

## Usage

```
envault health [--vault PATH] [--fail-on-warning]
```

### Options

| Flag | Default | Description |
|---|---|---|
| `--vault` | `.env.vault` | Path to the vault file to inspect |
| `--fail-on-warning` | off | Exit with code 1 on warnings too, not just errors |

## Checks Performed

| Category | Severity | Condition |
|---|---|---|
| `vault` | error | Vault file does not exist |
| `encryption` | error | One or more entries appear unencrypted |
| `placeholders` | warning | Keys still contain placeholder values (e.g. `CHANGE_ME`) |
| `ttl` | warning | One or more keys have an expired TTL |
| `vault` | info | Vault contains no entries |

## Exit Codes

- `0` — No errors (warnings/info are OK unless `--fail-on-warning` is set)
- `1` — One or more errors detected (or any issue with `--fail-on-warning`)

## Examples

```bash
# Basic health check
envault health

# Check a specific vault
envault health --vault production.vault

# Treat warnings as failures (useful in CI)
envault health --fail-on-warning
```

## Sample Output

```
Health report for: .env.vault
  [WARNING] ttl: 1 key(s) have expired TTL: DATABASE_URL
  [WARNING] placeholders: 2 key(s) still contain placeholder values

  0 error(s), 2 warning(s)
```

A clean vault looks like:

```
Health report for: .env.vault
  All checks passed. Vault looks healthy.
```

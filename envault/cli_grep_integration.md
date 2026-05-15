# `envault grep` — Grep Vault Values

Search decrypted vault entries by value (or key) pattern, similar to `grep`.

## Usage

```
envault grep <vault> <pattern> [options]
```

## Options

| Flag | Description |
|------|-------------|
| `-k`, `--keys-only` | Match against keys instead of values |
| `-i`, `--ignore-case` | Case-insensitive matching |
| `-v`, `--invert` | Show entries that do **not** match |
| `-E`, `--regex` | Treat pattern as a regular expression |
| `-n`, `--line-numbers` | Show line numbers in output |
| `-c`, `--count` | Print total match count at the end |

## Examples

### Find entries whose value contains "localhost"
```
envault grep vault.json localhost
```

### Case-insensitive search
```
envault grep vault.json LOCALHOST -i
```

### Search keys matching a prefix
```
envault grep vault.json DB_ --keys-only
```

### Regex: find values that are pure integers
```
envault grep vault.json '^\d+$' --regex
```

### Invert: show entries whose value does NOT contain "false"
```
envault grep vault.json false --invert
```

### Show match count
```
envault grep vault.json secret --count
```

## Exit Codes

- `0` — one or more matches found
- `1` — no matches, or an error occurred

## Notes

- Values are decrypted in memory; nothing is written to disk.
- Entries that fail to decrypt (e.g. wrong password) are silently skipped.
- Meta keys (prefixed with `__`) are excluded from search.

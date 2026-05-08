# Template Rendering Feature

Render configuration files from templates by substituting decrypted vault entries.

## Usage

```bash
# Render to stdout
envault template path/to/app.conf.tmpl --vault .envault

# Render to output file
envault template path/to/app.conf.tmpl --vault .envault --output app.conf
```

## Template syntax

Use `{{KEY}}` placeholders (whitespace around the key is allowed):

```
# app.conf.tmpl
database_url = postgres://{{ DB_USER }}:{{ DB_PASS }}@{{ DB_HOST }}/{{ DB_NAME }}
app_secret   = {{SECRET_KEY}}
```

## Wiring into CLI

Add to `envault/cli.py` inside `build_parser`:

```python
from envault.cli_template import add_template_subcommand
add_template_subcommand(subparsers)
```

## Errors

- If a `{{KEY}}` placeholder has no matching entry in the vault, the command
  exits with status 1 and lists all missing keys.
- If the template file or vault file cannot be found, the command exits with
  status 1 and prints the missing path.

"""Generate secure random values for .env keys."""

import secrets
import string

DEFAULT_LENGTH = 32
DEFAULT_ALPHABET = string.ascii_letters + string.digits
SPECIAL_CHARS = "!@#$%^&*()-_=+[]{}"


class GenerateError(Exception):
    pass


def generate_secret(length: int = DEFAULT_LENGTH, use_special: bool = False) -> str:
    """Generate a cryptographically secure random string."""
    if length < 8:
        raise GenerateError("Length must be at least 8 characters.")
    alphabet = DEFAULT_ALPHABET
    if use_special:
        alphabet += SPECIAL_CHARS
    return "".join(secrets.choice(alphabet) for _ in range(length))


def generate_hex(length: int = DEFAULT_LENGTH) -> str:
    """Generate a random hex token of given byte length."""
    if length < 4:
        raise GenerateError("Length must be at least 4.")
    return secrets.token_hex(length)


def generate_urlsafe(length: int = DEFAULT_LENGTH) -> str:
    """Generate a URL-safe base64 random token."""
    if length < 4:
        raise GenerateError("Length must be at least 4.")
    return secrets.token_urlsafe(length)


def generate_for_key(
    vault: dict,
    key: str,
    password: str,
    length: int = DEFAULT_LENGTH,
    mode: str = "secret",
    use_special: bool = False,
    overwrite: bool = False,
) -> str:
    """Generate a value and store it in the vault under key.

    Returns the generated value.
    """
    from envault.vault import lock  # avoid circular import

    if key in vault.get("entries", {}) and not overwrite:
        raise GenerateError(
            f"Key '{key}' already exists. Use overwrite=True to replace it."
        )

    generators = {
        "secret": lambda: generate_secret(length, use_special),
        "hex": lambda: generate_hex(length),
        "urlsafe": lambda: generate_urlsafe(length),
    }
    if mode not in generators:
        raise GenerateError(f"Unknown mode '{mode}'. Choose from: {list(generators)}.")

    value = generators[mode]()
    lock(vault, key, value, password)
    return value


def format_generate_report(key: str, value: str, mode: str) -> str:
    """Return a human-readable summary of the generation."""
    return f"Generated [{mode}] value for '{key}': {value}"

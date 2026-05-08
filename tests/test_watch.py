"""Tests for envault.watch."""

import time
from pathlib import Path

import pytest

from envault.watch import _file_hash, watch_env, format_watch_event


@pytest.fixture()
def tmp_env(tmp_path):
    p = tmp_path / ".env"
    p.write_text("KEY=value\n")
    return p


def test_file_hash_returns_string(tmp_env):
    h = _file_hash(tmp_env)
    assert isinstance(h, str) and len(h) == 32


def test_file_hash_missing_file_returns_none(tmp_path):
    assert _file_hash(tmp_path / "nonexistent.env") is None


def test_file_hash_changes_on_content_change(tmp_env):
    h1 = _file_hash(tmp_env)
    tmp_env.write_text("KEY=changed\n")
    h2 = _file_hash(tmp_env)
    assert h1 != h2


def test_watch_env_calls_on_change(tmp_env):
    called_with = []

    def mutate_after_first_sleep(original_sleep):
        """Wrap time.sleep to mutate the file on the first call."""
        call_count = [0]

        def fake_sleep(secs):
            if call_count[0] == 0:
                tmp_env.write_text("KEY=newvalue\n")
            call_count[0] += 1
            # no real sleep in tests

        return fake_sleep

    import envault.watch as wmod
    original = wmod.time.sleep
    wmod.time.sleep = mutate_after_first_sleep(original)
    try:
        watch_env(
            env_path=tmp_env,
            on_change=lambda p: called_with.append(p),
            interval=0.0,
            max_iterations=2,
        )
    finally:
        wmod.time.sleep = original

    assert len(called_with) == 1
    assert called_with[0] == tmp_env


def test_watch_env_no_change_no_callback(tmp_env):
    called = []

    import envault.watch as wmod
    wmod.time.sleep = lambda s: None
    try:
        watch_env(
            env_path=tmp_env,
            on_change=lambda p: called.append(p),
            interval=0.0,
            max_iterations=3,
        )
    finally:
        import time
        wmod.time.sleep = time.sleep

    assert called == []


def test_format_watch_event_contains_paths(tmp_path):
    env = tmp_path / ".env"
    vault = tmp_path / ".env.vault"
    msg = format_watch_event(env, vault)
    assert str(env) in msg
    assert str(vault) in msg
    assert "locked" in msg

"""Tests for envault.lint."""

import pytest
from envault.lint import lint_lines, format_lint_report, LintIssue


def issues_for(text: str):
    return lint_lines(text.splitlines(keepends=True))


def test_clean_file_produces_no_issues():
    src = "DB_HOST=localhost\nDB_PORT=5432\n"
    assert issues_for(src) == []


def test_missing_equals_is_error():
    issues = issues_for("BADLINE\n")
    assert len(issues) == 1
    assert issues[0].severity == "error"
    assert "missing '='" in issues[0].message


def test_empty_key_is_error():
    issues = issues_for("=somevalue\n")
    assert any(i.severity == "error" and "empty key" in i.message for i in issues)


def test_key_with_whitespace_is_error():
    issues = issues_for("MY KEY=value\n")
    assert any("whitespace" in i.message for i in issues)


def test_lowercase_key_is_warning():
    issues = issues_for("my_var=hello\n")
    assert any(i.severity == "warning" and "UPPER_CASE" in i.message for i in issues)


def test_duplicate_key_is_warning():
    src = "FOO=bar\nFOO=baz\n"
    issues = issues_for(src)
    dup = [i for i in issues if "duplicate" in i.message]
    assert len(dup) == 1
    assert dup[0].line_no == 2


def test_empty_value_is_warning():
    issues = issues_for("SECRET=\n")
    assert any("empty" in i.message for i in issues)


def test_unbalanced_double_quote_is_error():
    issues = issues_for('KEY="unfinished\n')
    assert any('unbalanced "' in i.message for i in issues)


def test_unbalanced_single_quote_is_error():
    issues = issues_for("KEY='unfinished\n")
    assert any("unbalanced '" in i.message for i in issues)


def test_comments_and_blanks_are_ignored():
    src = "# this is a comment\n\nDB=ok\n"
    assert issues_for(src) == []


def test_format_lint_report_no_issues():
    assert format_lint_report([]) == "No issues found."


def test_format_lint_report_with_issues():
    issues = issues_for("bad line\n")
    report = format_lint_report(issues)
    assert "ERROR" in report
    assert "line 1" in report

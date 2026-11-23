from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "ems-validate.yml"
EXPECTED_PATTERN_LINE = (
    "secret_pattern='(gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}"
    "|BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY"
    "|(AZURE_CLIENT_SECRET|AWS_SECRET_ACCESS_KEY)[[:space:]]*=)'"
)


def secret_step() -> str:
    text = WORKFLOW.read_text(encoding="utf-8")
    start = text.index("- name: Secret-pattern sanity check")
    end = text.find("\n  archive-assessment:", start)
    return text[start:end]


def secret_pattern() -> str:
    for line in secret_step().splitlines():
        stripped = line.strip()
        if stripped.startswith("secret_pattern="):
            return stripped[len("secret_pattern='"):-1]
    raise AssertionError("secret_pattern line not found in workflow")


def git_grep(pattern: str, *pathspec: str, cwd: Path = ROOT) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "grep", "-nE", "-e", pattern, "--", *pathspec],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def test_secret_scan_does_not_exclude_markdown():
    step = secret_step()
    assert "--exclude='*.md'" not in step
    assert '--exclude="*.md"' not in step
    assert "--exclude=*.md" not in step
    assert "--include" not in step


def test_secret_pattern_line_unchanged():
    lines = [line.strip() for line in secret_step().splitlines()]
    assert EXPECTED_PATTERN_LINE in lines


def test_no_tracked_markdown_matches_secret_pattern():
    result = git_grep(secret_pattern(), "*.md")
    assert result.returncode == 1, f"secret pattern matches tracked .md files:\n{result.stdout}{result.stderr}"
    assert result.stdout == ""


def test_secret_pattern_detects_positive_control(tmp_path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    sample = tmp_path / "sample.md"
    sample.write_text("example: " + "AWS_SECRET" + "_ACCESS_KEY = value\n", encoding="utf-8")
    subprocess.run(["git", "add", "sample.md"], cwd=tmp_path, check=True)
    result = git_grep(secret_pattern(), "*.md", cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    assert "sample.md" in result.stdout

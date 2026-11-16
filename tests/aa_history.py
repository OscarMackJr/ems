from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

OPT_OUT = 'EMS_ALLOW_NO_HISTORY'
HINT = 'run git fetch --unshallow, or set EMS_ALLOW_NO_HISTORY=1 for an offline local run'


def _git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(['git', *args], cwd=root, capture_output=True)


def history_problem(root: Path, commits=()) -> str | None:
    pinned = f" (pinned commits: {', '.join(commits)})" if commits else ''
    try:
        r = _git(root, 'rev-parse', '--is-shallow-repository')
    except OSError:
        return f'git is unavailable, cannot read the pinned history of {root}{pinned}; fetch full history with git installed'
    if r.returncode != 0:
        return f'{root} is not a git repository, pinned history is unavailable{pinned}; fetch full history'
    if r.stdout.decode('utf-8', 'replace').strip() != 'false':
        return f'{root} is a shallow repository, history is incomplete{pinned}; fetch full history'
    for sha in commits:
        if _git(root, 'cat-file', '-e', f'{sha}^{{commit}}').returncode != 0:
            return f'pinned commit {sha} is not reachable in {root}; fetch full history'
    return None


def require_history(root: Path, commits=()) -> None:
    msg = history_problem(root, commits)
    if not msg:
        return
    if os.environ.get(OPT_OUT) == '1':
        pytest.skip(f'{msg} ({OPT_OUT}=1)')
    pytest.fail(f'{msg}; {HINT}', pytrace=False)


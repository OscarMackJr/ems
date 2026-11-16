from __future__ import annotations

import os
from pathlib import Path

import pytest

from aa_history import require_history

ROOT = Path(__file__).resolve().parents[1]


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    if os.environ.get('EMS_FAIL_ON_SKIP') != '1':
        return
    rep = outcome.get_result()
    if rep.skipped and not hasattr(rep, 'wasxfail'):
        rep.outcome = 'failed'
        rep.longrepr = f'skipped test treated as failure (EMS_FAIL_ON_SKIP=1): {item.nodeid}: {rep.longrepr}'


@pytest.hookimpl(hookwrapper=True)
def pytest_make_collect_report(collector):
    outcome = yield
    if os.environ.get('EMS_FAIL_ON_SKIP') != '1':
        return
    rep = outcome.get_result()
    if rep.skipped:
        rep.outcome = 'failed'
        rep.longrepr = f'skipped test treated as failure (EMS_FAIL_ON_SKIP=1): {collector.nodeid}: {rep.longrepr}'


@pytest.fixture
def require_git_history():
    require_history(ROOT)

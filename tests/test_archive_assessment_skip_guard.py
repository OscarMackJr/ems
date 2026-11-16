import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from aa_history import history_problem, require_history

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / 'tests'
MISSING = 'd' * 40
ENV_KEYS = ('EMS_FAIL_ON_SKIP', 'EMS_ALLOW_NO_HISTORY')

BODIES = {
    'skip': 'import pytest\n\ndef test_x():\n    pytest.skip("deliberate")\n',
    'skipif': 'import pytest\n\n@pytest.mark.skipif(True, reason="deliberate")\ndef test_x():\n    pass\n',
    'missing_history': (
        'from pathlib import Path\nfrom aa_history import require_history\n\n'
        f'def test_x():\n    require_history(Path({str(ROOT)!r}), commits=({MISSING!r},))\n'
    ),
    'passes': 'def test_x():\n    assert True\n',
    'xfail': 'import pytest\n\n@pytest.mark.xfail(reason="deliberate", strict=True)\ndef test_x():\n    assert False\n',
    'module_importorskip': (
        'import pytest\n\npytest.importorskip("ems_no_such_module_xyz")\n\ndef test_x():\n    pass\n'
    ),
    'module_skip': (
        'import pytest\n\npytest.skip("deliberate module skip", allow_module_level=True)\n\ndef test_x():\n    pass\n'
    ),
}
OK_MODULE = 'def test_ok():\n    pass\n'
GUARD_MSG = 'skipped test treated as failure (EMS_FAIL_ON_SKIP=1)'


def run_case(tmp_path, body, extra_module=None, module_name='test_case.py', extra_name='test_ok.py',
             extra_args=(), **env_set):
    work = tmp_path / 'work'
    work.mkdir()
    shutil.copyfile(TESTS / 'conftest.py', work / 'conftest.py')
    shutil.copyfile(TESTS / 'aa_history.py', work / 'aa_history.py')
    (work / module_name).write_text(BODIES[body], encoding='utf-8')
    targets = [str(work / module_name)]
    if extra_module is not None:
        (work / extra_name).write_text(extra_module, encoding='utf-8')
        targets.append(str(work / extra_name))
    if extra_args:
        targets = [str(work)]
    env = {k: v for k, v in os.environ.items() if k not in ENV_KEYS}
    env.update(env_set)
    r = subprocess.run(
        [sys.executable, '-m', 'pytest', *targets, *extra_args, '-p', 'no:cacheprovider', '-q', '-rs',
         '--rootdir', str(work), '--basetemp', str(tmp_path / 'bt')],
        cwd=work, env=env, capture_output=True, text=True,
    )
    return r.returncode, r.stdout + r.stderr


def test_pytest_skip_with_guard_fails(tmp_path):
    code, out = run_case(tmp_path, 'skip', EMS_FAIL_ON_SKIP='1')
    assert code != 0, out
    assert 'skipped test treated as failure (EMS_FAIL_ON_SKIP=1)' in out
    assert '1 failed' in out


def test_pytest_skip_without_guard_passes(tmp_path):
    code, out = run_case(tmp_path, 'skip')
    assert code == 0, out
    assert '1 skipped' in out


def test_skipif_mark_with_guard_fails(tmp_path):
    code, out = run_case(tmp_path, 'skipif', EMS_FAIL_ON_SKIP='1')
    assert code != 0, out
    assert 'skipped test treated as failure' in out


def test_skipif_mark_without_guard_passes(tmp_path):
    code, out = run_case(tmp_path, 'skipif')
    assert code == 0, out
    assert '1 skipped' in out


def test_guard_is_inert_for_passing_test(tmp_path):
    code, out = run_case(tmp_path, 'passes', EMS_FAIL_ON_SKIP='1')
    assert code == 0, out
    assert '1 passed' in out


def test_guard_leaves_xfail_alone(tmp_path):
    code, out = run_case(tmp_path, 'xfail', EMS_FAIL_ON_SKIP='1')
    assert code == 0, out
    assert '1 xfailed' in out


def test_module_importorskip_with_guard_fails(tmp_path):
    code, out = run_case(tmp_path, 'module_importorskip', OK_MODULE, module_name='test_archive_assessment_case.py',
                         extra_name='test_archive_assessment_ok.py', EMS_FAIL_ON_SKIP='1')
    assert code != 0, out
    assert GUARD_MSG in out
    assert '1 error' in out


def test_module_skip_with_guard_fails(tmp_path):
    code, out = run_case(tmp_path, 'module_skip', OK_MODULE, module_name='test_archive_assessment_case.py',
                         extra_name='test_archive_assessment_ok.py', EMS_FAIL_ON_SKIP='1')
    assert code != 0, out
    assert GUARD_MSG in out
    assert '1 error' in out


def test_guard_ignores_skip_in_deselected_non_archive_module(tmp_path):
    code, out = run_case(tmp_path, 'module_skip', OK_MODULE, module_name='test_other_skip.py',
                         extra_name='test_archive_assessment_ok.py', extra_args=('-k', 'archive_assessment'),
                         EMS_FAIL_ON_SKIP='1')
    assert code == 0, out
    assert '1 passed' in out
    assert 'treated as failure' not in out


def test_module_importorskip_without_guard_passes(tmp_path):
    code, out = run_case(tmp_path, 'module_importorskip', OK_MODULE)
    assert code == 0, out
    assert 'skipped' in out
    assert 'treated as failure' not in out


def test_module_skip_without_guard_passes(tmp_path):
    code, out = run_case(tmp_path, 'module_skip', OK_MODULE)
    assert code == 0, out
    assert 'skipped' in out
    assert 'treated as failure' not in out


def test_missing_history_fails_by_default(tmp_path):
    code, out = run_case(tmp_path, 'missing_history')
    assert code != 0, out
    assert MISSING in out
    assert 'fetch full history' in out
    assert 'EMS_ALLOW_NO_HISTORY=1' in out


def test_missing_history_skips_with_opt_out_only(tmp_path):
    code, out = run_case(tmp_path, 'missing_history', EMS_ALLOW_NO_HISTORY='1')
    assert code == 0, out
    assert '1 skipped' in out
    assert MISSING in out


def test_missing_history_with_opt_out_and_guard_fails(tmp_path):
    code, out = run_case(tmp_path, 'missing_history', EMS_ALLOW_NO_HISTORY='1', EMS_FAIL_ON_SKIP='1')
    assert code != 0, out
    assert 'skipped test treated as failure' in out
    assert MISSING in out


def test_history_problem_full_clone_is_none():
    assert history_problem(ROOT) is None


def test_history_problem_names_missing_commit():
    msg = history_problem(ROOT, commits=(MISSING,))
    assert MISSING in msg and 'fetch full history' in msg and str(ROOT) in msg


def test_history_problem_not_a_repository(tmp_path, monkeypatch):
    empty = tmp_path / 'empty_git_dir'
    empty.mkdir()
    monkeypatch.setenv('GIT_DIR', str(empty))
    msg = history_problem(ROOT)
    assert 'not a git repository' in msg and 'fetch full history' in msg


def test_history_problem_git_unavailable(monkeypatch):
    import aa_history

    def boom(*a, **k): raise FileNotFoundError('git')
    monkeypatch.setattr(aa_history.subprocess, 'run', boom)
    assert 'git is unavailable' in history_problem(ROOT)


@pytest.mark.parametrize('stdout', [b'', b'maybe', b'true'])
def test_history_problem_unrecognised_shallow_output_is_problem(monkeypatch, stdout):
    import aa_history

    def fake(*a, **k): return subprocess.CompletedProcess(args=[], returncode=0, stdout=stdout, stderr=b'')
    monkeypatch.setattr(aa_history.subprocess, 'run', fake)
    msg = history_problem(ROOT)
    assert 'shallow' in msg and 'fetch full history' in msg
    out = stdout.decode('utf-8').strip()
    if out == 'true':
        assert 'is a shallow repository' in msg
    else:
        assert repr(out) in msg
        assert 'cannot tell whether' in msg
        assert 'is a shallow repository' not in msg


def test_history_problem_false_output_passes_shallow_check(monkeypatch):
    import aa_history

    def fake(*a, **k): return subprocess.CompletedProcess(args=[], returncode=0, stdout=b'false\n', stderr=b'')
    monkeypatch.setattr(aa_history.subprocess, 'run', fake)
    assert history_problem(ROOT, commits=()) is None


def test_require_history_fail_and_opt_out(monkeypatch):
    for k in ENV_KEYS:
        monkeypatch.delenv(k, raising=False)
    require_history(ROOT)
    with pytest.raises(pytest.fail.Exception, match=f'{MISSING}.*fetch full history.*EMS_ALLOW_NO_HISTORY=1'):
        require_history(ROOT, commits=(MISSING,))
    monkeypatch.setenv('EMS_ALLOW_NO_HISTORY', '1')
    with pytest.raises(pytest.skip.Exception, match=MISSING):
        require_history(ROOT, commits=(MISSING,))
    monkeypatch.setenv('EMS_ALLOW_NO_HISTORY', '0')
    with pytest.raises(pytest.fail.Exception):
        require_history(ROOT, commits=(MISSING,))

import copy
import hashlib
import importlib.util
import shutil
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[1] / 'scripts' / 'publish_archive_assessment_applicability_authority_v2.py'
SPEC = importlib.util.spec_from_file_location('aa3_authority_v2_lineage', SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
AuthorityError = MODULE.AuthorityError
REAL_ROOT = MODULE.ROOT

AA1_MANIFEST_RAW_SHA256 = 'f0da8e2e45c306ccc42ae96f25a19922668f3eedecdb26006f13514e24ad9b4b'
AA1_GITATTRIBUTES_LINE = 'generated/archive-assessment/ems-aa1/ems_aa1_analysis_artifact_manifest.json -text'

CRLF_DATA = b'{"k": 1}\r\n{"j": 2}\r\n'


def git(*args, cwd=REAL_ROOT):
    return subprocess.run(['git', *args], cwd=cwd, capture_output=True)


def git_ready():
    if not shutil.which('git'):
        return 'git unavailable'
    shallow = git('rev-parse', '--is-shallow-repository')
    if shallow.returncode != 0 or shallow.stdout.strip() != b'false':
        return 'shallow or unreadable repository'
    for commit in (MODULE.V1_BASELINE_COMMIT, MODULE.SUPERSEDED_V2_0_1['commit']):
        if git('cat-file', '-e', f'{commit}^{{commit}}').returncode != 0:
            return f'commit {commit[:7]} not available'
    return None


def sha(norm, data):
    return hashlib.sha256(MODULE.NORMALISERS[norm](data)).hexdigest()


def put(root, rel, data):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)


@pytest.fixture
def fx(tmp_path, monkeypatch):
    if not shutil.which('git'):
        pytest.skip('git unavailable')
    monkeypatch.setattr(MODULE, 'ROOT', tmp_path)
    sup = MODULE.SUPERSEDED_V2_0_1
    rels = [MODULE.AA1_MANIFEST_REL, MODULE.AA2_CLOSURE_REL, MODULE.AA2_APPROVAL_REL, MODULE.CATALOG_REL,
            MODULE.GOVERNANCE_DECISIONS_REL, MODULE.V1_BASELINE_REL, sup['relative_path']]
    for i, rel in enumerate(rels):
        put(tmp_path, rel, CRLF_DATA + str(i).encode() + b'\r\n')
    (tmp_path / '.gitattributes').write_bytes(b'* -text\n')
    base = ['-c', 'core.autocrlf=false', '-c', 'user.name=t', '-c', 'user.email=t@t']
    assert git('init', cwd=tmp_path).returncode == 0
    assert git(*base, 'add', '--', '.', cwd=tmp_path).returncode == 0
    assert git(*base, 'commit', '-m', 'fixture', cwd=tmp_path).returncode == 0
    commit = git('rev-parse', 'HEAD', cwd=tmp_path).stdout.decode().strip()
    rd = lambda rel: (tmp_path / rel).read_bytes()
    lin = {
        'aa1_manifest': MODULE.digest_entry(MODULE.AA1_MANIFEST_REL, sha('RAW_BYTES', rd(MODULE.AA1_MANIFEST_REL)), 'RAW_BYTES'),
        'aa2_closure': MODULE.digest_entry(MODULE.AA2_CLOSURE_REL, sha('RAW_BYTES', rd(MODULE.AA2_CLOSURE_REL)), 'RAW_BYTES'),
        'aa2_approval': MODULE.digest_entry(MODULE.AA2_APPROVAL_REL, sha('RAW_BYTES', rd(MODULE.AA2_APPROVAL_REL)), 'RAW_BYTES'),
        'catalog_reference': MODULE.digest_entry(MODULE.CATALOG_REL, sha('CRLF_TO_LF', rd(MODULE.CATALOG_REL)), 'CRLF_TO_LF', commit),
        'governance_decisions': MODULE.digest_entry(MODULE.GOVERNANCE_DECISIONS_REL, sha('CRLF_TO_LF', rd(MODULE.GOVERNANCE_DECISIONS_REL)), 'CRLF_TO_LF'),
        'v1_baseline': MODULE.digest_entry(MODULE.V1_BASELINE_REL, sha('CRLF_TO_LF', rd(MODULE.V1_BASELINE_REL)), 'CRLF_TO_LF', commit),
        'supersedes': {
            'commit': commit, 'relative_path': sup['relative_path'], 'sha256': sha('CRLF_TO_LF', rd(sup['relative_path'])), 'normalisation': 'CRLF_TO_LF',
            'governance_decisions_relative_path': MODULE.GOVERNANCE_DECISIONS_REL,
            'governance_decisions_sha256': sha('CRLF_TO_LF', rd(MODULE.GOVERNANCE_DECISIONS_REL)),
            'governance_decisions_normalisation': 'CRLF_TO_LF',
        },
    }
    return tmp_path, lin


def test_fixture_lineage_passes(fx):
    _, lin = fx
    assert MODULE.validate_lineage(lin) is None


def flip_sha(value):
    return ('0' if value[0] != '0' else '1') + value[1:]


@pytest.mark.parametrize('label,norm', [('aa1_manifest', 'RAW_BYTES')])
@pytest.mark.parametrize('kind', ['changed_byte', 'changed_declared_normalisation', 'changed_recorded_digest'])
def test_d12_tamper_working_tree_entry_raises(fx, label, norm, kind):
    root, lin = fx
    entry = lin[label]
    assert entry['normalisation'] == norm
    if kind == 'changed_byte':
        p = root / entry['relative_path']
        p.write_bytes(p.read_bytes().replace(b'1', b'2', 1))
    elif kind == 'changed_declared_normalisation':
        entry['normalisation'] = 'CRLF_TO_LF' if norm == 'RAW_BYTES' else 'RAW_BYTES'
    else:
        entry['sha256'] = flip_sha(entry['sha256'])
    with pytest.raises(AuthorityError):
        MODULE.validate_lineage(lin)


def test_d12_raw_and_lf_digests_differ_on_crlf_fixture():
    assert sha('RAW_BYTES', CRLF_DATA) != sha('CRLF_TO_LF', CRLF_DATA)


@pytest.mark.parametrize('label', ['v1_baseline', 'supersedes', 'catalog_reference'])
def test_d12_commit_pinned_changed_digest_raises(fx, label):
    _, lin = fx
    lin[label]['sha256'] = flip_sha(lin[label]['sha256'])
    with pytest.raises(AuthorityError):
        MODULE.validate_lineage(lin)


def test_d12_commit_pinned_supersedes_governance_digest_raises(fx):
    _, lin = fx
    lin['supersedes']['governance_decisions_sha256'] = flip_sha(lin['supersedes']['governance_decisions_sha256'])
    with pytest.raises(AuthorityError):
        MODULE.validate_lineage(lin)


@pytest.mark.parametrize('label', ['v1_baseline', 'supersedes', 'catalog_reference'])
def test_d12_commit_pinned_declared_normalisation_flip_raises(fx, label):
    _, lin = fx
    lin[label]['normalisation'] = 'RAW_BYTES'
    with pytest.raises(AuthorityError):
        MODULE.validate_lineage(lin)


def test_d11_commit_pinned_uses_blob_not_working_file(fx):
    root, lin = fx
    (root / MODULE.V1_BASELINE_REL).write_bytes(b'changed in working tree\r\n')
    (root / lin['supersedes']['relative_path']).write_bytes(b'changed in working tree\r\n')
    (root / MODULE.CATALOG_REL).write_bytes(b'changed in working tree\r\n')
    assert MODULE.validate_lineage(lin) is None


@pytest.mark.parametrize('label', ['v1_baseline', 'supersedes', 'catalog_reference'])
def test_d10_nonexistent_commit_raises(fx, label):
    _, lin = fx
    lin[label]['commit'] = '0' * 40
    with pytest.raises(AuthorityError):
        MODULE.validate_lineage(lin)


@pytest.mark.parametrize('label', ['v1_baseline', 'supersedes', 'catalog_reference'])
@pytest.mark.parametrize('missing',['absent', 'empty', 'none'])
def test_wr01_commit_pinned_entry_without_commit_raises(fx, label, missing):
    _, lin = fx
    if missing == 'absent':
        del lin[label]['commit']
    else:
        lin[label]['commit'] = '' if missing == 'empty' else None
    with pytest.raises(AuthorityError):
        MODULE.validate_lineage(lin)


@pytest.mark.parametrize('label', ['v1_baseline', 'supersedes', 'catalog_reference'])
@pytest.mark.parametrize('bad', [5, ['a' * 40], {'k': 'v'}, True])
def test_wr02_non_string_commit_raises_authority_error(fx, label, bad):
    _, lin = fx
    lin[label]['commit'] = bad
    with pytest.raises(AuthorityError):
        MODULE.validate_lineage(lin)


@pytest.mark.parametrize('bad', [['CRLF_TO_LF'], {'k': 'v'}, 5])
def test_wr02_unhashable_or_non_string_normalisation_raises_authority_error(fx, bad):
    _, lin = fx
    lin['catalog_reference']['normalisation'] = bad
    with pytest.raises(AuthorityError):
        MODULE.validate_lineage(lin)


@pytest.mark.parametrize('bad', [5, ['a' * 40], None])
def test_wr02_git_show_non_string_commit_raises_authority_error(bad):
    with pytest.raises(AuthorityError):
        MODULE.git_show(bad, 'registry/x.json')


@pytest.mark.parametrize('label', ['v1_baseline', 'supersedes', 'catalog_reference'])
def test_d10_short_commit_raises(fx, label):
    _, lin = fx
    lin[label]['commit'] = 'abcdef0'
    with pytest.raises(AuthorityError):
        MODULE.validate_lineage(lin)


def test_d10_option_like_commit_rejected_before_subprocess(monkeypatch):
    def boom(*a, **k):
        raise AssertionError('subprocess must not be called')
    monkeypatch.setattr(MODULE.subprocess, 'run', boom)
    with pytest.raises(AuthorityError):
        MODULE.git_show('--output=x' + '0' * 30, 'registry/x.json')


def test_d11_missing_path_in_commit_raises(fx):
    _, lin = fx
    lin['v1_baseline']['relative_path'] = 'registry/does_not_exist.json'
    with pytest.raises(AuthorityError):
        MODULE.validate_lineage(lin)


def test_d11_missing_working_file_raises(fx):
    root, lin = fx
    (root / lin['aa2_closure']['relative_path']).unlink()
    with pytest.raises(AuthorityError):
        MODULE.validate_lineage(lin)


@pytest.mark.parametrize('bad', ['LF', '', None, 'raw_bytes'])
def test_unknown_normalisation_raises(fx, bad):
    _, lin = fx
    lin['catalog_reference']['normalisation'] = bad
    with pytest.raises(AuthorityError):
        MODULE.validate_lineage(lin)


@pytest.mark.parametrize('bad', ['/etc/passwd', 'C:\\Windows\\x', '../outside.txt', 'a/../../b', '', 'C:foo', 'c:foo/bar.json', '\\rooted\\x.json', 5])
def test_bad_relative_path_raises(fx, bad):
    _, lin = fx
    lin['aa1_manifest']['relative_path'] = bad
    with pytest.raises(AuthorityError):
        MODULE.validate_lineage(lin)


def test_missing_lineage_label_raises(fx):
    _, lin = fx
    del lin['aa2_approval']
    with pytest.raises(AuthorityError):
        MODULE.validate_lineage(lin)


@pytest.mark.parametrize('bad', ['C:foo', '\\rooted\\x.json', '/abs/x.json', 'a/../b'])
def test_wr03_git_show_rejects_bad_relative_path_before_subprocess(monkeypatch, bad):
    def boom(*a, **k):
        raise AssertionError('subprocess must not be called')
    monkeypatch.setattr(MODULE.subprocess, 'run', boom)
    with pytest.raises(AuthorityError):
        MODULE.git_show('a' * 40, bad)


def test_git_show_git_unavailable_raises(monkeypatch):
    def nogit(*a, **k):
        raise FileNotFoundError('git')
    monkeypatch.setattr(MODULE.subprocess, 'run', nogit)
    with pytest.raises(AuthorityError):
        MODULE.git_show('a' * 40, 'registry/x.json')


# Real-repo tests (read-only)

def real_lineage():
    return MODULE.build_published_authority()['source_lineage']


def test_real_lineage_validates_against_repo():
    reason = git_ready()
    if reason:
        pytest.skip(reason)
    assert MODULE.validate_lineage(real_lineage()) is None


def test_real_lineage_declares_expected_normalisations():
    lin = real_lineage()
    for label in ('aa1_manifest', 'aa2_closure', 'aa2_approval'):
        assert lin[label]['normalisation'] == 'RAW_BYTES'
    for label in ('catalog_reference', 'governance_decisions', 'v1_baseline'):
        assert lin[label]['normalisation'] == 'CRLF_TO_LF'
    assert lin['supersedes']['normalisation'] == 'CRLF_TO_LF'
    assert lin['supersedes']['governance_decisions_normalisation'] == 'CRLF_TO_LF'
    assert 'digest_normalisation' not in lin


def test_real_aa1_manifest_tampered_digest_raises():
    lin = copy.deepcopy(real_lineage())
    lin['aa1_manifest']['sha256'] = flip_sha(lin['aa1_manifest']['sha256'])
    with pytest.raises(AuthorityError):
        MODULE.validate_lineage(lin)


# LIN-03

def test_aa1_manifest_is_tracked():
    if not shutil.which('git'):
        pytest.skip('git unavailable')
    r = git('ls-files', '--error-unmatch', '--', MODULE.AA1_MANIFEST_REL)
    assert r.returncode == 0, r.stderr.decode('utf-8', 'replace')


def test_aa1_manifest_blob_raw_sha256_is_pinned_literal():
    if not shutil.which('git'):
        pytest.skip('git unavailable')
    r = git('show', f'HEAD:{MODULE.AA1_MANIFEST_REL}')
    assert r.returncode == 0, r.stderr.decode('utf-8', 'replace')
    assert hashlib.sha256(r.stdout).hexdigest() == AA1_MANIFEST_RAW_SHA256


def test_aa1_gitattributes_carries_text_unset_rule():
    lines = (REAL_ROOT / '.gitattributes').read_bytes().decode('utf-8').splitlines()
    assert AA1_GITATTRIBUTES_LINE in [x.strip() for x in lines]


def test_aa1_check_attr_reports_text_unset():
    if not shutil.which('git'):
        pytest.skip('git unavailable')
    r = git('check-attr', 'text', '--', MODULE.AA1_MANIFEST_REL)
    assert r.returncode == 0
    assert r.stdout.decode('utf-8').strip().endswith('text: unset')


# GATE-03: catalog reads are pinned to CATALOG_COMMIT

def catalog_repo(tmp_path, monkeypatch, content):
    monkeypatch.setattr(MODULE, 'ROOT', tmp_path)
    put(tmp_path, MODULE.CATALOG_REL, content)
    (tmp_path / '.gitattributes').write_bytes(b'* -text\n')
    base = ['-c', 'core.autocrlf=false', '-c', 'user.name=t', '-c', 'user.email=t@t']
    assert git('init', cwd=tmp_path).returncode == 0
    assert git(*base, 'add', '--', '.', cwd=tmp_path).returncode == 0
    assert git(*base, 'commit', '-m', 'fixture', cwd=tmp_path).returncode == 0
    commit = git('rev-parse', 'HEAD', cwd=tmp_path).stdout.decode().strip()
    monkeypatch.setattr(MODULE, 'CATALOG_COMMIT', commit)
    return commit


def test_d10_live_catalog_edit_does_not_change_catalog_reads(tmp_path, monkeypatch):
    if not shutil.which('git'):
        pytest.skip('git unavailable')
    reason = git_ready()
    if reason:
        pytest.skip(reason)
    pinned = git('show', f'{MODULE.CATALOG_COMMIT}:{MODULE.CATALOG_REL}').stdout
    catalog_repo(tmp_path, monkeypatch, pinned)
    before_controls = MODULE.catalog_controls()
    before_bytes = MODULE.catalog_bytes()
    assert len(before_controls) == 80
    (tmp_path / MODULE.CATALOG_REL).write_bytes(b'controls: []\n')
    assert MODULE.catalog_bytes() == before_bytes
    assert MODULE.catalog_controls() == before_controls
    assert hashlib.sha256(MODULE.lf_bytes(MODULE.catalog_bytes())).hexdigest() == hashlib.sha256(MODULE.lf_bytes(pinned)).hexdigest()


def test_d10_live_catalog_edit_or_delete_does_not_change_build_or_validation(tmp_path, monkeypatch):
    if not shutil.which('git'):
        pytest.skip('git unavailable')
    reason = git_ready()
    if reason:
        pytest.skip(reason)
    pinned = git('show', f'{MODULE.CATALOG_COMMIT}:{MODULE.CATALOG_REL}').stdout
    sup, real_git_show = MODULE.SUPERSEDED_V2_0_1, MODULE.git_show
    prev = git('show', f"{sup['commit']}:{sup['relative_path']}")
    if prev.returncode != 0:
        pytest.skip('2.0.1 authority blob is not reachable in this clone')
    # the fixture repo has no 2.0.1 history; validate_publication's D-08 comparison reads it from the real repo
    monkeypatch.setattr(MODULE, 'git_show', lambda commit, path: prev.stdout if (commit, path) == (sup['commit'], sup['relative_path']) else real_git_show(commit, path))
    catalog_repo(tmp_path, monkeypatch, pinned)
    before_build = MODULE.jtext(MODULE.build_authority())
    before_published = MODULE.build_published_authority()
    MODULE.validate_publication(before_published)
    live = tmp_path / MODULE.CATALOG_REL
    for change in (lambda: live.write_bytes(b'controls: []\n'), live.unlink):
        change()
        assert MODULE.jtext(MODULE.build_authority()) == before_build
        after = MODULE.build_published_authority()
        assert after == before_published
        MODULE.validate_publication(after)
    assert not live.exists()


def test_d09_catalog_read_without_history_raises(tmp_path, monkeypatch):
    if not shutil.which('git'):
        pytest.skip('git unavailable')
    monkeypatch.setattr(MODULE, 'ROOT', tmp_path)
    assert git('init', cwd=tmp_path).returncode == 0
    with pytest.raises(AuthorityError):
        MODULE.catalog_controls()
    with pytest.raises(AuthorityError):
        MODULE.catalog_bytes()


def test_d09_catalog_read_git_failure_raises_not_skips(monkeypatch):
    def failing(*a, **k):
        return subprocess.CompletedProcess(a, 128, b'', b'fatal: shallow file has changed')
    monkeypatch.setattr(MODULE.subprocess, 'run', failing)
    with pytest.raises(AuthorityError):
        MODULE.catalog_controls()
    with pytest.raises(AuthorityError):
        MODULE.build_authority()


def test_d09_catalog_read_git_unavailable_raises(monkeypatch):
    def nogit(*a, **k):
        raise FileNotFoundError('git')
    monkeypatch.setattr(MODULE.subprocess, 'run', nogit)
    with pytest.raises(AuthorityError):
        MODULE.catalog_controls()

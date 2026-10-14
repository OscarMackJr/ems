import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

import jsonschema
import pytest
import yaml

ROOT = Path(__file__).parents[1]

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod

MODULE = load_module('aa_rule_proposals_validator', ROOT / 'scripts' / 'validate_archive_assessment_rule_proposals.py')
EARLIER = load_module('aa_rule_proposals_tests', ROOT / 'tests' / 'test_archive_assessment_rule_proposals.py')
PROPOSALS = 'registry/archive_assessment_not_applicable_rule_proposals.json'
BRIEF = 'docs/ARCHIVE_ASSESSMENT_RULE_DRAFTER_BRIEF.md'
CATALOG = 'registry/control_catalog.yaml'

def git(*args, text=True):
    r = subprocess.run(['git', *args], cwd=ROOT, capture_output=True)
    return r if not text else subprocess.CompletedProcess(r.args, r.returncode, r.stdout.decode('utf-8').strip(), r.stderr.decode('utf-8').strip())

def sha(b): return hashlib.sha256(b).hexdigest()

def record(): return json.loads(MODULE.RECORD.read_text(encoding='utf-8'))

def git_ready():
    try: r = git('rev-parse', '--is-shallow-repository')
    except OSError: return 'git is unavailable'
    if r.returncode != 0: return 'not a git repository'
    if r.stdout == 'true': return 'shallow repository, history is incomplete'
    return None

def needs_git(fn):
    reason = git_ready()
    return pytest.mark.skipif(reason is not None, reason=reason or '')(fn)

def test_proposals_brief_and_record_exist():
    assert MODULE.PROPOSALS.exists()
    assert MODULE.BRIEF.exists()
    assert MODULE.RECORD.exists()

def test_record_validates():
    MODULE.validate_record(record())
    jsonschema.Draft202012Validator(json.loads(MODULE.RECORD_SCHEMA.read_text(encoding='utf-8'))).validate(record())

def test_record_statement_and_isolation():
    r = record()
    assert r['statement'] == MODULE.RECORD_STATEMENT
    assert r['drafter']['holds_ems_authority'] is False
    assert 'by instruction and brief design' in r['isolation_method']

def test_term_scan_covers_all_three_files():
    for p in (MODULE.PROPOSALS, MODULE.BRIEF, MODULE.RECORD):
        assert EARLIER.scan(p.read_text(encoding='utf-8')) == []
        assert EARLIER.scan(p.name) == []

@needs_git
def test_recorded_commit_is_ancestor():
    assert git('merge-base', '--is-ancestor', record()['drafting_commit'], 'HEAD').returncode == 0

@needs_git
def test_drafting_commit_changed_exactly_one_path():
    r = git('diff-tree', '--no-commit-id', '--name-only', '-r', record()['drafting_commit'])
    assert r.stdout.splitlines() == [PROPOSALS]

@needs_git
def test_brief_commit_precedes_drafting_commit():
    rec = record()
    assert rec['brief_commit'] != rec['drafting_commit']
    assert git('merge-base', '--is-ancestor', rec['brief_commit'], rec['drafting_commit']).returncode == 0

@needs_git
def test_blob_hashes_match_record():
    rec = record()
    dc = rec['drafting_commit']
    assert sha(git('show', f'{dc}:{PROPOSALS}', text=False).stdout) == rec['proposals_sha256']
    assert sha(git('show', f"{rec['brief_commit']}:{BRIEF}", text=False).stdout) == rec['brief_sha256']
    assert sha(git('show', f'{dc}:{CATALOG}', text=False).stdout) == rec['catalog_sha256']
    blob = git('rev-parse', f'{dc}:{CATALOG}').stdout
    assert blob == rec['catalog_git_blob_id']
    proposals = json.loads(git('show', f'{dc}:{PROPOSALS}', text=False).stdout.decode('utf-8'))
    assert proposals['catalog_source']['git_blob_id'] == blob

@needs_git
def test_proposals_frozen_since_drafting_commit():
    rec = record()
    assert git('rev-parse', f'HEAD:{PROPOSALS}').stdout == git('rev-parse', f"{rec['drafting_commit']}:{PROPOSALS}").stdout
    assert git('rev-parse', f'HEAD:{BRIEF}').stdout == git('rev-parse', f"{rec['brief_commit']}:{BRIEF}").stdout

@needs_git
def test_catalog_inputs_match_catalog_at_drafting_commit():
    dc = record()['drafting_commit']
    catalog = yaml.safe_load(git('show', f'{dc}:{CATALOG}', text=False).stdout.decode('utf-8'))
    entries = catalog['controls'] if isinstance(catalog, dict) and 'controls' in catalog else catalog
    by_id = {e.get('control_id') or e.get('id'): e for e in entries}
    proposals = json.loads(git('show', f'{dc}:{PROPOSALS}', text=False).stdout.decode('utf-8'))
    assert len(proposals['proposals']) == len(MODULE.CONTROL_IDS)
    for p in proposals['proposals']:
        entry = by_id[p['control_id']]
        for k, v in p['catalog_inputs'].items(): assert entry[k] == v

@needs_git
def test_no_decision_or_v2_authority_at_drafting_commit():
    dc = record()['drafting_commit']
    names = git('ls-tree', '-r', '--name-only', dc).stdout.splitlines()
    assert 'registry/archive_assessment_applicability_authority_v2.json' not in names
    r = git('grep', '-l', 'AA4-GOV', dc, '--', 'registry')
    assert r.returncode == 1 and r.stdout == ''

@needs_git
def test_drafting_commit_is_sole_commit_of_proposals_file():
    assert git('log', '--format=%H', '--', PROPOSALS).stdout.splitlines() == [record()['drafting_commit']]

@needs_git
def test_published_authority_files_unchanged_at_drafting_commit():
    dc = record()['drafting_commit']
    added = git('log', '--diff-filter=A', '--format=%H', '--', 'scripts/validate_archive_assessment_rule_proposals.py').stdout.splitlines()
    baseline = f'{added[-1]}^'
    listed = git('ls-tree', '-r', '--name-only', baseline, '--', 'registry', 'schemas').stdout.splitlines()
    paths = [p for p in listed if Path(p).name.startswith('archive_assessment_applicability_authority') and '_v2' not in Path(p).name]
    assert 'registry/archive_assessment_applicability_authority.json' in paths
    assert len(paths) >= 2
    for p in paths: assert git('rev-parse', f'{dc}:{p}').stdout == git('rev-parse', f'{baseline}:{p}').stdout

FROZEN_COMMIT = 'dc3b41c'

def drifted_catalog(tmp_path):
    data = yaml.safe_load(MODULE.CATALOG.read_text(encoding='utf-8'))
    for c in data['controls']:
        if c['control_id'] == MODULE.CONTROL_IDS[0]: c['scope'] = 'ORGANIZATION' if c['scope'] != 'ORGANIZATION' else 'EMS'
    out = tmp_path / 'control_catalog.yaml'
    out.write_text(yaml.safe_dump(data), encoding='utf-8')
    return out

def real_proposals(): return json.loads(MODULE.PROPOSALS.read_text(encoding='utf-8'))

@needs_git
def test_frozen_validation_survives_catalog_drift_via_git(monkeypatch, tmp_path):
    monkeypatch.setattr(MODULE, 'CATALOG', drifted_catalog(tmp_path))
    MODULE.validate_proposals(real_proposals())

def test_frozen_validation_survives_drift_without_git_and_says_so(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(MODULE, 'CATALOG', drifted_catalog(tmp_path))
    def no_git(*a): raise MODULE.AuthorityError('git unavailable')
    monkeypatch.setattr(MODULE, 'git', no_git)
    MODULE.validate_proposals(real_proposals())
    err = capsys.readouterr().err
    assert err.startswith('NOTICE:') and FROZEN_COMMIT in err and len(err.strip().splitlines()) == 1

def test_default_path_runs_no_git_and_header_matches(monkeypatch):
    def boom(*a): raise AssertionError('git must not be called')
    monkeypatch.setattr(MODULE, 'git', boom)
    p = real_proposals()
    exp = MODULE.expected_header()
    for k in MODULE.HEADER_KEYS: assert p[k] == exp[k]
    MODULE.validate_proposals(p)

def test_catalog_blob_id_matches_record():
    data = MODULE.V2.lf_bytes(MODULE.CATALOG.read_bytes())
    assert MODULE.catalog_blob_id(data) == record()['catalog_git_blob_id']

def test_frame_differing_from_frozen_frame_is_rejected():
    p = real_proposals()
    p['drafting_frame']['unknown_is_not_not_applicable'] = False
    with pytest.raises(MODULE.AuthorityError): MODULE.validate_proposals(p)

def test_frozen_frame_is_pinned_to_constant():
    f = MODULE.frozen_frame()
    assert MODULE.V2.sha_text(MODULE.V2.jtext(f)) == MODULE.FROZEN_FRAME_SHA256

@needs_git
def test_frozen_frame_constant_matches_drafting_commit():
    blob = git('show', f'{FROZEN_COMMIT}:{PROPOSALS}', text=False).stdout
    frame = json.loads(blob.decode('utf-8'))['drafting_frame']
    assert MODULE.V2.sha_text(MODULE.V2.jtext(frame)) == MODULE.FROZEN_FRAME_SHA256

import copy
import importlib.util
import inspect
import sys
import types
from pathlib import Path

import jsonschema
import pytest

SCRIPT = Path(__file__).parents[1] / 'scripts' / 'publish_archive_assessment_applicability_authority_v2.py'
SPEC = importlib.util.spec_from_file_location('aa3_authority_v2_pub', SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
AuthorityError = MODULE.AuthorityError
build = MODULE.build_published_authority
validate_publication = MODULE.validate_publication
resolve_applicability = MODULE.resolve_applicability
# captured before any fixture fakes them; the real-repo at-pin test restores them
REAL_GIT_DIRTY = MODULE.git_dirty
REAL_GIT_NOT_SHALLOW = MODULE.git_not_shallow
REAL_GIT_HEAD = MODULE.git_head
REAL_GIT_IS_ANCESTOR = MODULE.git_is_ancestor
REAL_CHECK_TREE_MATCHES_HEAD = MODULE.check_tree_matches_head

REQUEST = MODULE.REQUEST_CONTROL_IDS
T, F, U = 'KNOWN_TRUE', 'KNOWN_FALSE', 'UNKNOWN'

def row(a, cid): return next(c for c in a['controls'] if c['control_id'] == cid)

def mutated(mutator):
    value = copy.deepcopy(build())
    mutator(value)
    return value

def fails(mutator, schema_too=False):
    value = mutated(mutator)
    with pytest.raises(AuthorityError):
        validate_publication(value)
    if schema_too:
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.Draft202012Validator(MODULE.schema()).validate(value)

def test_published_document_validates_against_validator_and_schema():
    a = build()
    validate_publication(a)
    jsonschema.Draft202012Validator(MODULE.schema()).validate(a)

def test_21_decided_59_undecided():
    a = build()
    decided = {c['control_id'] for c in a['controls'] if c['not_applicable_decision_state'] != 'NOT_YET_DECIDED'}
    assert decided == set(REQUEST) and len(decided) == 21
    assert sum(c['not_applicable_decision_state'] == 'NOT_YET_DECIDED' for c in a['controls']) == 59

def test_state_counts_and_rules():
    a = build()
    rp = [c for c in a['controls'] if c['not_applicable_decision_state'] == 'RULE_PUBLISHED']
    nr = [c for c in a['controls'] if c['not_applicable_decision_state'] == 'NO_RULE_WILL_BE_PUBLISHED']
    assert len(rp) == 3 and len(nr) == 18
    rules = {c['control_id']: c['not_applicable_rule']['conditions'] for c in rp}
    assert rules == {'EMS-CTRL-030': [{'field': 'production', 'state': F}], 'EMS-CTRL-039': [{'field': 'production', 'state': F}], 'EMS-CTRL-052': [{'field': 'ai_enabled', 'state': F}]}

def test_decision_ids_unchanged_and_id_list():
    a = build()
    assert all(c['decision_ids'] == MODULE.DECISIONS for c in a['controls'])
    assert a['approved_governance_decision_ids'] == MODULE.DECISIONS
    assert a['applicability_decision_ids'] == [f'AA4-GOV-{n:03d}' for n in range(1, 22)]
    assert {c['not_applicable_authority'] for c in a['controls'] if c['not_applicable_authority']} == set(a['applicability_decision_ids'])

def test_rows_stay_lean():
    a = build()
    base = MODULE.build_authority()['controls'][0]
    assert all(set(c) == set(base) for c in a['controls'])

def test_lineage_records_governance_decisions_and_v1():
    lin = build()['source_lineage']
    gd = lin['governance_decisions']
    assert gd['relative_path'] == 'registry/archive_assessment_governance_decisions.json'
    assert gd['record_count'] == 21 and len(gd['drafting_commit']) == 40
    assert gd['sha256'] == MODULE.lf_digest(MODULE.GOVERNANCE_DECISIONS)
    assert lin['supersedes'] == MODULE.SUPERSEDED_V2_0_2
    assert lin['v1_baseline']['commit'] == MODULE.V1_BASELINE_COMMIT and len(lin['v1_baseline']['commit']) == 40 and lin['v1_baseline']['version'] == '1.0.0'
    assert lin['v1_baseline']['sha256'] == MODULE.lf_digest(MODULE.V1_AUTHORITY)
    assert gd['sha256'] == MODULE.SUPERSEDED_V2_0_2['governance_decisions_sha256']
    assert lin['catalog_reference']['sha256'] == hashlib.sha256(MODULE.lf_bytes(MODULE.catalog_bytes())).hexdigest()
    assert lin['catalog_reference']['commit'] == MODULE.CATALOG_COMMIT
    assert 'digest_normalisation' not in lin
    for k in ('aa1_manifest', 'aa2_closure', 'aa2_approval'): assert lin[k]['normalisation'] == 'RAW_BYTES'
    for k in ('catalog_reference', 'v1_baseline', 'supersedes'): assert lin[k]['normalisation'] == 'CRLF_TO_LF'
    assert lin['supersedes']['governance_decisions_normalisation'] == 'CRLF_TO_LF'
    for k in ('aa1_manifest', 'aa2_closure', 'aa2_approval', 'catalog_reference', 'governance_decisions', 'supersedes', 'v1_baseline'): assert lin[k]['relative_path']
    for k in ('supersedes', 'v1_baseline'): assert len(lin[k]['commit']) == 40 and set(lin[k]['commit']) <= set('0123456789abcdef')

def source_without_git_show():
    # D-10: subprocess is confined to the git seam, git_show and git_run (and the import line)
    src = inspect.getsource(MODULE).replace('import subprocess\n', '', 1)
    src = src.replace(inspect.getsource(MODULE.git_show), '', 1)
    return src.replace(inspect.getsource(MODULE.git_run), '', 1)

def test_module_does_not_call_git():
    assert 'subprocess' not in source_without_git_show() and 'import git' not in source_without_git_show()
    assert 'subprocess.run' in inspect.getsource(MODULE.git_show)
    assert 'subprocess.run' in inspect.getsource(MODULE.git_run)

def test_swapped_authority_fails():
    def m(a):
        row(a, 'EMS-CTRL-009')['not_applicable_authority'], row(a, 'EMS-CTRL-010')['not_applicable_authority'] = 'AA4-GOV-002', 'AA4-GOV-001'
    fails(m)

def test_rule_field_change_fails():
    fails(lambda a: row(a, 'EMS-CTRL-030')['not_applicable_rule']['conditions'][0].__setitem__('field', 'ai_enabled'))

def test_rule_state_unknown_fails():
    fails(lambda a: row(a, 'EMS-CTRL-030')['not_applicable_rule']['conditions'][0].__setitem__('state', U), True)

def test_rule_unused_field_fails():
    fails(lambda a: row(a, 'EMS-CTRL-030')['not_applicable_rule']['conditions'][0].__setitem__('field', 'tier'), True)

def test_rule_state_flip_fails():
    fails(lambda a: row(a, 'EMS-CTRL-052')['not_applicable_rule']['conditions'][0].__setitem__('state', T))

def test_decided_flipped_to_not_yet_decided_fails():
    def m(a):
        row(a, 'EMS-CTRL-009').update({'not_applicable_decision_state': 'NOT_YET_DECIDED', 'not_applicable_authority': None})
    fails(m)

def test_22nd_control_decided_fails():
    def m(a):
        row(a, 'EMS-CTRL-001').update({'not_applicable_decision_state': 'NO_RULE_WILL_BE_PUBLISHED', 'not_applicable_authority': 'AA4-GOV-001'})
    fails(m)

def test_v1_field_change_on_undecided_row_fails():
    fails(lambda a: row(a, 'EMS-CTRL-001').__setitem__('default_applicability_result', 'APPLICABLE'), True)
    fails(lambda a: row(a, 'EMS-CTRL-001').__setitem__('control_name', 'Changed'))

def test_extra_field_on_decided_row_fails():
    fails(lambda a: row(a, 'EMS-CTRL-009').__setitem__('rationale', 'copied'))

def test_remove_id_from_list_fails():
    fails(lambda a: a['applicability_decision_ids'].pop())

def test_id_cited_twice_fails():
    fails(lambda a: row(a, 'EMS-CTRL-010').__setitem__('not_applicable_authority', 'AA4-GOV-001'))

def test_duplicate_id_in_list_schema_rejects():
    fails(lambda a: a['applicability_decision_ids'].append('AA4-GOV-001'), True)

def test_altered_governance_digest_fails():
    fails(lambda a: a['source_lineage']['governance_decisions'].__setitem__('sha256', '0' * 64))

def test_altered_record_count_and_drafting_commit_fail():
    fails(lambda a: a['source_lineage']['governance_decisions'].__setitem__('record_count', 20))
    fails(lambda a: a['source_lineage']['governance_decisions'].__setitem__('drafting_commit', '0' * 40))

def test_missing_governance_lineage_fails():
    fails(lambda a: a['source_lineage'].pop('governance_decisions'), True)
    fails(lambda a: a['source_lineage'].pop('v1_baseline'), True)
    fails(lambda a: a['source_lineage'].pop('supersedes'), True)

def test_wrong_v1_lineage_fails():
    fails(lambda a: a['source_lineage']['v1_baseline'].__setitem__('sha256', '0' * 64))
    fails(lambda a: a['source_lineage']['v1_baseline'].__setitem__('commit', 'abcdef0'), True)
    fails(lambda a: a['source_lineage']['supersedes'].__setitem__('commit', 'abcdef0'), True)
    fails(lambda a: a['source_lineage']['supersedes'].__setitem__('governance_decisions_sha256', '0' * 64))

def test_superseded_record_cited_fails(monkeypatch):
    doc = MODULE.load(MODULE.GOVERNANCE_DECISIONS)
    new = copy.deepcopy(doc['records'][0])
    new['decision_id'] = 'AA4-GOV-022'
    new['supersedes'] = 'AA4-GOV-001'
    doc['records'].append(new)
    monkeypatch.setattr(MODULE, 'load', lambda p, _orig=MODULE.load: doc if p == MODULE.GOVERNANCE_DECISIONS else _orig(p))
    # the unsuperseded record for CTRL-009 is now AA4-GOV-022, so building cites it
    built = build()
    assert row(built, 'EMS-CTRL-009')['not_applicable_authority'] == 'AA4-GOV-022'
    built['source_lineage']['governance_decisions']['sha256'] = MODULE.lf_digest(MODULE.GOVERNANCE_DECISIONS)
    stale = copy.deepcopy(built)
    row(stale, 'EMS-CTRL-009')['not_applicable_authority'] = 'AA4-GOV-001'
    stale['applicability_decision_ids'] = sorted(set(stale['applicability_decision_ids']) - {'AA4-GOV-022'} | {'AA4-GOV-001'})
    with pytest.raises(AuthorityError, match='latest unsuperseded'):
        validate_publication(stale)

def test_decisions_digest_bound_to_2_0_0_constant(monkeypatch, tmp_path):
    doc = MODULE.load(MODULE.GOVERNANCE_DECISIONS)
    doc['records'][0]['note'] = doc['records'][0]['note'] + ' amended'
    p = tmp_path / 'decisions.json'; MODULE.dump(p, doc)
    monkeypatch.setattr(MODULE, 'GOVERNANCE_DECISIONS', p)
    a = build()
    a['source_lineage']['governance_decisions']['sha256'] = MODULE.lf_digest(p)
    with pytest.raises(AuthorityError, match=re.escape(MODULE.SUPERSEDED_V2_0_2['version'])):
        validate_publication(a)

def test_row_decision_fields_are_rederived_from_records():
    fails(lambda a: row(a, 'EMS-CTRL-009').__setitem__('not_applicable_decision_state', 'NO_RULE_WILL_BE_PUBLISHED' if row(a, 'EMS-CTRL-009')['not_applicable_decision_state'] != 'NO_RULE_WILL_BE_PUBLISHED' else 'RULE_PUBLISHED'))
    fails(lambda a: row(a, 'EMS-CTRL-030').__setitem__('not_applicable_rule', {'combination': 'ALL_CONDITIONS_MUST_MATCH', 'conditions': [{'field': 'internet_exposed', 'state': 'KNOWN_FALSE'}]}))
    fails(lambda a: a.__setitem__('applicability_decision_ids', list(reversed(a['applicability_decision_ids']))))

def test_resolver_for_rule_controls():
    a = build()
    for cid, field in [('EMS-CTRL-030', 'production'), ('EMS-CTRL-039', 'production'), ('EMS-CTRL-052', 'ai_enabled')]:
        c = row(a, cid)
        assert resolve_applicability(c, {field: F}) == 'NOT_APPLICABLE'
        assert resolve_applicability(c, {field: T}) == 'APPLICABLE'
        assert resolve_applicability(c, {field: U}) == 'APPLICABILITY_UNRESOLVED'
        assert resolve_applicability(c, {}) == 'APPLICABILITY_UNRESOLVED'


import hashlib
import json
import re
import subprocess
import tempfile

from aa_history import require_history

ROOT = Path(__file__).parents[1]
DUAL = MODULE.DUAL_ROLE_STATEMENT

def sha_text(t): return hashlib.sha256(t.encode('utf-8')).hexdigest()

def valid_signoff(authority_digest, on='2026-10-14'):
    return {'status': 'PUBLICATION_SIGNOFF', 'approval': {'approver': 'Oscar Mack', 'role': 'EMS_GOVERNANCE_AUTHORITY', 'date': on, 'scope': 'Publish v2 authority'}, 'dual_role_statement': DUAL, 'authority_id': MODULE.AUTHORITY_ID, 'version': MODULE.VERSION, 'authority_sha256': authority_digest, 'authority_sha256_normalisation': 'CRLF_TO_LF'}

def prev_superseded_authority_bytes():
    sup = MODULE.SUPERSEDED_V2_0_2
    r = subprocess.run(['git', 'show', f"{sup['commit']}:{sup['relative_path']}"], cwd=ROOT, capture_output=True)
    if r.returncode != 0: pytest.fail(f"{sup['version']} authority blob {sup['relative_path']} at commit {sup['commit']} is not reachable in {ROOT}; fetch full history (git fetch --unshallow)", pytrace=False)
    return r.stdout

@pytest.fixture
def lineage_calls():
    return []

@pytest.fixture
def env(monkeypatch, lineage_calls):
    real_catalog = MODULE.catalog_bytes()
    monkeypatch.setattr(MODULE, 'catalog_bytes', lambda: real_catalog)
    # validate_lineage reads git history and the real tree; under the empty temp ROOT it is a recorder
    monkeypatch.setattr(MODULE, 'validate_lineage', lambda lin: lineage_calls.append(lin))
    prev_blob, real_git_show, sup = prev_superseded_authority_bytes(), MODULE.git_show, MODULE.SUPERSEDED_V2_0_2
    # validate_publication compares against the superseded authority in git history; serve it under the empty temp ROOT
    monkeypatch.setattr(MODULE, 'git_show', lambda commit, path: prev_blob if (commit, path) == (sup['commit'], sup['relative_path']) else real_git_show(commit, path))
    # at-pin git state checks run against the real repo otherwise; the temp ROOT is not a git repo
    monkeypatch.setattr(MODULE, 'git_not_shallow', lambda: None)
    monkeypatch.setattr(MODULE, 'git_dirty', lambda paths: [])
    # working-tree vs HEAD binding (CR-01, WR-01); tests that need the real check restore REAL_CHECK_TREE_MATCHES_HEAD
    monkeypatch.setattr(MODULE, 'check_tree_matches_head', lambda paths: None)
    # plain-mode D-06 ancestry; tests that need real history restore REAL_GIT_HEAD / REAL_GIT_IS_ANCESTOR
    monkeypatch.setattr(MODULE, 'git_head', lambda: HEAD_COMMIT)
    monkeypatch.setattr(MODULE, 'git_is_ancestor', lambda a, b: True)
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        for name, value in {'ROOT': root, 'AUTHORITY': root / 'registry' / 'a.json', 'SCHEMA': root / 'schemas' / 's.json', 'SIGNOFF': root / 'registry' / 'signoff.json', 'PUBLICATION_RECORD': root / 'registry' / 'record.json', 'OUT': root / 'generated' / 'out', 'SCRIPT': root / 'scripts' / 'pub.py'}.items():
            monkeypatch.setattr(MODULE, name, value)
        MODULE.dump(MODULE.SCHEMA, MODULE.schema())
        MODULE.write_text(MODULE.SCRIPT, 'print(1)\n')
        yield root

def write_signoff(a=None, on='2026-10-14'):
    a = a or build()
    MODULE.dump(MODULE.SIGNOFF, valid_signoff(sha_text(MODULE.jtext(a)), on))

def outputs(a=None, on='2026-10-14', **kw):
    a = a or build()
    write_signoff(a, on)
    return MODULE.build_all_outputs(a, MODULE.load(MODULE.SIGNOFF), **kw)

def test_outputs_deterministic_and_lf_only(env):
    first = outputs()
    assert first == outputs()
    assert list(first) == [MODULE.N_MATRIX, MODULE.N_SEMANTIC, MODULE.N_NEGATIVE, MODULE.N_TRACE, MODULE.N_CERT, MODULE.N_REPORT, MODULE.N_MANIFEST]
    for text in first.values():
        assert '\r' not in text
        assert 'T00:' not in text
    assert '2026-10-14' in first[MODULE.N_CERT]
    assert json.loads(first[MODULE.N_CERT])['digest_normalisation'] == 'CRLF_TO_LF'
    assert json.loads(first[MODULE.N_MANIFEST])['digest_normalisation'] == 'CRLF_TO_LF'

def test_traceability_21_and_59(env):
    t = json.loads(outputs()[MODULE.N_TRACE])
    assert len(t['decision_records']) == 21 and len(t['undecided_controls']) == 59
    r = t['decision_records'][0]
    assert {'control_id', 'decision_id', 'state', 'rule', 'decision_record_path', 'decision_record_sha256'} <= set(r)

def test_semantic_output_never_resolves_unknown_to_not_applicable(env):
    s = json.loads(outputs()[MODULE.N_SEMANTIC])
    assert s['unknown_never_not_applicable'] is True and len(s['rule_controls']) == 3
    for c in s['rule_controls']:
        assert c['results']['UNKNOWN'] == 'APPLICABILITY_UNRESOLVED'
        assert c['results']['KNOWN_FALSE'] == 'NOT_APPLICABLE' and c['results']['KNOWN_TRUE'] == 'APPLICABLE'

def so_fails(mutator):
    r = valid_signoff('d' * 64)
    mutator(r)
    with pytest.raises(AuthorityError):
        MODULE.validate_signoff(r, 'd' * 64)

def test_signoff_valid_passes():
    MODULE.validate_signoff(valid_signoff('d' * 64), 'd' * 64)

@pytest.mark.parametrize('key', ['status', 'approval', 'dual_role_statement', 'authority_id', 'version', 'authority_sha256', 'authority_sha256_normalisation'])
def test_signoff_missing_key_fails(key):
    so_fails(lambda r: r.pop(key))

@pytest.mark.parametrize('key', ['approver', 'role', 'date', 'scope'])
def test_signoff_missing_approval_key_fails(key):
    so_fails(lambda r: r['approval'].pop(key))

def test_signoff_value_mutations_fail():
    so_fails(lambda r: r.__setitem__('status', 'DRAFT'))
    so_fails(lambda r: r['approval'].__setitem__('approver', 'Someone Else'))
    so_fails(lambda r: r['approval'].__setitem__('role', 'INTERN'))
    so_fails(lambda r: r.__setitem__('dual_role_statement', ''))
    so_fails(lambda r: r.__setitem__('dual_role_statement', 'Oscar Mack approved this.'))
    so_fails(lambda r: r.__setitem__('authority_sha256', 'e' * 64))
    so_fails(lambda r: r.__setitem__('authority_sha256_normalisation', 'NONE'))

def test_signoff_hardening_cases_fail():
    so_fails(lambda r: r['approval'].__setitem__('role', 'HAYES_VERIFY_DEVELOPER'))
    so_fails(lambda r: r['approval'].__setitem__('date', 'not-a-date'))
    so_fails(lambda r: r['approval'].__setitem__('date', '2026-02-30'))
    so_fails(lambda r: r.__setitem__('dual_role_statement', DUAL + ' Extra text.'))
    so_fails(lambda r: r.__setitem__('extra', 'x'))
    so_fails(lambda r: r['approval'].__setitem__('extra', 'x'))
    so_fails(lambda r: r['approval'].__setitem__('scope', ''))
    so_fails(lambda r: r['approval'].__setitem__('scope', 5))

def test_signoff_role_constant():
    assert MODULE.SIGNOFF_ROLE == 'EMS_GOVERNANCE_AUTHORITY'
    assert MODULE.SIGNOFF_ROLE in MODULE.APPROVER_ROLES

_TAMPER_DIR = tempfile.TemporaryDirectory()

def tampered_decisions(name, mutator):
    doc = copy.deepcopy(json.loads(MODULE.GOVERNANCE_DECISIONS.read_text(encoding='utf-8')))
    mutator(doc)
    p = Path(_TAMPER_DIR.name) / f'{name}.json'
    p.write_text(json.dumps(doc, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    return p

def _all(key, value):
    def m(doc):
        for r in doc['records']: r[key] = value
    return m

def _drop_decided(doc): doc['records'][0].pop('decided')

@pytest.mark.parametrize('name,mutator', [
    ('approver', _all('approver', 'Someone Else')),
    ('dual_role', _all('dual_role_statement', '')),
    ('disposition', _all('disposition', 'BOGUS')),
    ('missing_decided', _drop_decided),
])
def test_decisions_gate_rejects_tampered_file(monkeypatch, name, mutator):
    monkeypatch.setattr(MODULE, 'GOVERNANCE_DECISIONS', tampered_decisions(name, mutator))
    with pytest.raises(MODULE.AuthorityError):
        MODULE.published_authority_checked()
    with pytest.raises(MODULE.AuthorityError):
        MODULE.validate_published()

def test_decisions_gate_passes_real_file():
    doc = MODULE.validate_governance_decisions()
    assert len(doc['records']) == 21

def test_decisions_builder_is_cached():
    assert MODULE.decisions_builder() is MODULE.decisions_builder()

def test_publish_refuses_without_signoff(env):
    with pytest.raises(AuthorityError):
        MODULE.publish(False)
    assert not MODULE.AUTHORITY.exists() and not MODULE.OUT.exists()

def test_publish_refuses_on_digest_mismatch_or_wrong_approver(env):
    MODULE.dump(MODULE.SIGNOFF, valid_signoff('f' * 64))
    with pytest.raises(AuthorityError):
        MODULE.publish(False)
    r = valid_signoff(sha_text(MODULE.jtext(build())))
    r['approval']['approver'] = 'Someone Else'
    MODULE.dump(MODULE.SIGNOFF, r)
    with pytest.raises(AuthorityError):
        MODULE.publish(False)
    assert not MODULE.AUTHORITY.exists()

def test_dry_run_writes_nothing_and_summarises(env, capsys):
    MODULE.publish(True)
    out = capsys.readouterr().out
    assert 'Decided controls: 21' in out and 'Undecided controls: 59' in out
    assert 'EMS-CTRL-030: ALL_CONDITIONS_MUST_MATCH: production = KNOWN_FALSE' in out
    assert 'EMS-CTRL-052: ALL_CONDITIONS_MUST_MATCH: ai_enabled = KNOWN_FALSE' in out
    assert sha_text(MODULE.jtext(build())) in out
    for cid in REQUEST: assert cid in out
    assert 'AA4-GOV-001' in out and 'NO_RULE_WILL_BE_PUBLISHED' in out
    for word in ('best', 'critical', 'important', 'recommended', 'highest'): assert word not in out.lower()
    assert not MODULE.AUTHORITY.exists() and not MODULE.OUT.exists()

def snapshot():
    return {p: p.read_bytes() for p in sorted(MODULE.OUT.iterdir())} | {MODULE.AUTHORITY: MODULE.AUTHORITY.read_bytes()}

def published(env):
    write_signoff()
    MODULE.publish(False)

RECORD_COMMIT = 'a' * 40
HEAD_COMMIT = 'b' * 40

@pytest.fixture
def fake_git_show(monkeypatch):
    blobs = {(MODULE.SUPERSEDED_V2_0_2['commit'], MODULE.SUPERSEDED_V2_0_2['relative_path']): prev_superseded_authority_bytes()}
    def fake(commit, path):
        if (commit, path) not in blobs: raise AuthorityError(f'{path}@{commit[:7]}: git show failed: unknown object')
        return blobs[(commit, path)]
    monkeypatch.setattr(MODULE, 'git_show', fake)
    return blobs

def register_blobs(blobs, commit=RECORD_COMMIT):
    blobs[(commit, MODULE.rel(MODULE.AUTHORITY))] = MODULE.AUTHORITY.read_bytes()
    blobs[(commit, MODULE.rel(MODULE.OUT / MODULE.N_MANIFEST))] = (MODULE.OUT / MODULE.N_MANIFEST).read_bytes()
    # D-06: every D-05 file (and the publisher script) at the publication commit and at HEAD
    for p in [*MODULE.publication_paths(), MODULE.rel(MODULE.SCRIPT)]:
        data = (MODULE.ROOT / p).read_bytes()
        blobs[(commit, p)] = data
        blobs[(HEAD_COMMIT, p)] = data

def published_recorded(env, blobs):
    published(env)
    MODULE.write_publication_record(RECORD_COMMIT)
    register_blobs(blobs)

def test_publish_writes_all_and_is_byte_identical(env, fake_git_show):
    published(env)
    first = snapshot()
    assert len(first) == 8
    assert all(b'\r' not in v for v in first.values())
    MODULE.publish(False)
    assert snapshot() == first
    MODULE.write_publication_record(RECORD_COMMIT); register_blobs(fake_git_show)
    MODULE.validate_published()

def test_validate_published_calls_validate_lineage(env, lineage_calls, fake_git_show):
    published_recorded(env, fake_git_show)
    lineage_calls.clear()
    MODULE.validate_published()
    a = MODULE.load(MODULE.AUTHORITY)
    assert lineage_calls == [a['source_lineage']]

def test_validate_published_rejects_absent_authority(env):
    with pytest.raises(AuthorityError, match='not published'):
        MODULE.validate_published()

def test_validate_rejects_changed_output(env):
    published(env)
    p = MODULE.OUT / MODULE.N_MATRIX
    p.write_bytes(p.read_bytes().replace(b'80', b'81', 1))
    with pytest.raises(AuthorityError):
        MODULE.validate_published()

def test_validate_rejects_hand_edit_with_consistent_rehash(env):
    published(env)
    a = MODULE.load(MODULE.AUTHORITY)
    row(a, 'EMS-CTRL-009')['not_applicable_decision_state'] = 'NOT_YET_DECIDED'
    row(a, 'EMS-CTRL-009')['not_applicable_authority'] = None
    MODULE.dump(MODULE.AUTHORITY, a)
    write_signoff(a)
    ps = MODULE.load(MODULE.OUT / MODULE.N_MANIFEST)['publisher_script']['sha256']
    outs = MODULE.build_all_outputs(a, MODULE.load(MODULE.SIGNOFF), script_sha256=ps)
    for n, t in outs.items(): MODULE.write_text(MODULE.OUT / n, t)
    with pytest.raises(AuthorityError):
        MODULE.validate_published()

def test_validate_rejects_signoff_digest_mismatch(env):
    published(env)
    MODULE.dump(MODULE.SIGNOFF, valid_signoff('a' * 64))
    with pytest.raises(AuthorityError):
        MODULE.validate_published()

def test_validate_rejects_manifest_digest_difference(env):
    published(env)
    p = MODULE.OUT / MODULE.N_MANIFEST
    m = json.loads(p.read_text(encoding='utf-8'))
    m['artifacts'][0]['sha256'] = '0' * 64
    MODULE.dump(p, m)
    with pytest.raises(AuthorityError):
        MODULE.validate_published()

def test_validate_rejects_extra_or_missing_file(env):
    published(env)
    (MODULE.OUT / 'extra.txt').write_text('x', encoding='utf-8')
    with pytest.raises(AuthorityError):
        MODULE.validate_published()
    (MODULE.OUT / 'extra.txt').unlink()
    (MODULE.OUT / MODULE.N_REPORT).unlink()
    with pytest.raises(AuthorityError):
        MODULE.validate_published()

def test_write_publication_record(env, fake_git_show):
    published(env)
    MODULE.write_publication_record('a' * 40)
    rec = MODULE.load(MODULE.PUBLICATION_RECORD)
    assert set(rec) == {'publication_commit', 'authority_id', 'version', 'authority_sha256', 'manifest_sha256', 'digest_normalisation'}
    assert rec['publication_commit'] == 'a' * 40 and rec['digest_normalisation'] == 'CRLF_TO_LF'
    assert rec['authority_sha256'] == MODULE.lf_digest(MODULE.AUTHORITY)
    for bad in ('abc', 'A' * 40, 'g' * 40, ''):
        with pytest.raises(AuthorityError):
            MODULE.write_publication_record(bad)

def test_validate_record_absent_fails(env, fake_git_show):
    published(env)
    assert not MODULE.PUBLICATION_RECORD.exists()
    with pytest.raises(AuthorityError, match='absent'):
        MODULE.validate_published()
    with pytest.raises(AuthorityError, match='absent'):
        MODULE.validate_published(True)

def test_validate_record_matching_passes(env, fake_git_show):
    published_recorded(env, fake_git_show)
    MODULE.validate_published()

def authority_supersedes():
    return MODULE.load(MODULE.AUTHORITY)['source_lineage']['supersedes']

def superseded_authority_blob(s):
    blob = subprocess.run(['git', 'show', f"{s['commit']}:{s['relative_path']}", '--'], cwd=SCRIPT.parents[1], capture_output=True, check=True).stdout
    assert hashlib.sha256(MODULE.lf_bytes(blob)).hexdigest() == s['sha256']
    return blob

def superseded_record(blobs, **over):
    s = authority_supersedes()
    rec = {'publication_commit': s['commit'], 'authority_id': s['authority_id'], 'version': s['version'], 'authority_sha256': s['sha256'], 'manifest_sha256': MODULE.lf_digest(MODULE.OUT / MODULE.N_MANIFEST), 'digest_normalisation': 'CRLF_TO_LF'}
    rec.update(over)
    MODULE.dump(MODULE.PUBLICATION_RECORD, rec)
    blobs[(s['commit'], MODULE.rel(MODULE.AUTHORITY))] = b'superseded authority bytes\n'
    blobs[(s['commit'], MODULE.rel(MODULE.OUT / MODULE.N_MANIFEST))] = (MODULE.OUT / MODULE.N_MANIFEST).read_bytes()
    return rec

def test_at_pin_mode_accepts_only_superseded_record(env, fake_git_show, capsys):
    published(env)
    s = authority_supersedes()
    # D-02 needs the real superseded authority blob; patching the pinned sha would break source_lineage.supersedes
    blob = superseded_authority_blob(s)
    superseded_record(fake_git_show)
    fake_git_show[(s['commit'], MODULE.rel(MODULE.AUTHORITY))] = blob
    capsys.readouterr()
    MODULE.validate_published(True)
    out = capsys.readouterr().out
    assert out.endswith('\n') and out.count('\n') == 1
    doc = json.loads(out)
    assert doc == {'status': 'PASS', 'mode': 'AT_PIN', 'deferred': [MODULE.AT_PIN_DEFERRED]}
    assert len(doc['deferred']) == 1 and doc['deferred'][0].startswith('PUBLICATION_RECORD_BINDING: ')
    with pytest.raises(AuthorityError, match='--validate --at-pin'):
        MODULE.validate_published()

def test_at_pin_binding_reads_supersedes_from_authority(env, fake_git_show):
    published_recorded(env, fake_git_show)
    sup = authority_supersedes()
    rec = superseded_record(fake_git_show)
    assert (rec['publication_commit'], rec['authority_id'], rec['version'], rec['authority_sha256']) == (sup['commit'], sup['authority_id'], sup['version'], sup['sha256'])
    # the identity follows the authority document passed in, not a module constant
    other_blob = b'another superseded authority\n'
    other = dict(sup, authority_id='EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-9.9.8', version='9.9.8', commit='c' * 40, sha256=hashlib.sha256(other_blob).hexdigest())
    a = MODULE.load(MODULE.AUTHORITY); a['source_lineage']['supersedes'] = other
    superseded_record(fake_git_show, publication_commit=other['commit'], authority_id=other['authority_id'], version=other['version'], authority_sha256=other['sha256'])
    fake_git_show[(other['commit'], MODULE.rel(MODULE.AUTHORITY))] = other_blob
    fake_git_show[(other['commit'], MODULE.rel(MODULE.OUT / MODULE.N_MANIFEST))] = (MODULE.OUT / MODULE.N_MANIFEST).read_bytes()
    script_sha256 = MODULE.load(MODULE.OUT / MODULE.N_MANIFEST)['publisher_script']['sha256']
    MODULE.check_publication_record(a, True, script_sha256)
    with pytest.raises(AuthorityError, match=f"superseded {re.escape(sup['version'])} publication commit"):
        MODULE.check_publication_record(MODULE.load(MODULE.AUTHORITY), True, script_sha256)

def test_other_authority_record_fails_in_both_modes(env, fake_git_show):
    published_recorded(env, fake_git_show)
    rec = MODULE.load(MODULE.PUBLICATION_RECORD)
    rec['authority_id'] = 'EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-9.9.9'; rec['version'] = '9.9.9'
    MODULE.dump(MODULE.PUBLICATION_RECORD, rec)
    for mode in (False, True):
        with pytest.raises(AuthorityError):
            MODULE.validate_published(mode)

def test_at_pin_wrong_commit_or_digest_fails(env, fake_git_show):
    published_recorded(env, fake_git_show)
    v = re.escape(authority_supersedes()['version'])
    superseded_record(fake_git_show, publication_commit='b' * 40)
    with pytest.raises(AuthorityError, match=f'superseded {v} publication commit'):
        MODULE.validate_published(True)
    superseded_record(fake_git_show, authority_sha256='0' * 64)
    with pytest.raises(AuthorityError, match=f'superseded {v} digest'):
        MODULE.validate_published(True)

def test_at_pin_record_blobs_must_match_the_superseded_commit(env, fake_git_show):
    published(env)
    s = authority_supersedes()
    # superseded_record serves a wrong authority blob at the superseded commit
    superseded_record(fake_git_show)
    with pytest.raises(AuthorityError, match='authority at the publication commit'):
        MODULE.validate_published(True)
    fake_git_show[(s['commit'], MODULE.rel(MODULE.AUTHORITY))] = superseded_authority_blob(s)
    fake_git_show[(s['commit'], MODULE.rel(MODULE.OUT / MODULE.N_MANIFEST))] = b'different manifest bytes\n'
    with pytest.raises(AuthorityError, match='manifest at the publication commit'):
        MODULE.validate_published(True)

def test_at_pin_dirty_tree_fails_closed(env, monkeypatch):
    seen, tree = [], []
    monkeypatch.setattr(MODULE, 'check_tree_matches_head', lambda paths: tree.append(list(paths)))
    monkeypatch.setattr(MODULE, 'git_dirty', lambda paths: seen.append(list(paths)) or [' M registry/a.json'])
    with pytest.raises(AuthorityError, match='at-pin: git status'):
        MODULE.validate_published(True)
    assert tree == [MODULE.publication_paths() + [MODULE.rel(MODULE.SCRIPT)]]
    assert len(tree[0]) == 11
    assert seen == [MODULE.publication_paths() + [MODULE.rel(MODULE.SCRIPT), MODULE.rel(MODULE.OUT)]]
    assert len(seen[0]) == 12
    # plain mode does not consult the working-tree state
    with pytest.raises(AuthorityError, match='not published'):
        MODULE.validate_published()
    assert len(seen) == 1

def test_at_pin_shallow_fails_closed(env, monkeypatch):
    dirty_calls, tree_calls = [], []
    def shallow(): raise MODULE.GitHistoryError('the clone is shallow; fetch full history (git fetch --unshallow)')
    monkeypatch.setattr(MODULE, 'git_not_shallow', shallow)
    monkeypatch.setattr(MODULE, 'git_dirty', lambda paths: dirty_calls.append(paths) or [])
    monkeypatch.setattr(MODULE, 'check_tree_matches_head', lambda paths: tree_calls.append(paths))
    with pytest.raises(MODULE.GitHistoryError, match='shallow'):
        MODULE.validate_published(True)
    assert dirty_calls == []
    assert tree_calls == []

@pytest.mark.parametrize('mutate', [lambda r: r.pop('version'), lambda r: r.__setitem__('extra', 1)], ids=['missing_key', 'extra_key'])
def test_record_shape_violation_raises_authority_error(env, fake_git_show, mutate):
    published_recorded(env, fake_git_show)
    rec = MODULE.load(MODULE.PUBLICATION_RECORD); mutate(rec)
    MODULE.dump(MODULE.PUBLICATION_RECORD, rec)
    with pytest.raises(AuthorityError, match='exactly the six'):
        MODULE.validate_published()

@pytest.mark.parametrize('value', [[], 'text', 7])
def test_record_non_object_raises_authority_error(env, fake_git_show, value):
    published_recorded(env, fake_git_show)
    MODULE.dump(MODULE.PUBLICATION_RECORD, value)
    with pytest.raises(AuthorityError, match='exactly the six'):
        MODULE.validate_published()

@pytest.mark.parametrize('value', ['RAW_BYTES', 7, None, 'crlf_to_lf'])
def test_record_digest_normalisation_must_be_crlf_to_lf(env, fake_git_show, value):
    published_recorded(env, fake_git_show)
    rec = MODULE.load(MODULE.PUBLICATION_RECORD)
    rec['digest_normalisation'] = value
    MODULE.dump(MODULE.PUBLICATION_RECORD, rec)
    for mode in (False, True):
        with pytest.raises(AuthorityError, match='digest_normalisation must be CRLF_TO_LF'):
            MODULE.validate_published(mode)

@pytest.mark.parametrize('key', ['authority_sha256', 'manifest_sha256'])
def test_validate_record_digest_mismatch_fails(env, fake_git_show, key):
    published_recorded(env, fake_git_show)
    rec = MODULE.load(MODULE.PUBLICATION_RECORD)
    rec[key] = '0' * 64
    MODULE.dump(MODULE.PUBLICATION_RECORD, rec)
    with pytest.raises(AuthorityError, match=key):
        MODULE.validate_published()

@pytest.mark.parametrize('rel_name', ['authority', 'manifest'])
def test_commit_blob_digest_differs_fails(env, fake_git_show, rel_name):
    published_recorded(env, fake_git_show)
    path = MODULE.AUTHORITY if rel_name == 'authority' else MODULE.OUT / MODULE.N_MANIFEST
    fake_git_show[(RECORD_COMMIT, MODULE.rel(path))] = b'different bytes\n'
    with pytest.raises(AuthorityError, match='publication commit'):
        MODULE.validate_published()

def test_unreachable_publication_commit_fails_closed(env, fake_git_show):
    published_recorded(env, fake_git_show)
    fake_git_show.clear()
    with pytest.raises(AuthorityError, match='git show failed'):
        MODULE.validate_published()

def use_real_git_state(monkeypatch):
    monkeypatch.setattr(MODULE, 'git_head', REAL_GIT_HEAD)
    monkeypatch.setattr(MODULE, 'git_is_ancestor', REAL_GIT_IS_ANCESTOR)
    monkeypatch.setattr(MODULE, 'git_not_shallow', REAL_GIT_NOT_SHALLOW)
    monkeypatch.setattr(MODULE, 'check_tree_matches_head', REAL_CHECK_TREE_MATCHES_HEAD)

def test_plain_validate_requires_ancestry(env, fake_git_show, monkeypatch):
    published_recorded(env, fake_git_show)
    MODULE.validate_published()
    seen = []
    monkeypatch.setattr(MODULE, 'git_is_ancestor', lambda a, b: seen.append((a, b)) or False)
    with pytest.raises(AuthorityError, match='is not an ancestor of HEAD'):
        MODULE.validate_published()
    assert seen == [(RECORD_COMMIT, HEAD_COMMIT)]

@pytest.mark.parametrize('which', ['authority', 'schema', 'manifest'])
def test_plain_validate_requires_blob_identity_at_head(env, fake_git_show, which):
    published_recorded(env, fake_git_show)
    path = {'authority': MODULE.AUTHORITY, 'schema': MODULE.SCHEMA, 'manifest': MODULE.OUT / MODULE.N_MANIFEST}[which]
    p = MODULE.rel(path)
    assert p in MODULE.publication_paths()
    fake_git_show[(HEAD_COMMIT, p)] = fake_git_show[(HEAD_COMMIT, p)] + b' '
    with pytest.raises(AuthorityError, match=re.escape(p) + ': differs between the publication commit and HEAD'):
        MODULE.validate_published()

def test_plain_validate_shallow_fails_closed(env, fake_git_show, monkeypatch):
    published_recorded(env, fake_git_show)
    head_calls = []
    def shallow(): raise MODULE.GitHistoryError('the clone is shallow; fetch full history (git fetch --unshallow)')
    monkeypatch.setattr(MODULE, 'git_not_shallow', shallow)
    monkeypatch.setattr(MODULE, 'git_head', lambda: head_calls.append(1) or HEAD_COMMIT)
    with pytest.raises(MODULE.GitHistoryError, match='shallow'):
        MODULE.validate_published()
    assert head_calls == []

def test_plain_validate_at_pin_record_points_to_at_pin(env, fake_git_show):
    published(env)
    v = re.escape(authority_supersedes()['version'])
    superseded_record(fake_git_show)
    with pytest.raises(AuthorityError, match=f'still names the superseded {v} publication.*run --validate --at-pin here'):
        MODULE.validate_published()

def test_real_git_repo_record_passes_plain_mode(env, monkeypatch):
    def run(*args): return subprocess.run(['git', *args], cwd=MODULE.ROOT, capture_output=True)
    require_history(ROOT)
    r = run('init', '-q')
    if r.returncode != 0: pytest.fail(f"git init failed in temp repo {MODULE.ROOT}: {r.stderr.decode('utf-8', 'replace')}", pytrace=False)
    run('config', 'user.email', 't@example.com'); run('config', 'user.name', 't'); run('config', 'commit.gpgsign', 'false')
    use_real_git_state(monkeypatch)
    published(env)
    run('add', '-A')
    r = run('commit', '-q', '-m', 'publish')
    if r.returncode != 0: pytest.fail(f"git commit failed in temp repo {MODULE.ROOT}: {r.stderr.decode('utf-8', 'replace')}", pytrace=False)
    sha = run('rev-parse', 'HEAD').stdout.decode().strip()
    MODULE.write_publication_record(sha)
    MODULE.validate_published()

def test_real_git_repo_plain_passes_after_record_and_later_commits_and_catches_head_drift(env, monkeypatch):
    def run(*args): return subprocess.run(['git', *args], cwd=MODULE.ROOT, capture_output=True)
    def commit(msg):
        r = run('commit', '-q', '-m', msg)
        if r.returncode != 0: pytest.fail(f"git commit failed in temp repo {MODULE.ROOT}: {r.stderr.decode('utf-8', 'replace')}", pytrace=False)
        return run('rev-parse', 'HEAD').stdout.decode().strip()
    require_history(ROOT)
    r = run('init', '-q')
    if r.returncode != 0: pytest.fail(f"git init failed in temp repo {MODULE.ROOT}: {r.stderr.decode('utf-8', 'replace')}", pytrace=False)
    run('config', 'user.email', 't@example.com'); run('config', 'user.name', 't'); run('config', 'commit.gpgsign', 'false'); run('config', 'core.autocrlf', 'false')
    use_real_git_state(monkeypatch)
    published(env)
    run('add', '-A')
    c1 = commit('publish')
    MODULE.write_publication_record(c1)
    run('add', '-A')
    c2 = commit('record')
    (MODULE.ROOT / 'notes.txt').write_text('unrelated\n', encoding='utf-8')
    run('add', 'notes.txt')
    c3 = commit('unrelated')
    assert len({c1, c2, c3}) == 3 and MODULE.git_head() == c3
    MODULE.validate_published()
    schema_rel = MODULE.rel(MODULE.SCHEMA)
    original = MODULE.SCHEMA.read_bytes()
    MODULE.SCHEMA.write_bytes(original + b'\n')
    run('add', schema_rel)
    commit('drift')
    r = run('checkout', 'HEAD~1', '--', schema_rel)
    assert r.returncode == 0, r.stderr
    assert MODULE.SCHEMA.read_bytes() == original
    with pytest.raises(AuthorityError, match=re.escape(schema_rel) + ': differs between the publication commit and HEAD'):
        MODULE.validate_published()

def test_real_git_repo_at_pin_passes_and_dirty_fails(env, fake_git_show, monkeypatch, capsys):
    def run(*args): return subprocess.run(['git', *args], cwd=MODULE.ROOT, capture_output=True)
    require_history(ROOT)
    r = run('init', '-q')
    if r.returncode != 0: pytest.fail(f"git init failed in temp repo {MODULE.ROOT}: {r.stderr.decode('utf-8', 'replace')}", pytrace=False)
    run('config', 'user.email', 't@example.com'); run('config', 'user.name', 't'); run('config', 'commit.gpgsign', 'false'); run('config', 'core.autocrlf', 'false')
    published(env)
    s = authority_supersedes()
    superseded_record(fake_git_show)
    # git_show stays faked: it serves the superseded-commit blobs, which are not in the temp repo
    fake_git_show[(s['commit'], MODULE.rel(MODULE.AUTHORITY))] = superseded_authority_blob(s)
    run('add', '-A')
    r = run('commit', '-q', '-m', 'publish')
    if r.returncode != 0: pytest.fail(f"git commit failed in temp repo {MODULE.ROOT}: {r.stderr.decode('utf-8', 'replace')}", pytrace=False)
    monkeypatch.setattr(MODULE, 'git_dirty', REAL_GIT_DIRTY)
    monkeypatch.setattr(MODULE, 'git_not_shallow', REAL_GIT_NOT_SHALLOW)
    monkeypatch.setattr(MODULE, 'git_head', REAL_GIT_HEAD)
    monkeypatch.setattr(MODULE, 'check_tree_matches_head', REAL_CHECK_TREE_MATCHES_HEAD)
    capsys.readouterr()
    MODULE.validate_published(True)
    assert json.loads(capsys.readouterr().out) == {'status': 'PASS', 'mode': 'AT_PIN', 'deferred': [MODULE.AT_PIN_DEFERRED]}
    original = MODULE.AUTHORITY.read_bytes()
    MODULE.AUTHORITY.write_bytes(original + b' ')
    with pytest.raises(AuthorityError, match='working tree differs from HEAD'):
        MODULE.validate_published(True)
    MODULE.AUTHORITY.write_bytes(original)
    MODULE.validate_published(True)
    MODULE.write_text(MODULE.SCRIPT, 'print(2)\n')
    with pytest.raises(AuthorityError, match='working tree differs from HEAD') as e:
        MODULE.validate_published(True)
    assert MODULE.rel(MODULE.SCRIPT) in str(e.value)

# ---- 12-08 Task 3 (WR-04): real-layout git repos, `.gitignore: generated/` with force-added generated files ----

def real_layout_pin(env, fake_git_show, monkeypatch):
    def run(*args): return subprocess.run(['git', *args], cwd=MODULE.ROOT, capture_output=True)
    require_history(ROOT)
    r = run('init', '-q')
    if r.returncode != 0: pytest.fail(f"git init failed in temp repo {MODULE.ROOT}: {r.stderr.decode('utf-8', 'replace')}", pytrace=False)
    run('config', 'user.email', 't@example.com'); run('config', 'user.name', 't'); run('config', 'commit.gpgsign', 'false'); run('config', 'core.autocrlf', 'false')
    # mirrors .gitignore:6 of this repository; the generated publication files are force-added
    (MODULE.ROOT / '.gitignore').write_text('generated/\n', encoding='utf-8')
    published(env)
    s = authority_supersedes()
    superseded_record(fake_git_show)
    # git_show stays faked: it serves the superseded-commit blobs, which are not in the temp repo
    fake_git_show[(s['commit'], MODULE.rel(MODULE.AUTHORITY))] = superseded_authority_blob(s)
    run('add', '-A')
    run('add', '-f', '--', MODULE.rel(MODULE.OUT))
    r = run('commit', '-q', '-m', 'publish')
    if r.returncode != 0: pytest.fail(f"git commit failed in temp repo {MODULE.ROOT}: {r.stderr.decode('utf-8', 'replace')}", pytrace=False)
    monkeypatch.setattr(MODULE, 'git_dirty', REAL_GIT_DIRTY)
    monkeypatch.setattr(MODULE, 'git_not_shallow', REAL_GIT_NOT_SHALLOW)
    monkeypatch.setattr(MODULE, 'git_head', REAL_GIT_HEAD)
    monkeypatch.setattr(MODULE, 'check_tree_matches_head', REAL_CHECK_TREE_MATCHES_HEAD)
    out_rel = MODULE.rel(MODULE.OUT)
    assert sorted(run('ls-files', '--', out_rel).stdout.decode().split()) == sorted(MODULE.publication_paths()[3:])
    assert run('check-ignore', '-q', '--no-index', '--', f'{out_rel}/{MODULE.N_MANIFEST}').returncode == 0
    return run

def legacy_status(run):
    # the pre-12-08 at-pin status argv
    r = run('status', '--porcelain', '--', *MODULE.publication_paths(), MODULE.rel(MODULE.SCRIPT), MODULE.rel(MODULE.OUT))
    assert r.returncode == 0, r.stderr
    return r.stdout.decode('utf-8', 'replace')

def at_pin_pass(capsys):
    capsys.readouterr()
    MODULE.validate_published(True)
    assert json.loads(capsys.readouterr().out) == {'status': 'PASS', 'mode': 'AT_PIN', 'deferred': [MODULE.AT_PIN_DEFERRED]}

def test_real_layout_at_pin_passes_on_clean_pinned_tree(env, fake_git_show, monkeypatch, capsys):
    real_layout_pin(env, fake_git_show, monkeypatch)
    at_pin_pass(capsys)
    # ignored content elsewhere under generated/ is outside the at-pin pathspecs
    MODULE.write_text(MODULE.ROOT / 'generated' / 'other' / 'scratch.txt', 'scratch\n')
    at_pin_pass(capsys)

def test_real_layout_at_pin_passes_with_crlf_on_disk_over_lf_blobs(env, fake_git_show, monkeypatch, capsys):
    run = real_layout_pin(env, fake_git_show, monkeypatch)
    run('config', 'core.autocrlf', 'true')
    files = [MODULE.AUTHORITY, MODULE.SCRIPT, MODULE.OUT / MODULE.N_MATRIX]
    for f in files: f.unlink()
    # git itself writes the CRLF checkout (hand-written CRLF changes the size the index records)
    r = run('checkout', '--', *[MODULE.rel(f) for f in files])
    assert r.returncode == 0, r.stderr
    for f in files: assert b'\r\n' in f.read_bytes(), f
    assert b'\r' not in run('cat-file', 'blob', f'HEAD:{MODULE.rel(MODULE.AUTHORITY)}').stdout
    at_pin_pass(capsys)

BLIND_SPOT_CASES = ['rm_cached_generated', 'skip_worktree_authority_edit', 'assume_unchanged_authority_edit', 'skip_worktree_script_edit', 'assume_unchanged_script_edit', 'skip_worktree_flag_only', 'assume_unchanged_flag_only', 'untracked_with_show_untracked_no', 'ignored_extra_in_out']

@pytest.mark.parametrize('case', BLIND_SPOT_CASES)
def test_real_layout_at_pin_fails_closed_where_git_status_is_blind(env, fake_git_show, monkeypatch, case):
    run = real_layout_pin(env, fake_git_show, monkeypatch)
    def commit(msg):
        r = run('commit', '-q', '-m', msg)
        if r.returncode != 0: pytest.fail(f"git commit failed in temp repo {MODULE.ROOT}: {r.stderr.decode('utf-8', 'replace')}", pytrace=False)
    def git_ok(*args):
        r = run(*args)
        assert r.returncode == 0, r.stderr
    matrix, auth, script, signoff = f'{MODULE.rel(MODULE.OUT)}/{MODULE.N_MATRIX}', MODULE.rel(MODULE.AUTHORITY), MODULE.rel(MODULE.SCRIPT), MODULE.rel(MODULE.SIGNOFF)
    flag = '--skip-worktree' if case.startswith('skip_worktree') else '--assume-unchanged'
    if case == 'rm_cached_generated':
        git_ok('rm', '--cached', '-q', '--', matrix); commit('drop')
        want = re.escape(matrix) + ': not committed at HEAD'
    elif case.endswith('_authority_edit'):
        git_ok('update-index', flag, '--', auth)
        MODULE.AUTHORITY.write_bytes(MODULE.AUTHORITY.read_bytes() + b' ')
        want = re.escape(auth) + ': working tree differs from HEAD'
    elif case.endswith('_script_edit'):
        git_ok('update-index', flag, '--', script)
        MODULE.write_text(MODULE.SCRIPT, 'print(2)\n')
        want = re.escape(script) + ': working tree differs from HEAD'
    elif case.endswith('_flag_only'):
        git_ok('update-index', flag, '--', auth)
        want = 'index flags hide working-tree state'
    elif case == 'untracked_with_show_untracked_no':
        git_ok('config', 'status.showUntrackedFiles', 'no')
        git_ok('rm', '--cached', '-q', '--', signoff); commit('untrack')
        want = re.escape(signoff) + ': not committed at HEAD'
        assert REAL_GIT_DIRTY([signoff]) == [f'?? {signoff}']
    else:
        MODULE.write_text(MODULE.OUT / 'extra.json', '{}\n')
        want = 'at-pin: git status'
    assert legacy_status(run) == ''
    with pytest.raises(AuthorityError, match=want) as e:
        MODULE.validate_published(True)
    if case == 'ignored_extra_in_out': assert f'!! {MODULE.rel(MODULE.OUT)}/extra.json' in str(e.value)

def test_real_layout_plain_validate_binds_working_tree_to_head(env, monkeypatch):
    def run(*args): return subprocess.run(['git', *args], cwd=MODULE.ROOT, capture_output=True)
    def commit(msg):
        r = run('commit', '-q', '-m', msg)
        if r.returncode != 0: pytest.fail(f"git commit failed in temp repo {MODULE.ROOT}: {r.stderr.decode('utf-8', 'replace')}", pytrace=False)
        return run('rev-parse', 'HEAD').stdout.decode().strip()
    require_history(ROOT)
    r = run('init', '-q')
    if r.returncode != 0: pytest.fail(f"git init failed in temp repo {MODULE.ROOT}: {r.stderr.decode('utf-8', 'replace')}", pytrace=False)
    run('config', 'user.email', 't@example.com'); run('config', 'user.name', 't'); run('config', 'commit.gpgsign', 'false'); run('config', 'core.autocrlf', 'false')
    (MODULE.ROOT / '.gitignore').write_text('generated/\n', encoding='utf-8')
    use_real_git_state(monkeypatch)
    published(env)
    matrix_file = MODULE.OUT / MODULE.N_MATRIX
    good = matrix_file.read_bytes()
    # commit stale generated bytes, then restore the correct bytes on disk: pub equals HEAD, both stale
    matrix_file.write_bytes(good + b' ')
    run('add', '-A')
    run('add', '-f', '--', MODULE.rel(MODULE.OUT))
    c1 = commit('publish')
    matrix_file.write_bytes(good)
    MODULE.write_publication_record(c1)
    run('add', '--', MODULE.rel(MODULE.PUBLICATION_RECORD))
    commit('record')
    matrix = f'{MODULE.rel(MODULE.OUT)}/{MODULE.N_MATRIX}'
    with pytest.raises(AuthorityError, match=re.escape(matrix) + ': working tree differs from HEAD'):
        MODULE.validate_published()

def test_cli_at_pin_requires_validate(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['x', '--at-pin'])
    with pytest.raises(SystemExit):
        MODULE.main()

REMOVED_FLAG = '--pre' + '-publication'  # built so a source grep for the removed flag finds nothing

def test_cli_pre_publication_flag_is_removed(monkeypatch):
    seen = []
    monkeypatch.setattr(MODULE, 'validate_published', lambda at_pin=False: seen.append(at_pin))
    monkeypatch.setattr(sys, 'argv', ['x', '--validate', REMOVED_FLAG])
    with pytest.raises(SystemExit):
        MODULE.main()
    assert seen == []
    src = inspect.getsource(MODULE)
    assert REMOVED_FLAG[2:] not in src and REMOVED_FLAG[2:].replace('-', '_') not in src

def test_cli_validate_at_pin_passes_true(monkeypatch):
    seen = []
    monkeypatch.setattr(MODULE, 'validate_published', lambda at_pin=False: seen.append(at_pin))
    monkeypatch.setattr(sys, 'argv', ['x', '--validate', '--at-pin'])
    MODULE.main()
    monkeypatch.setattr(sys, 'argv', ['x', '--validate'])
    MODULE.main()
    assert seen == [True, False]

@pytest.mark.parametrize('bad', ['/etc/passwd', 'C:\\Windows\\x', '../outside.txt', 'a/../../b'])
def test_validate_rejects_manifest_path_traversal(env, bad):
    published(env)
    p = MODULE.OUT / MODULE.N_MANIFEST
    m = json.loads(p.read_text(encoding='utf-8'))
    m['artifacts'][0]['relative_path'] = bad
    MODULE.dump(p, m)
    with pytest.raises(AuthorityError):
        MODULE.validate_published()

REAL_AUTHORITY = MODULE.AUTHORITY
REAL_RECORD = MODULE.PUBLICATION_RECORD
REAL_OUT = MODULE.OUT
REAL_SIGNOFF = MODULE.SIGNOFF

def test_real_published_files_validate():
    assert REAL_AUTHORITY.exists(), f'{REAL_AUTHORITY} must be committed'
    MODULE.validate_published()
    a = MODULE.load(REAL_AUTHORITY)
    assert sum(c['not_applicable_decision_state'] != 'NOT_YET_DECIDED' for c in a['controls']) == 21
    assert sum(c['not_applicable_decision_state'] == 'NOT_YET_DECIDED' for c in a['controls']) == 59
    ids = {r['decision_id'] for r in MODULE.load(MODULE.GOVERNANCE_DECISIONS)['records']}
    assert set(a['applicability_decision_ids']) <= ids
    for c in a['controls']:
        if c['not_applicable_rule']:
            for cond in c['not_applicable_rule']['conditions']:
                assert cond['field'] in ('production', 'internet_exposed', 'contains_customer_data', 'ai_enabled') and cond['state'] in ('KNOWN_TRUE', 'KNOWN_FALSE')

def test_publisher_still_valid_and_digest_matches_manifest():
    # Moved from the reply tests (11-01): this checks the live publisher, not the frozen reply.
    MODULE.validate_published()
    manifest = MODULE.load(MODULE.OUT / MODULE.N_MANIFEST)
    assert manifest['publisher_script']['relative_path'] == MODULE.rel(MODULE.SCRIPT)
    assert MODULE.lf_digest(MODULE.SCRIPT) == manifest['publisher_script']['sha256']

def git(*args):
    r = subprocess.run(['git', *args], cwd=ROOT, capture_output=True)
    return subprocess.CompletedProcess(r.args, r.returncode, r.stdout, r.stderr.decode('utf-8', 'replace').strip())

def lf_sha(b): return hashlib.sha256(b.replace(b'\r\n', b'\n')).hexdigest()

def test_publication_commit_ancestor_and_file_set():
    assert REAL_RECORD.exists(), f'{REAL_RECORD} must be committed'
    require_history(ROOT, commits=(MODULE.load(REAL_RECORD)['publication_commit'],))
    rec = MODULE.load(REAL_RECORD)
    sha = rec['publication_commit']
    assert git('merge-base', '--is-ancestor', sha, 'HEAD').returncode == 0
    files = git('diff-tree', '--no-commit-id', '--name-only', '-r', sha).stdout.decode().split()
    out_rel = REAL_OUT.relative_to(ROOT).as_posix()
    expected = {REAL_AUTHORITY.relative_to(ROOT).as_posix(), 'schemas/archive_assessment_applicability_authority_v2.schema.json', REAL_SIGNOFF.relative_to(ROOT).as_posix(), *(f'{out_rel}/{p.name}' for p in REAL_OUT.iterdir())}
    # Outputs byte-identical to the previous version are not re-committed, so the commit may hold a subset of the expected set.
    auth_rel = REAL_AUTHORITY.relative_to(ROOT).as_posix()
    signoff_rel = REAL_SIGNOFF.relative_to(ROOT).as_posix()
    assert set(files) <= expected
    assert {auth_rel, signoff_rel, f'{out_rel}/{MODULE.N_MANIFEST}'} <= set(files)
    present = set(git('ls-tree', '-r', '--name-only', sha, '--', *sorted(expected)).stdout.decode().split())
    assert present == expected
    assert 'registry/adjudication_rules.json' not in files and 'registry/policy_decisions.json' not in files
    assert lf_sha(git('show', f'{sha}:{auth_rel}').stdout) == rec['authority_sha256']
    manifest = json.loads(git('show', f'{sha}:{out_rel}/{MODULE.N_MANIFEST}').stdout.decode('utf-8'))
    for art in manifest['artifacts']:
        assert lf_sha(git('show', f"{sha}:{art['relative_path']}").stdout) == art['sha256']


def test_manifest_publisher_script_digest_matches_publication_commit():
    assert REAL_RECORD.exists(), f'{REAL_RECORD} must be committed'
    require_history(ROOT, commits=(MODULE.load(REAL_RECORD)['publication_commit'],))
    sha = MODULE.load(REAL_RECORD)['publication_commit']
    manifest = MODULE.load(REAL_OUT / MODULE.N_MANIFEST)
    script_rel = MODULE.SCRIPT.relative_to(ROOT).as_posix()
    shown = git('show', f'{sha}:{script_rel}')
    assert shown.returncode == 0
    assert manifest['publisher_script']['sha256'] == lf_sha(shown.stdout)


# ---- 06-05: lineage constants, D-13, dry-run, script digest, executed mutations ----

PREVIOUS_17 = ['swapped_authority', 'rule_field_change', 'rule_state_unknown', 'rule_unused_field', 'rule_state_flip', 'decided_flipped_to_not_yet_decided', 'twenty_second_control_decided', 'v1_field_change_on_undecided_row', 'extra_field_on_decided_row', 'authority_removed_from_id_list', 'authority_cited_twice', 'duplicate_id_in_list', 'altered_governance_digest', 'altered_record_count_or_drafting_commit', 'missing_governance_lineage', 'wrong_v1_lineage', 'superseded_record_cited']
NEW_9 = ['signoff_role_hayes_developer', 'signoff_invalid_date', 'signoff_dual_role_text_appended', 'signoff_extra_keys', 'decision_record_tampered_approver', 'decision_record_empty_dual_role_statement', 'decision_record_bogus_disposition', 'rule_same_field_twice_opposite_states', 'supersedes_governance_digest_differs']

PUBLISHER_REL = 'scripts/publish_archive_assessment_applicability_authority_v2.py'

def publisher_at(commit):
    r = git('show', f'{commit}:{PUBLISHER_REL}')
    if r.returncode != 0: pytest.fail(f'cannot read {PUBLISHER_REL} at {commit}: {r.stderr}; fetch full history (git fetch --unshallow)', pytrace=False)
    name = f'aa_publisher_at_{commit[:7]}'
    m = types.ModuleType(name)
    m.__file__ = str(SCRIPT)
    sys.modules[name] = m
    try:
        exec(compile(r.stdout.decode('utf-8'), f'publisher@{commit}', 'exec'), m.__dict__)
    finally:
        sys.modules.pop(name, None)
    return m

def test_2_0_0_anchor_matches_frozen_2_0_1_publisher_and_chain():
    require_history(ROOT, commits=('54a7fd09114704a97a7a48fce5f89aebeb48c90a', MODULE.V1_BASELINE_COMMIT, '31addfa95ffc5c2d6805c73fa1f34d6ccbe313eb', 'ae15c7458e49c8f55cc58c61bab04bc716aa9892'))
    sup = {'authority_id': 'EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.0', 'version': '2.0.0', 'commit': '54a7fd09114704a97a7a48fce5f89aebeb48c90a', 'relative_path': 'registry/archive_assessment_applicability_authority_v2.json', 'sha256': 'de36e227be4ccc95f4a8a8a08247cf6e49f7682908c7f425f8cc02bbaa1da353', 'governance_decisions_sha256': '4e746d1f2c9ffc36d93bead5742db3fa41b22abb11c499dc4cef823a023f081f'}
    auth_bytes = git('show', '54a7fd0:registry/archive_assessment_applicability_authority_v2.json').stdout
    dec_bytes = git('show', '54a7fd0:registry/archive_assessment_governance_decisions.json').stdout
    old = json.loads(auth_bytes.decode('utf-8'))
    assert sup['authority_id'] == old['authority_id'] and sup['version'] == old['version']
    assert sup['sha256'] == lf_sha(auth_bytes) and sup['governance_decisions_sha256'] == lf_sha(dec_bytes)
    rec = json.loads(git('show', '0ce89f2:registry/archive_assessment_applicability_authority_v2_publication_record.json').stdout.decode('utf-8'))
    assert sup['commit'] == rec['publication_commit'] and sup['sha256'] == rec['authority_sha256']
    assert git('rev-parse', '54a7fd0').stdout.decode().strip() == sup['commit']
    assert git('rev-parse', '62a8955').stdout.decode().strip() == MODULE.V1_BASELINE_COMMIT
    assert git('show', f"{sup['commit']}:{sup['relative_path']}").stdout == auth_bytes
    assert publisher_at('31addfa95ffc5c2d6805c73fa1f34d6ccbe313eb').SUPERSEDED_V2_0_0 == sup
    auth_201 = json.loads(git('show', '31addfa95ffc5c2d6805c73fa1f34d6ccbe313eb:registry/archive_assessment_applicability_authority_v2.json').stdout.decode('utf-8'))
    assert auth_201['version'] == '2.0.1' and auth_201['source_lineage']['supersedes'] == sup
    auth_202 = json.loads(git('show', 'ae15c7458e49c8f55cc58c61bab04bc716aa9892:registry/archive_assessment_applicability_authority_v2.json').stdout.decode('utf-8'))
    blob_201 = git('show', '31addfa95ffc5c2d6805c73fa1f34d6ccbe313eb:registry/archive_assessment_applicability_authority_v2.json').stdout
    sup_202 = auth_202['source_lineage']['supersedes']
    assert auth_202['version'] == '2.0.2' and sup_202['commit'] == '31addfa95ffc5c2d6805c73fa1f34d6ccbe313eb' and sup_202['version'] == '2.0.1'
    assert sup_202['sha256'] == lf_sha(blob_201)
    assert git('rev-parse', 'ae15c74').stdout.decode().strip() == MODULE.SUPERSEDED_V2_0_2['commit']

def test_superseded_v2_0_2_constants_match_git_history():
    require_history(ROOT, commits=('ae15c7458e49c8f55cc58c61bab04bc716aa9892', 'a71257ed267410138a3c4daba412b00c116663d8'))
    sup = MODULE.SUPERSEDED_V2_0_2
    assert sup['commit'] == 'ae15c7458e49c8f55cc58c61bab04bc716aa9892'
    auth_bytes = git('show', f"ae15c7458e49c8f55cc58c61bab04bc716aa9892:{sup['relative_path']}").stdout
    dec_bytes = git('show', f"ae15c7458e49c8f55cc58c61bab04bc716aa9892:{sup['governance_decisions_relative_path']}").stdout
    old = json.loads(auth_bytes.decode('utf-8'))
    assert sup['authority_id'] == old['authority_id'] and sup['version'] == old['version'] == '2.0.2'
    assert sup['sha256'] == lf_sha(auth_bytes) and sup['governance_decisions_sha256'] == lf_sha(dec_bytes) == '4e746d1f2c9ffc36d93bead5742db3fa41b22abb11c499dc4cef823a023f081f'
    rec = json.loads(git('show', 'a71257ed267410138a3c4daba412b00c116663d8:registry/archive_assessment_applicability_authority_v2_publication_record.json').stdout.decode('utf-8'))
    assert sup['commit'] == rec['publication_commit'] and sup['sha256'] == rec['authority_sha256']
    assert rec['authority_id'] == sup['authority_id'] and rec['version'] == sup['version']
    assert git('rev-parse', 'ae15c74').stdout.decode().strip() == sup['commit']

def superseded_2_0_1_identity():
    # the frozen 2.0.1 identity, as the 2.0.2 publication at ae15c74 recorded it in source_lineage.supersedes
    require_history(ROOT, commits=('ae15c7458e49c8f55cc58c61bab04bc716aa9892', '31addfa95ffc5c2d6805c73fa1f34d6ccbe313eb'))
    return json.loads(git('show', 'ae15c7458e49c8f55cc58c61bab04bc716aa9892:registry/archive_assessment_applicability_authority_v2.json').stdout.decode('utf-8'))['source_lineage']['supersedes']

def test_validate_signoff_accepts_frozen_2_0_1_signoff_with_explicit_identity():
    sup = superseded_2_0_1_identity()
    assert sup['version'] == '2.0.1' and sup['commit'] == '31addfa95ffc5c2d6805c73fa1f34d6ccbe313eb'
    record = json.loads(git('show', f"{sup['commit']}:registry/archive_assessment_applicability_authority_v2_signoff.json").stdout.decode('utf-8'))
    MODULE.validate_signoff(record, sup['sha256'], sup['authority_id'], sup['version'])
    with pytest.raises(AuthorityError):
        MODULE.validate_signoff(record, sup['sha256'])
    with pytest.raises(AuthorityError, match='authority_id'):
        MODULE.validate_signoff(record, sup['sha256'], 'EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-9.9.9', sup['version'])
    live = dict(record, authority_id=MODULE.AUTHORITY_ID, version=MODULE.VERSION)
    MODULE.validate_signoff(live, sup['sha256'])

def test_rows_equal_2_0_0_rows_and_only_identity_and_lineage_differ():
    require_history(ROOT, commits=('54a7fd09114704a97a7a48fce5f89aebeb48c90a',))
    old = json.loads(git('show', '54a7fd0:registry/archive_assessment_applicability_authority_v2.json').stdout.decode('utf-8'))
    new = build()
    assert len(old['controls']) == len(new['controls']) == 80
    assert old['controls'] == new['controls']
    differing = {k for k in set(old) | set(new) if old.get(k) != new.get(k)}
    assert differing <= {'authority_id', 'version', 'source_lineage'}
    ol, nl = old['source_lineage'], new['source_lineage']
    assert nl['aa1_manifest']['sha256'] == ol['aa1_manifest_sha256']
    assert nl['aa2_closure']['sha256'] == ol['aa2_closure_sha256']
    assert nl['aa2_approval']['sha256'] == ol['aa2_approval_sha256']

def test_version_constants_and_published_on_removed():
    assert MODULE.VERSION == '2.0.3' and MODULE.AUTHORITY_ID.endswith('-2.0.3')
    assert not hasattr(MODULE, 'PUBLISHED_ON')

def test_build_all_outputs_requires_signoff_and_uses_its_date(env):
    with pytest.raises((TypeError, AuthorityError)):
        MODULE.build_all_outputs(build())
    one, two = outputs(on='2026-10-14'), outputs(on='2026-11-02')
    assert set(one) == set(two)
    for n in (MODULE.N_MATRIX, MODULE.N_SEMANTIC, MODULE.N_NEGATIVE, MODULE.N_TRACE, MODULE.N_CERT, MODULE.N_REPORT, MODULE.N_MANIFEST):
        assert '2026-11-02' in two[n] and '2026-10-14' not in two[n]
        assert '2026-10-14' in one[n]

def test_manifest_records_publisher_script(env):
    published(env)
    m = MODULE.load(MODULE.OUT / MODULE.N_MANIFEST)
    ps = m['publisher_script']
    assert ps == {'relative_path': MODULE.rel(MODULE.SCRIPT), 'sha256': MODULE.lf_digest(MODULE.SCRIPT), 'sha256_normalisation': 'CRLF_TO_LF'}
    assert all(a['relative_path'] != ps['relative_path'] for a in m['artifacts'])
    assert {a['relative_path'] for a in m['artifacts']} >= {MODULE.rel(MODULE.SCHEMA), MODULE.rel(MODULE.AUTHORITY), MODULE.rel(MODULE.SIGNOFF)}

SCRIPT_DIGEST_MSG = 'publisher script differs from the certified manifest digest'

def test_script_edit_after_publication_fails_validate(env, fake_git_show, capsys):
    published_recorded(env, fake_git_show)
    MODULE.validate_published()
    # D-07: a later publisher edit, even a comment, turns plain --validate red until a certified republication
    MODULE.write_text(MODULE.SCRIPT, 'print(1)  # comment\n')
    with pytest.raises(AuthorityError, match=SCRIPT_DIGEST_MSG):
        MODULE.validate_published()
    # D-08: at the pin the live script check is not deferred
    s = authority_supersedes()
    superseded_record(fake_git_show)
    fake_git_show[(s['commit'], MODULE.rel(MODULE.AUTHORITY))] = superseded_authority_blob(s)
    with pytest.raises(AuthorityError, match=SCRIPT_DIGEST_MSG):
        MODULE.validate_published(True)
    MODULE.write_text(MODULE.SCRIPT, 'print(1)\n')
    capsys.readouterr()
    MODULE.validate_published(True)
    assert json.loads(capsys.readouterr().out)['status'] == 'PASS'

def test_pinned_script_digest_mismatch_fails_plain_validate(env, fake_git_show):
    published_recorded(env, fake_git_show)
    script_rel = MODULE.rel(MODULE.SCRIPT)
    # CRLF in the pinned blob is normalised away
    fake_git_show[(RECORD_COMMIT, script_rel)] = b'print(1)\r\n'
    MODULE.validate_published()
    fake_git_show[(RECORD_COMMIT, script_rel)] = b'print(3)\n'
    with pytest.raises(AuthorityError, match='publisher script at the publication commit differs from the certified manifest digest'):
        MODULE.validate_published()

def test_validate_rejects_missing_publisher_script_entry(env):
    published(env)
    p = MODULE.OUT / MODULE.N_MANIFEST
    m = json.loads(p.read_text(encoding='utf-8')); m.pop('publisher_script')
    MODULE.dump(p, m)
    with pytest.raises(AuthorityError):
        MODULE.validate_published()

def test_dry_run_summary_lists_decisions_rules_and_supersession(env, capsys):
    MODULE.publish(True)
    out = capsys.readouterr().out
    for r in build()['controls']:
        if r['not_applicable_decision_state'] != 'NOT_YET_DECIDED':
            assert f"{r['control_id']}  {r['not_applicable_authority']}  {r['not_applicable_decision_state']}" in out
    assert 'EMS-CTRL-039: ALL_CONDITIONS_MUST_MATCH: production = KNOWN_FALSE' in out
    assert 'Published on' not in out and 'PUBLISHED_ON' not in out
    sup = MODULE.SUPERSEDED_V2_0_2
    assert f"supersedes {sup['authority_id']} version 2.0.2 (commit ae15c74). No decision changed" in out
    assert f"{sup['governance_decisions_sha256']} equals the 2.0.2 value" in out
    for word in ('best', 'critical', 'important', 'recommended', 'highest'): assert word not in out.lower()
    assert 'What changed in 2.0.3' in out
    for label, e in build()['source_lineage'].items():
        if isinstance(e, dict) and 'relative_path' in e: assert f"lineage {label}: {e['relative_path']} ({e['normalisation']})" in out
    assert 'lineage aa1_manifest: ' in out and '(RAW_BYTES)' in out
    assert f'negative mutations: {len(MODULE.NEGATIVE_MUTATIONS)}' in out
    levels = MODULE.closed_schema_levels(MODULE.schema())
    assert levels and f'additionalProperties false: {len(levels)} (' in out
    assert 'row comparison 2.0.2 -> 2.0.3: 80 controls identical to 2.0.2' in out
    assert 'GATE-01 to GATE-10' in out and 'publisher-script digest checked by --validate' in out
    assert 'pre-publication' not in out
    assert 'Decided controls: 21' in out and 'Undecided controls: 59' in out

def test_mutation_records_shape():
    ids = [m.id for m in MODULE.NEGATIVE_MUTATIONS]
    assert len(ids) == 29 and len(set(ids)) == 29
    assert ids[:17] == PREVIOUS_17 and set(ids[17:26]) == set(NEW_9)
    assert ids[26:] == ['extra_top_level_field', 'extra_field_on_undecided_row', 'extra_field_in_semantics']
    assert all(m.description and m.target in ('AUTHORITY', 'SIGNOFF', 'DECISIONS') for m in MODULE.NEGATIVE_MUTATIONS)
    assert next(m for m in MODULE.NEGATIVE_MUTATIONS if m.id == 'missing_governance_lineage').schema_must_reject

def mutation_inputs():
    a = build(); ash = sha_text(MODULE.jtext(a))
    return {'AUTHORITY': a, 'SIGNOFF': valid_signoff(ash), 'DECISIONS': MODULE.load(MODULE.GOVERNANCE_DECISIONS)}, ash

@pytest.mark.parametrize('m', MODULE.NEGATIVE_MUTATIONS, ids=lambda m: m.id)
def test_each_mutation_is_rejected_by_its_gates(m):
    docs, ash = mutation_inputs()
    doc = copy.deepcopy(docs[m.target]); m.apply(doc)
    assert doc != docs[m.target]
    gates = MODULE.mutation_gates(m.target, doc, ash)
    assert gates
    if m.schema_must_reject: assert 'SCHEMA' in gates
    if m.target == 'SIGNOFF': assert gates == ['PYTHON_VALIDATOR']
    if m.target == 'DECISIONS': assert gates == ['PYTHON_VALIDATOR', 'SCHEMA']
    if m.id == 'rule_same_field_twice_opposite_states': assert gates == ['PYTHON_VALIDATOR', 'SCHEMA']
    if m.id == 'supersedes_governance_digest_differs': assert gates == ['PYTHON_VALIDATOR']

NEW_SCHEMA_07 = ['extra_top_level_field', 'extra_field_on_undecided_row', 'extra_field_in_semantics']

@pytest.mark.parametrize('mid', NEW_SCHEMA_07)
def test_schema_07_mutations_rejected_by_schema(mid):
    docs, ash = mutation_inputs()
    m = next(x for x in MODULE.NEGATIVE_MUTATIONS if x.id == mid)
    doc = copy.deepcopy(docs['AUTHORITY']); m.apply(doc)
    gates = MODULE.mutation_gates('AUTHORITY', doc, ash)
    assert 'SCHEMA' in gates
    if mid == 'extra_top_level_field': assert gates == ['SCHEMA']

@pytest.mark.parametrize('exc', [KeyError, TypeError, AttributeError])
@pytest.mark.parametrize('target,name', [('AUTHORITY', 'validate_publication'), ('SIGNOFF', 'validate_signoff'), ('DECISIONS', 'validate_decisions')])
def test_non_domain_exceptions_propagate_from_mutation_gates(monkeypatch, exc, target, name):
    docs, ash = mutation_inputs()
    def boom(*args, **kwargs): raise exc('crash')
    owner = MODULE.decisions_builder() if name == 'validate_decisions' else MODULE
    monkeypatch.setattr(owner, name, boom)
    with pytest.raises(exc):
        MODULE.mutation_gates(target, docs[target], ash)

def test_git_history_error_is_an_authority_error_subclass():
    assert issubclass(MODULE.GitHistoryError, AuthorityError)

def test_git_history_error_propagates_from_authority_gate(monkeypatch):
    docs, ash = mutation_inputs()
    def boom(commit, path): raise MODULE.GitHistoryError(f'{path}@{commit[:7]}: git show failed: shallow clone')
    monkeypatch.setattr(MODULE, 'git_show', boom)
    with pytest.raises(MODULE.GitHistoryError):
        MODULE.mutation_gates('AUTHORITY', docs['AUTHORITY'], ash)

def test_git_show_unknown_object_raises_git_history_error():
    with pytest.raises(MODULE.GitHistoryError, match='git show failed'):
        MODULE.git_show('f' * 40, MODULE.CATALOG_REL)

def test_plain_value_error_propagates_from_decisions_gate(monkeypatch):
    docs, ash = mutation_inputs()
    def boom(*args, **kwargs): raise ValueError('not a domain error')
    monkeypatch.setattr(MODULE.decisions_builder(), 'validate_decisions', boom)
    with pytest.raises(ValueError, match='not a domain error'):
        MODULE.mutation_gates('DECISIONS', docs['DECISIONS'], ash)

def test_non_domain_exception_aborts_publish_and_writes_nothing(env, monkeypatch):
    def boom(*args, **kwargs): raise KeyError('crash')
    monkeypatch.setattr(MODULE, 'validate_publication', boom)
    write_signoff()
    with pytest.raises(KeyError):
        MODULE.publish(False)
    assert not MODULE.AUTHORITY.exists() and not MODULE.OUT.exists()

@pytest.mark.parametrize('m', MODULE.NEGATIVE_MUTATIONS, ids=lambda m: m.id)
def test_python_validators_raise_only_domain_errors(m):
    docs, ash = mutation_inputs()
    doc = copy.deepcopy(docs[m.target]); m.apply(doc)
    domain = ValueError if m.target == 'DECISIONS' else AuthorityError
    try:
        if m.target == 'AUTHORITY': MODULE.validate_publication(doc)
        elif m.target == 'SIGNOFF': MODULE.validate_signoff(doc, ash)
        else: MODULE.decisions_builder().validate_decisions(doc)
    except domain:
        pass
    except (KeyError, TypeError, AttributeError) as e:
        pytest.fail(f'{m.id}: validator crashed with {type(e).__name__}')

MALFORMED_SHAPES = {
    'classification_vocabulary_is_a_list': lambda a: a.__setitem__('classification_vocabulary', ['KNOWN_TRUE']),
    'control_row_is_a_string': lambda a: a['controls'].__setitem__(0, 'EMS-CTRL-001'),
    'controls_is_an_object': lambda a: a.__setitem__('controls', {'EMS-CTRL-001': {}}),
    'control_id_is_a_list': lambda a: a['controls'][0].__setitem__('control_id', ['EMS-CTRL-001']),
    'evidence_boundary_is_a_string': lambda a: a.__setitem__('evidence_boundary', 'none'),
    'evidence_boundary_list_holds_objects': lambda a: a['evidence_boundary'].__setitem__('archive_content_does_not_establish', [{'x': 1}]),
    'attestation_prohibitions_is_a_list': lambda a: a.__setitem__('attestation_prohibitions', []),
    'dependencies_holds_a_string': lambda a: a.__setitem__('dependencies', ['x']),
    'applicability_decision_ids_holds_an_object': lambda a: a['applicability_decision_ids'].__setitem__(0, {'id': 'AA4-GOV-001'}),
}

@pytest.mark.parametrize('name', sorted(MALFORMED_SHAPES))
def test_malformed_authority_shapes_raise_domain_error(name):
    a = copy.deepcopy(build()); MALFORMED_SHAPES[name](a)
    with pytest.raises(AuthorityError):
        validate_publication(a)

@pytest.mark.parametrize('value', [[], 'text', 7, None])
def test_non_object_authority_raises_domain_error(value):
    with pytest.raises(AuthorityError, match='authority must be an object'):
        validate_publication(value)

def test_run_mutations_outcomes_shape():
    docs, _ = mutation_inputs()
    out = MODULE.run_mutations(docs['AUTHORITY'], docs['SIGNOFF'], docs['DECISIONS'])
    assert [o['id'] for o in out] == [m.id for m in MODULE.NEGATIVE_MUTATIONS]
    for o in out:
        assert o['mutation'] == o['id'] and o['description'] and o['result'] == 'REJECTED_FAIL_CLOSED'
        assert o['rejected_by'] and set(o['rejected_by']) <= {'SCHEMA', 'PYTHON_VALIDATOR'} and o['rejected_by'] == sorted(o['rejected_by'])

def test_accepted_mutation_aborts_build_and_writes_nothing(env, monkeypatch):
    noop = [MODULE.NEGATIVE_MUTATIONS[0]._replace(apply=lambda d: None)] + list(MODULE.NEGATIVE_MUTATIONS[1:])
    monkeypatch.setattr(MODULE, 'NEGATIVE_MUTATIONS', noop)
    write_signoff()
    with pytest.raises(AuthorityError, match='was accepted'):
        MODULE.publish(False)
    assert not MODULE.AUTHORITY.exists() and not MODULE.OUT.exists()

def test_schema_must_reject_violation_aborts(env, monkeypatch):
    weak = [m._replace(schema_must_reject=True) if m.id == 'swapped_authority' else m for m in MODULE.NEGATIVE_MUTATIONS]
    monkeypatch.setattr(MODULE, 'NEGATIVE_MUTATIONS', weak)
    write_signoff()
    with pytest.raises(AuthorityError, match='schema'):
        MODULE.publish(False)
    assert not MODULE.AUTHORITY.exists()

def test_unknown_resolving_to_not_applicable_aborts_build(env, monkeypatch):
    monkeypatch.setattr(MODULE, 'resolve_applicability', lambda control, facts: 'NOT_APPLICABLE')
    write_signoff()
    with pytest.raises(AuthorityError, match='semantic conflicts'):
        MODULE.publish(False)
    assert not MODULE.AUTHORITY.exists() and not MODULE.OUT.exists()

def test_semantic_conflicts_cover_all_80_rows_and_are_empty():
    a = build()
    assert len(a['controls']) == 80 and MODULE.semantic_conflicts(a['controls']) == []
    bad = copy.deepcopy(a['controls']); bad[0]['not_applicable_decision_state'] = 'MAYBE'
    assert MODULE.semantic_conflicts(bad)

def test_certification_and_semantic_files_are_derived(env):
    outs = outputs()
    cert, sem, neg = (json.loads(outs[n]) for n in (MODULE.N_CERT, MODULE.N_SEMANTIC, MODULE.N_NEGATIVE))
    assert cert['semantic_conflicts'] == sem['semantic_conflict_count'] == 0 and sem['controls_checked'] == 80
    assert cert['negative_invariants'] == neg['result'] == 'PASS'
    assert len(neg['negative_invariant_tests']) == 29
    assert cert['prohibitions'] == {'evaluator_executions': 0, 'hayes_modifications': 0, 'target_comparisons': 0}

def test_publisher_source_runs_no_subprocess_or_evaluator():
    src = source_without_git_show()
    for banned in ('subprocess', 'os.system', 'Evaluate-', 'Popen'): assert banned not in src
    assert 'subprocess.run' in inspect.getsource(MODULE.git_show)
    assert 'subprocess.run' in inspect.getsource(MODULE.git_run)

def test_published_negative_file_equals_observed_outcomes(env):
    published(env)
    a = MODULE.load(MODULE.AUTHORITY)
    observed = MODULE.run_mutations(a, MODULE.load(MODULE.SIGNOFF), MODULE.load(MODULE.GOVERNANCE_DECISIONS))
    neg = MODULE.load(MODULE.OUT / MODULE.N_NEGATIVE)
    assert neg['negative_invariant_tests'] == observed

@pytest.mark.parametrize('field,value', [('commit', '0' * 40), ('relative_path', 'registry/other.yaml'), ('sha256', '0' * 64)])
def test_catalog_reference_tamper_fails_validation(env, field, value):
    a = copy.deepcopy(build())
    a['source_lineage']['catalog_reference'][field] = value
    with pytest.raises(AuthorityError):
        validate_publication(a)

def test_catalog_reference_commit_change_fails_schema(env):
    a = copy.deepcopy(build())
    a['source_lineage']['catalog_reference']['commit'] = 'a' * 40
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(MODULE.schema()).validate(a)

def test_catalog_reference_commit_missing_fails_schema_and_validation(env):
    a = copy.deepcopy(build())
    del a['source_lineage']['catalog_reference']['commit']
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(MODULE.schema()).validate(a)
    with pytest.raises(AuthorityError):
        validate_publication(a)

def test_catalog_commit_is_v1_baseline_and_in_commit_pinned():
    assert MODULE.CATALOG_COMMIT == '62a8955dc28d9458cd1167fad314926e057c31fc' == MODULE.V1_BASELINE_COMMIT
    assert 'catalog_reference' in MODULE.COMMIT_PINNED
    assert not hasattr(MODULE, 'CATALOG')


# ---- 09-01 Task 2b: D-08 comparison with the superseded publication (2.0.2 since 12-07), D-04 byte identity ----

DECISION_FIELDS = ('not_applicable_decision_state', 'not_applicable_rule', 'not_applicable_authority', 'decision_ids')

def prev_superseded_rows():
    return {c['control_id']: c for c in json.loads(prev_superseded_authority_bytes().decode('utf-8'))['controls']}

def test_built_rows_equal_superseded_rows_on_the_four_decision_fields():
    a = build(); prev = prev_superseded_rows()
    assert len(a['controls']) == 80 and set(prev) == {c['control_id'] for c in a['controls']}
    for c in a['controls']:
        assert all(c[k] == prev[c['control_id']][k] for k in DECISION_FIELDS), c['control_id']
    assert a['applicability_decision_ids'] == json.loads(prev_superseded_authority_bytes().decode('utf-8'))['applicability_decision_ids']
    MODULE.validate_publication(a)

def tamper_state(c): c['not_applicable_decision_state'] = 'NO_RULE_WILL_BE_PUBLISHED' if c['not_applicable_decision_state'] != 'NO_RULE_WILL_BE_PUBLISHED' else 'NOT_YET_DECIDED'
def tamper_rule(c): c['not_applicable_rule'] = None if c['not_applicable_rule'] else {'combination': 'ALL_CONDITIONS_MUST_MATCH', 'conditions': [{'field': 'production', 'state': 'KNOWN_FALSE'}]}
def tamper_authority(c): c['not_applicable_authority'] = 'AA4-GOV-999' if c['not_applicable_authority'] != 'AA4-GOV-999' else None
def tamper_decision_ids(c): c['decision_ids'] = c['decision_ids'][:-1]

@pytest.mark.parametrize('cid, state', [('EMS-CTRL-001', 'NOT_YET_DECIDED'), ('EMS-CTRL-009', 'NO_RULE_WILL_BE_PUBLISHED'), ('EMS-CTRL-030', 'RULE_PUBLISHED')])
@pytest.mark.parametrize('tamper', [tamper_state, tamper_rule, tamper_authority, tamper_decision_ids], ids=lambda f: f.__name__)
def test_row_tamper_against_superseded_raises_authority_error(monkeypatch, tamper, cid, state):
    a = build(); r = row(a, cid)
    assert r['not_applicable_decision_state'] == state
    before = copy.deepcopy(r); tamper(r)
    assert r != before, f'{tamper.__name__} is a no-op on {cid}'
    with pytest.raises(AuthorityError):
        MODULE.validate_publication(a)
    # isolate the D-08 comparison from the earlier checks
    monkeypatch.setattr(MODULE, 'validate_authority', lambda *args, **kwargs: None)
    with pytest.raises(AuthorityError, match=f'{cid}: decision content differs from'):
        MODULE.validate_publication(a)

def test_applicability_decision_ids_tamper_against_superseded_raises_authority_error(monkeypatch):
    a = build(); a['applicability_decision_ids'] = a['applicability_decision_ids'][:-1]
    monkeypatch.setattr(MODULE, 'validate_authority', lambda *args, **kwargs: None)
    with pytest.raises(AuthorityError, match=re.escape(f"decision set differs from {MODULE.SUPERSEDED_V2_0_2['version']}")):
        MODULE.validate_publication(a)

def test_missing_superseded_history_raises_git_history_error_through_mutation_gates(monkeypatch):
    docs, ash = mutation_inputs()
    def boom(commit, path): raise MODULE.GitHistoryError(f'{path}@{commit[:7]}: git show failed: shallow clone')
    monkeypatch.setattr(MODULE, 'git_show', boom)
    with pytest.raises(MODULE.GitHistoryError):
        MODULE.validate_publication(docs['AUTHORITY'])
    with pytest.raises(MODULE.GitHistoryError):
        MODULE.mutation_gates('AUTHORITY', docs['AUTHORITY'], ash)

def test_publication_files_byte_identical_between_publication_and_record_commit():
    assert REAL_RECORD.exists(), f'{REAL_RECORD} must be committed'
    require_history(ROOT, commits=(MODULE.load(REAL_RECORD)['publication_commit'],))
    pub = MODULE.load(REAL_RECORD)['publication_commit']
    rec_rel = REAL_RECORD.relative_to(ROOT).as_posix()
    paths = MODULE.publication_paths()
    assert len(paths) == 10
    rec_commit = git('log', '-n1', '--format=%H', '--', rec_rel).stdout.decode().strip()
    assert re.fullmatch(r'[0-9a-f]{40}', rec_commit)
    assert git('diff', '--quiet', pub, rec_commit, '--', *paths).returncode == 0
    assert git('diff-tree', '--no-commit-id', '--name-only', '-r', rec_commit).stdout.decode().split() == [rec_rel]
    between = git('diff', '--name-only', pub, f'{rec_commit}^').stdout.decode().split()
    assert all(f.startswith('.planning/') for f in between), between


# ---- 12-04: GATE-07 malformed published files and GATE-10 IN-01 dry-run DIFFER branch ----

def _drop_required_key(p):
    a = MODULE.load(p); del a['evidence_boundary']; MODULE.dump(p, a)

MALFORMED_FILES = {
    'authority_invalid_json': (lambda: MODULE.AUTHORITY, b'{', 'cannot be read as JSON'),
    'signoff_invalid_json': (lambda: MODULE.SIGNOFF, b'{', 'cannot be read as JSON'),
    'manifest_invalid_json': (lambda: MODULE.OUT / MODULE.N_MANIFEST, b'{', 'cannot be read as JSON'),
    'manifest_is_a_list': (lambda: MODULE.OUT / MODULE.N_MANIFEST, b'[]', 'manifest must be an object'),
    'record_invalid_json': (lambda: MODULE.PUBLICATION_RECORD, b'{', 'cannot be read as JSON'),
    'schema_invalid_json': (lambda: MODULE.SCHEMA, b'{', 'cannot be read as JSON'),
    'schema_not_a_valid_schema': (lambda: MODULE.SCHEMA, b'{"type": 7}', 'committed schema is invalid'),
    'authority_missing_required_key': (lambda: MODULE.AUTHORITY, _drop_required_key, 'fails the schema'),
    # 12-06: the --at-pin pointer must not run before the record shape check
    'record_is_a_list': (lambda: MODULE.PUBLICATION_RECORD, b'[]', 'exactly the six'),
}

@pytest.mark.parametrize('name', sorted(MALFORMED_FILES))
def test_malformed_published_files_raise_domain_error(env, fake_git_show, name):
    published_recorded(env, fake_git_show)
    MODULE.validate_published()
    path, corrupt, match = MALFORMED_FILES[name]
    p = path()
    if callable(corrupt): corrupt(p)
    else: p.write_bytes(corrupt)
    with pytest.raises(AuthorityError, match=match):
        MODULE.validate_published()

def test_dry_run_summary_differ_branch_is_reachable(monkeypatch):
    require_history(ROOT, commits=(MODULE.SUPERSEDED_V2_0_2['commit'],))
    a = build()
    tamper_state(row(a, 'EMS-CTRL-030'))
    out = MODULE.dry_run_summary(a)
    assert 'DIFFER' in out and 'No decision changed' not in out
    assert f"DECISIONS DIFFER from {MODULE.SUPERSEDED_V2_0_2['version']}" in out


# ---- 12-05 Task 1: single git seam (git_run and typed helpers), git show --, D-05 publication_paths ----

SHA40 = '0123456789abcdef0123456789abcdef01234567'

def fake_git_run(monkeypatch, rc, stdout=b'', stderr=b''):
    calls = []
    def fake(*args):
        calls.append(args)
        return subprocess.CompletedProcess(['git', *args], rc, stdout, stderr)
    monkeypatch.setattr(MODULE, 'git_run', fake)
    return calls

def test_git_head_returns_sha(monkeypatch):
    calls = fake_git_run(monkeypatch, 0, SHA40.encode() + b'\n')
    assert MODULE.git_head() == SHA40
    assert calls == [('rev-parse', 'HEAD')]

@pytest.mark.parametrize('rc,stdout', [(128, b''), (0, b'not-a-sha\n'), (0, b'ABCDEF' * 7)], ids=['rc128', 'non_hex', 'upper_hex'])
def test_git_head_fails_closed(monkeypatch, rc, stdout):
    fake_git_run(monkeypatch, rc, stdout, b'fatal: not a git repository')
    with pytest.raises(MODULE.GitHistoryError):
        MODULE.git_head()

@pytest.mark.parametrize('rc,want', [(0, True), (1, False)])
def test_git_is_ancestor_maps_rc(monkeypatch, rc, want):
    calls = fake_git_run(monkeypatch, rc)
    assert MODULE.git_is_ancestor(SHA40, 'f' * 40) is want
    assert calls == [('merge-base', '--is-ancestor', SHA40, 'f' * 40)]

def test_git_is_ancestor_other_rc_fails_closed(monkeypatch):
    fake_git_run(monkeypatch, 128, b'', b'fatal: bad object')
    with pytest.raises(MODULE.GitHistoryError, match='bad object'):
        MODULE.git_is_ancestor(SHA40, 'f' * 40)

@pytest.mark.parametrize('a,b', [('HEAD', SHA40), (SHA40, 'HEAD'), (SHA40[:7], SHA40), (SHA40, '--all'), (None, SHA40)])
def test_git_is_ancestor_rejects_non_sha_before_git(monkeypatch, a, b):
    calls = fake_git_run(monkeypatch, 0)
    with pytest.raises(AuthorityError):
        MODULE.git_is_ancestor(a, b)
    assert calls == []

def test_git_not_shallow_passes_on_false(monkeypatch):
    calls = fake_git_run(monkeypatch, 0, b'false\n')
    assert MODULE.git_not_shallow() is None
    assert calls == [('rev-parse', '--is-shallow-repository')]

def test_git_not_shallow_rejects_shallow(monkeypatch):
    fake_git_run(monkeypatch, 0, b'true\n')
    with pytest.raises(MODULE.GitHistoryError, match='shallow') as e:
        MODULE.git_not_shallow()
    assert 'fetch full history' in str(e.value)

@pytest.mark.parametrize('stdout', [b'maybe\n', b''], ids=['maybe', 'empty'])
def test_git_not_shallow_unknown_output_fails_closed(monkeypatch, stdout):
    fake_git_run(monkeypatch, 0, stdout)
    with pytest.raises(MODULE.GitHistoryError, match='cannot tell whether the clone is shallow') as e:
        MODULE.git_not_shallow()
    assert repr(stdout.decode('utf-8')) in str(e.value)

def test_git_not_shallow_rc_failure(monkeypatch):
    fake_git_run(monkeypatch, 128, b'', b'fatal: not a git repository')
    with pytest.raises(MODULE.GitHistoryError):
        MODULE.git_not_shallow()

def test_git_dirty_returns_porcelain_lines(monkeypatch):
    calls = fake_git_run(monkeypatch, 0, b' M registry/a.json\n?? registry/b.json\n\n')
    assert MODULE.git_dirty(['registry/a.json', 'registry/b.json']) == [' M registry/a.json', '?? registry/b.json']
    assert calls == [('--literal-pathspecs', 'status', '--porcelain', '--untracked-files=all', '--ignored=matching', '--', 'registry/a.json', 'registry/b.json')]
    fake_git_run(monkeypatch, 0, b'')
    assert MODULE.git_dirty(['registry/a.json']) == []

@pytest.mark.parametrize('bad', ['../x', '/etc/passwd', 'C:\\x', 'a/../../b', ''])
def test_git_dirty_rejects_bad_path_before_git(monkeypatch, bad):
    calls = fake_git_run(monkeypatch, 0)
    with pytest.raises(AuthorityError):
        MODULE.git_dirty(['registry/a.json', bad])
    assert calls == []

def test_git_dirty_rejects_empty_path_list(monkeypatch):
    calls = fake_git_run(monkeypatch, 0)
    with pytest.raises(AuthorityError):
        MODULE.git_dirty([])
    assert calls == []

def test_git_dirty_rc_failure(monkeypatch):
    fake_git_run(monkeypatch, 128, b'', b'fatal: not a git repository')
    with pytest.raises(MODULE.GitHistoryError, match='not a git repository'):
        MODULE.git_dirty(['registry/a.json'])

def test_git_run_oserror_is_git_history_error(monkeypatch):
    def boom(*args, **kwargs): raise OSError('no git on PATH')
    monkeypatch.setattr(MODULE.subprocess, 'run', boom)
    with pytest.raises(MODULE.GitHistoryError, match='git unavailable'):
        MODULE.git_run('status')

def test_git_run_oserror_names_the_command(monkeypatch):
    def boom(*args, **kwargs): raise OSError('no git on PATH')
    monkeypatch.setattr(MODULE.subprocess, 'run', boom)
    with pytest.raises(MODULE.GitHistoryError) as e:
        MODULE.git_run('--literal-pathspecs', 'status')
    assert 'git status:' in str(e.value) and 'git --literal-pathspecs' not in str(e.value)

# ---- 12-08 Task 2: HEAD-blob, index-flag and plain working-tree binding seams (CR-01, WR-01) ----

@pytest.mark.parametrize('commit,path', [('HEAD', 'registry/a.json'), (SHA40[:7], 'registry/a.json'), (SHA40.upper(), 'registry/a.json'), (None, 'registry/a.json'), (SHA40, '../x'), (SHA40, '/etc/passwd'), (SHA40, 'C:\\x'), (SHA40, '')], ids=['head_name', 'short_sha', 'upper_sha', 'none', 'dotdot', 'absolute', 'drive', 'empty'])
def test_git_commit_blob_argv_and_failures(monkeypatch, commit, path):
    calls = fake_git_run(monkeypatch, 0, b'{"a": 1}\n')
    assert MODULE.git_commit_blob(SHA40, 'registry/a.json') == b'{"a": 1}\n'
    assert calls == [('cat-file', 'blob', f'{SHA40}:registry/a.json')]
    fake_git_run(monkeypatch, 128, b'', b'fatal: path does not exist')
    with pytest.raises(MODULE.GitHistoryError, match='git cat-file failed: fatal: path does not exist'):
        MODULE.git_commit_blob(SHA40, 'registry/a.json')
    calls = fake_git_run(monkeypatch, 0, b'x')
    with pytest.raises(AuthorityError) as e:
        MODULE.git_commit_blob(commit, path)
    assert e.type is AuthorityError
    assert calls == []

def test_git_index_flags_reports_flagged_and_missing_paths(monkeypatch):
    paths = ['registry/a.json', 'registry/b.json', 'registry/c.json', 'registry/d.json']
    want = ["registry/b.json: index tag 'S' (lowercase = assume-unchanged, S = skip-worktree)", "registry/c.json: index tag 'h' (lowercase = assume-unchanged, S = skip-worktree)", 'registry/d.json: not in the index']
    calls = fake_git_run(monkeypatch, 0, b'H registry/a.json\nS registry/b.json\nh registry/c.json\n')
    assert MODULE.git_index_flags(paths) == want
    assert calls == [('--literal-pathspecs', 'ls-files', '-v', '--', *paths)]
    fake_git_run(monkeypatch, 0, b'H registry/a.json\r\nS registry/b.json\r\nh registry/c.json\r\n')
    assert MODULE.git_index_flags(paths) == want
    fake_git_run(monkeypatch, 0, b'H registry/a.json\nM registry/b.json\n')
    assert MODULE.git_index_flags(paths[:2]) == ["registry/b.json: index tag 'M' (lowercase = assume-unchanged, S = skip-worktree)"]
    fake_git_run(monkeypatch, 0, b'H registry/a.json\nH registry/b.json\n')
    assert MODULE.git_index_flags(paths[:2]) == []

@pytest.mark.parametrize('paths', [[], ['registry/a.json', '../x'], ['registry/a.json', '/etc/passwd'], ['C:\\x'], ['']], ids=['empty_list', 'dotdot', 'absolute', 'drive', 'empty_path'])
def test_git_index_flags_rejects_bad_input_before_git(monkeypatch, paths):
    calls = fake_git_run(monkeypatch, 0)
    with pytest.raises(AuthorityError) as e:
        MODULE.git_index_flags(paths)
    assert e.type is AuthorityError
    assert calls == []

def test_git_index_flags_rc_failure(monkeypatch):
    fake_git_run(monkeypatch, 128, b'', b'fatal: not a git repository')
    with pytest.raises(MODULE.GitHistoryError, match='git ls-files failed: fatal: not a git repository'):
        MODULE.git_index_flags(['registry/a.json'])

@pytest.mark.parametrize('case', ['pass_crlf', 'not_committed', 'absent', 'differs', 'flagged'])
def test_check_tree_matches_head_cases(env, monkeypatch, case):
    p, blob = 'registry/a.json', b'{"a": 1}\n'
    live = MODULE.ROOT / p
    if case != 'absent':
        live.parent.mkdir(parents=True, exist_ok=True)
        live.write_bytes(b'{"a": 2}\n' if case == 'differs' else blob.replace(b'\n', b'\r\n'))
    blob_calls, flag_calls = [], []
    def commit_blob(commit, path):
        blob_calls.append((commit, path))
        if case == 'not_committed': raise MODULE.GitHistoryError(f'{path}@{commit[:7]}: git cat-file failed: fatal: path does not exist')
        return blob
    monkeypatch.setattr(MODULE, 'git_commit_blob', commit_blob)
    flagged = [f"{p}: index tag 'S' (lowercase = assume-unchanged, S = skip-worktree)"]
    monkeypatch.setattr(MODULE, 'git_index_flags', lambda paths: flag_calls.append(list(paths)) or (flagged if case == 'flagged' else []))
    if case == 'pass_crlf':
        assert REAL_CHECK_TREE_MATCHES_HEAD([p]) is None
        assert blob_calls == [(HEAD_COMMIT, p)] and flag_calls == [[p]]
        return
    want = {'not_committed': re.escape(p) + ': not committed at HEAD bbbbbbb', 'absent': re.escape(p) + ': absent from the working tree', 'differs': re.escape(p) + ': working tree differs from HEAD bbbbbbb', 'flagged': 'index flags hide working-tree state from git: ' + re.escape(flagged[0])}[case]
    with pytest.raises(AuthorityError, match=want) as e:
        REAL_CHECK_TREE_MATCHES_HEAD([p])
    assert e.type is AuthorityError
    assert blob_calls == [(HEAD_COMMIT, p)]
    # the byte comparison runs first, so the index is consulted only when every path's bytes match HEAD
    assert flag_calls == ([[p]] if case == 'flagged' else [])

def test_plain_validate_binds_working_tree_to_head(env, fake_git_show, monkeypatch, capsys):
    published_recorded(env, fake_git_show)
    tree, dirty = [], []
    monkeypatch.setattr(MODULE, 'check_tree_matches_head', lambda paths: tree.append(list(paths)))
    monkeypatch.setattr(MODULE, 'git_dirty', lambda paths: dirty.append(list(paths)) or [])
    capsys.readouterr()
    MODULE.validate_published()
    assert capsys.readouterr().out.strip() == 'PASS'
    assert tree == [MODULE.publication_paths()] and len(tree[0]) == 10
    assert dirty == []
    matrix = f'{MODULE.rel(MODULE.OUT)}/{MODULE.N_MATRIX}'
    def differs(paths): raise AuthorityError(f'{matrix}: working tree differs from HEAD bbbbbbb (CRLF_TO_LF normalised)')
    monkeypatch.setattr(MODULE, 'check_tree_matches_head', differs)
    with pytest.raises(AuthorityError, match=re.escape(matrix) + ': working tree differs from HEAD'):
        MODULE.validate_published()

def test_git_show_argv_ends_with_double_dash(monkeypatch):
    seen = []
    def fake(argv, **kwargs):
        seen.append(argv)
        return subprocess.CompletedProcess(argv, 0, b'x', b'')
    monkeypatch.setattr(MODULE.subprocess, 'run', fake)
    assert MODULE.git_show(SHA40, 'registry/a.json') == b'x'
    assert seen == [['git', 'show', f'{SHA40}:registry/a.json', '--']]

def test_publication_paths_are_the_ten_d05_files():
    paths = MODULE.publication_paths()
    assert len(paths) == 10 and len(set(paths)) == 10
    assert paths[:3] == [MODULE.rel(MODULE.AUTHORITY), MODULE.rel(MODULE.SCHEMA), MODULE.rel(MODULE.SIGNOFF)]
    out_rel = MODULE.rel(MODULE.OUT)
    assert paths[3:] == [f'{out_rel}/{n}' for n in (MODULE.N_MATRIX, MODULE.N_SEMANTIC, MODULE.N_NEGATIVE, MODULE.N_TRACE, MODULE.N_CERT, MODULE.N_REPORT, MODULE.N_MANIFEST)]
    assert all(not MODULE.bad_rel(p) for p in paths)

def test_publication_paths_match_the_publication_commit_file_list():
    assert REAL_RECORD.exists(), f'{REAL_RECORD} must be committed'
    pub = MODULE.load(REAL_RECORD)['publication_commit']
    require_history(ROOT, commits=(pub,))
    files = git('diff-tree', '--no-commit-id', '--name-only', '-r', pub).stdout.decode().split()
    assert sorted(MODULE.publication_paths()) == sorted(files)

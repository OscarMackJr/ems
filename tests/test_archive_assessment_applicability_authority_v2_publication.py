import copy
import importlib.util
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
    assert lin['supersedes']['commit'] == '62a8955' and lin['supersedes']['version'] == '1.0.0'
    assert lin['supersedes']['sha256'] == MODULE.lf_digest(MODULE.V1_AUTHORITY)
    assert lin['catalog_reference']['sha256'] == MODULE.lf_digest(MODULE.CATALOG)
    assert lin['digest_normalisation'] == 'CRLF_TO_LF'

def test_module_does_not_call_git():
    src = SCRIPT.read_text(encoding='utf-8')
    assert 'subprocess' not in src and 'import git' not in src

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
    fails(lambda a: a['source_lineage'].pop('governance_decisions'))

def test_wrong_v1_lineage_fails():
    fails(lambda a: a['source_lineage']['supersedes'].__setitem__('sha256', '0' * 64))
    fails(lambda a: a['source_lineage']['supersedes'].__setitem__('commit', 'abcdef0'))

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
import subprocess
import tempfile

ROOT = Path(__file__).parents[1]
DUAL = MODULE.DUAL_ROLE_STATEMENT

def sha_text(t): return hashlib.sha256(t.encode('utf-8')).hexdigest()

def valid_signoff(authority_digest):
    return {'status': 'PUBLICATION_SIGNOFF', 'approval': {'approver': 'Oscar Mack', 'role': 'EMS_GOVERNANCE_AUTHORITY', 'date': '2026-10-14', 'scope': 'Publish v2 authority'}, 'dual_role_statement': DUAL, 'authority_id': MODULE.AUTHORITY_ID, 'version': '2.0.0', 'authority_sha256': authority_digest, 'authority_sha256_normalisation': 'CRLF_TO_LF'}

@pytest.fixture
def env(monkeypatch):
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        for name, value in {'ROOT': root, 'AUTHORITY': root / 'registry' / 'a.json', 'SCHEMA': root / 'schemas' / 's.json', 'SIGNOFF': root / 'registry' / 'signoff.json', 'PUBLICATION_RECORD': root / 'registry' / 'record.json', 'OUT': root / 'generated' / 'out', 'SCRIPT': root / 'scripts' / 'pub.py'}.items():
            monkeypatch.setattr(MODULE, name, value)
        MODULE.dump(MODULE.SCHEMA, MODULE.schema())
        MODULE.write_text(MODULE.SCRIPT, 'print(1)\n')
        yield root

def write_signoff(a=None):
    a = a or build()
    MODULE.dump(MODULE.SIGNOFF, valid_signoff(sha_text(MODULE.jtext(a))))

def test_outputs_deterministic_and_lf_only():
    a = build()
    first = MODULE.build_all_outputs(a)
    assert first == MODULE.build_all_outputs(a)
    assert list(first) == [MODULE.N_MATRIX, MODULE.N_SEMANTIC, MODULE.N_NEGATIVE, MODULE.N_TRACE, MODULE.N_CERT, MODULE.N_REPORT, MODULE.N_MANIFEST]
    for text in first.values():
        assert '\r' not in text
        assert 'T00:' not in text
    assert MODULE.PUBLISHED_ON in first[MODULE.N_CERT]
    assert json.loads(first[MODULE.N_CERT])['digest_normalisation'] == 'CRLF_TO_LF'
    assert json.loads(first[MODULE.N_MANIFEST])['digest_normalisation'] == 'CRLF_TO_LF'

def test_traceability_21_and_59():
    t = json.loads(MODULE.build_all_outputs(build())[MODULE.N_TRACE])
    assert len(t['decision_records']) == 21 and len(t['undecided_controls']) == 59
    r = t['decision_records'][0]
    assert {'control_id', 'decision_id', 'state', 'rule', 'decision_record_path', 'decision_record_sha256'} <= set(r)

def test_semantic_output_never_resolves_unknown_to_not_applicable():
    s = json.loads(MODULE.build_all_outputs(build())[MODULE.N_SEMANTIC])
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

def test_publish_writes_all_and_is_byte_identical(env):
    published(env)
    first = snapshot()
    assert len(first) == 8
    assert all(b'\r' not in v for v in first.values())
    MODULE.publish(False)
    assert snapshot() == first
    MODULE.validate_published()

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
    outs = MODULE.build_all_outputs(a, MODULE.load(MODULE.SIGNOFF))
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

def test_write_publication_record(env):
    published(env)
    MODULE.write_publication_record('a' * 40)
    rec = MODULE.load(MODULE.PUBLICATION_RECORD)
    assert set(rec) == {'publication_commit', 'authority_id', 'version', 'authority_sha256', 'manifest_sha256', 'digest_normalisation'}
    assert rec['publication_commit'] == 'a' * 40 and rec['digest_normalisation'] == 'CRLF_TO_LF'
    assert rec['authority_sha256'] == MODULE.lf_digest(MODULE.AUTHORITY)
    for bad in ('abc', 'A' * 40, 'g' * 40, ''):
        with pytest.raises(AuthorityError):
            MODULE.write_publication_record(bad)

REAL_AUTHORITY = MODULE.AUTHORITY
REAL_RECORD = MODULE.PUBLICATION_RECORD
REAL_OUT = MODULE.OUT
REAL_SIGNOFF = MODULE.SIGNOFF

@pytest.mark.skipif(not REAL_AUTHORITY.exists(), reason='v2 authority not published yet')
def test_real_published_files_validate():
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

def git(*args):
    r = subprocess.run(['git', *args], cwd=ROOT, capture_output=True)
    return subprocess.CompletedProcess(r.args, r.returncode, r.stdout, r.stderr.decode('utf-8', 'replace').strip())

def git_ready():
    try: r = git('rev-parse', '--is-shallow-repository')
    except OSError: return 'git is unavailable'
    if r.returncode != 0: return 'not a git repository'
    if r.stdout.decode().strip() == 'true': return 'shallow repository, history is incomplete'
    return None

def lf_sha(b): return hashlib.sha256(b.replace(b'\r\n', b'\n')).hexdigest()

@pytest.mark.skipif(not REAL_RECORD.exists(), reason='publication record not written yet')
def test_publication_commit_ancestor_and_file_set():
    reason = git_ready()
    if reason: pytest.skip(reason)
    rec = MODULE.load(REAL_RECORD)
    sha = rec['publication_commit']
    assert git('merge-base', '--is-ancestor', sha, 'HEAD').returncode == 0
    files = git('diff-tree', '--no-commit-id', '--name-only', '-r', sha).stdout.decode().split()
    out_rel = REAL_OUT.relative_to(ROOT).as_posix()
    expected = {REAL_AUTHORITY.relative_to(ROOT).as_posix(), REAL_SIGNOFF.relative_to(ROOT).as_posix(), *(f'{out_rel}/{p.name}' for p in REAL_OUT.iterdir())}
    assert set(files) == expected
    assert 'registry/adjudication_rules.json' not in files and 'registry/policy_decisions.json' not in files
    auth_rel = REAL_AUTHORITY.relative_to(ROOT).as_posix()
    assert lf_sha(git('show', f'{sha}:{auth_rel}').stdout) == rec['authority_sha256']
    manifest = json.loads(git('show', f'{sha}:{out_rel}/{MODULE.N_MANIFEST}').stdout.decode('utf-8'))
    for art in manifest['artifacts']:
        assert lf_sha(git('show', f"{sha}:{art['relative_path']}").stdout) == art['sha256']

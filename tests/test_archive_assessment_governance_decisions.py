import copy
import hashlib
import importlib.util
import json
import re
import subprocess
from pathlib import Path

import jsonschema
import pytest

TERMS = ['RiskMVP', '42aa362c76980a934fbaa470e603b48c7ef4b0b7', '42aa362', '2026-10-01', 'EMS_NOT_APPLICABLE_RULE_ABSENT']

ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / 'scripts' / 'build_archive_assessment_governance_decisions.py'
SPEC = importlib.util.spec_from_file_location('aa_governance_decisions', SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
AuthorityError = MODULE.AuthorityError
PROPOSALS = json.loads(MODULE.PROPOSALS.read_text(encoding='utf-8'))
BY_ID = {p['control_id']: p for p in PROPOSALS['proposals']}
DRAFTING = json.loads(MODULE.DRAFTING_RECORD.read_text(encoding='utf-8'))
APPROVAL = json.loads(MODULE.WORDING_APPROVAL.read_text(encoding='utf-8'))
RULE_ID = 'EMS-CTRL-010'
NO_RULE_ID = 'EMS-CTRL-009'
TWO = 'First decided sentence. Second decided sentence.'
SYNTH_SHA = 'a' * 64

def scan(text): return [t for t in TERMS if re.search(re.escape(t), text, re.IGNORECASE)]

def rule(*pairs): return {'combination': 'ALL_CONDITIONS_MUST_MATCH', 'conditions': [{'field': f, 'state': s} for f, s in pairs]}

def load(p): return json.loads(p.read_text(encoding='utf-8'))

def kind(cid): return BY_ID[cid]['proposed_outcome']

def filled():
    entries = []
    for c in MODULE.CONTROL_IDS:
        e = MODULE.blank_entry(c)
        e.update(disposition='APPROVED_AS_DRAFTED', note=f'Test-only note for {c}, reviewed on its own.', decided_on='2026-10-14')
        if c in MODULE.SCOPE_NOTE_IDS: e['scope_note_ruling'] = 'ACCEPTED_AS_TRUE_LIMITATION'
        entries.append(e)
    a = {'status': MODULE.STATUS, 'entries': entries}
    rule_ids = [c for c in MODULE.CONTROL_IDS if kind(c) == 'PROPOSE_RULE']
    no_rule_ids = [c for c in MODULE.CONTROL_IDS if kind(c) == 'PROPOSE_NO_RULE']
    ent(a, no_rule_ids[0]).update(disposition='CHANGED', decided_rationale=TWO)
    ent(a, no_rule_ids[1]).update(disposition='REJECTED', decided_rule=rule(('production', 'KNOWN_FALSE')), decided_rationale=TWO)
    if rule_ids:
        ent(a, rule_ids[0]).update(disposition='REJECTED', decided_rule=None, decided_rationale=TWO)
        if len(rule_ids) > 1: ent(a, rule_ids[1]).update(disposition='CHANGED', decided_rule=rule(('internet_exposed', 'KNOWN_FALSE')), decided_rationale=TWO)
    return a

def ent(a, cid): return next(e for e in a['entries'] if e['control_id'] == cid)

def built(answers=None):
    return MODULE.build_decisions(PROPOSALS, answers or filled(), DRAFTING, APPROVAL, SYNTH_SHA, MODULE.V2.digest(MODULE.DRAFTING_RECORD))

def rec(d, cid): return next(r for r in d['records'] if r['control_id'] == cid)

def both_reject(mutator):
    d = built(); mutator(d)
    with pytest.raises(AuthorityError): MODULE.validate_decisions(d)
    with pytest.raises(jsonschema.ValidationError): jsonschema.Draft202012Validator(MODULE.decisions_schema()).validate(d)

def validator_rejects(mutator):
    d = built(); mutator(d)
    with pytest.raises(AuthorityError): MODULE.validate_decisions(d)

def test_build_validates_and_schema_passes():
    d = built()
    MODULE.validate_decisions(d)
    jsonschema.Draft202012Validator(MODULE.decisions_schema()).validate(d)
    assert len(d['records']) == 21
    assert [r['decision_id'] for r in d['records']] == [f'AA4-GOV-{i:03d}' for i in range(1, 22)]
    assert [r['control_id'] for r in d['records']] == MODULE.CONTROL_IDS
    assert d['records'][0]['control_id'] == 'EMS-CTRL-009' and d['records'][20]['control_id'] == 'EMS-CTRL-079'
    assert not any(re.match(r'AA1-GOV-00[1-8]$', r['decision_id']) for r in d['records'])

def test_build_refuses_blank_answers():
    with pytest.raises(AuthorityError): MODULE.build_decisions(PROPOSALS, MODULE.blank_answers(), DRAFTING, APPROVAL, SYNTH_SHA)

def test_synthetic_mix_covers_dispositions():
    d = built()
    assert {r['disposition'] for r in d['records']} == set(MODULE.DISPOSITIONS)
    assert {r['decided_outcome'] for r in d['records']} == {'RULE_PUBLISHED', 'NO_RULE_WILL_BE_PUBLISHED'}

@pytest.mark.parametrize('key', ['dual_role_statement', 'decision_id', 'disposition', 'control_id'])
def test_missing_record_key_rejected(key): both_reject(lambda d: d['records'][3].pop(key))

def test_dropped_role_rejected(): both_reject(lambda d: d['records'][0]['approver_roles'].pop())
def test_other_role_dropped_rejected(): both_reject(lambda d: d['records'][0]['approver_roles'].pop(0))
def test_reordered_roles_rejected(): both_reject(lambda d: d['records'][0]['approver_roles'].reverse())
def test_dual_role_one_character_rejected(): both_reject(lambda d: d['records'][2].__setitem__('dual_role_statement', d['records'][2]['dual_role_statement'][:-1] + '!'))
def test_missing_approver_rejected(): both_reject(lambda d: d['records'][0].pop('approver'))
def test_wrong_approver_rejected(): both_reject(lambda d: d['records'][0].__setitem__('approver', 'Someone Else'))
def test_missing_header_statement_rejected(): both_reject(lambda d: d.pop('earlier_assessment_knowledge_statement'))
def test_missing_typed_statement_rejected(): both_reject(lambda d: d.pop('answers_typed_by_authority_statement'))
def test_not_yet_decided_rejected(): both_reject(lambda d: d['records'][0].__setitem__('decided_outcome', 'NOT_YET_DECIDED'))
def test_unknown_record_key_rejected(): both_reject(lambda d: d['records'][0].__setitem__('extra', 1))
def test_unknown_header_key_rejected(): both_reject(lambda d: d.__setitem__('extra', 1))

def test_approved_with_different_rule_rejected():
    def m(d):
        r = next(x for x in d['records'] if x['disposition'] == 'APPROVED_AS_DRAFTED' and x['decided']['rule'] is not None)
        r['decided']['rule'] = rule(('production', 'KNOWN_TRUE'), ('ai_enabled', 'KNOWN_TRUE'))
        r['amendment_present'] = True
    validator_rejects(m)

def test_changed_equal_to_drafted_rejected():
    def m(d):
        r = next(x for x in d['records'] if x['disposition'] == 'CHANGED')
        r['decided'] = copy.deepcopy(r['drafted']); r['decided']['rationale'] = TWO if r['drafted']['rationale'] != TWO else r['drafted']['rationale']
        r['decided'] = copy.deepcopy(r['drafted']); r['amendment_present'] = False
    validator_rejects(m)

def test_rejected_keeps_kind_rejected():
    def m(d):
        r = next(x for x in d['records'] if x['disposition'] == 'REJECTED')
        r['decided'] = {'outcome': r['drafted']['outcome'], 'rule': copy.deepcopy(r['drafted']['rule']), 'rationale': TWO}
        r['decided_outcome'] = 'RULE_PUBLISHED' if r['decided']['rule'] is not None else 'NO_RULE_WILL_BE_PUBLISHED'
        r['amendment_present'] = True
    validator_rejects(m)

def test_drafted_text_altered_rejected(): validator_rejects(lambda d: d['records'][0]['drafted'].__setitem__('rationale', 'Altered drafted text.'))
def test_duplicate_decision_id_rejected(): validator_rejects(lambda d: d['records'][1].__setitem__('decision_id', d['records'][0]['decision_id']))
def test_skipped_id_rejected(): validator_rejects(lambda d: d['records'][5].__setitem__('decision_id', 'AA4-GOV-099'))
def test_scope_note_missing_on_030_rejected(): validator_rejects(lambda d: rec(d, 'EMS-CTRL-030').__setitem__('scope_note', None))
def test_scope_note_present_on_009_rejected(): validator_rejects(lambda d: rec(d, 'EMS-CTRL-009').__setitem__('scope_note', {'drafted_note': 'x', 'ruling': 'ACCEPTED_AS_TRUE_LIMITATION'}))
def test_proposals_digest_mismatch_rejected(): validator_rejects(lambda d: d.__setitem__('proposals_sha256', 'b' * 64))
def test_drafting_record_digest_mismatch_rejected(): validator_rejects(lambda d: d.__setitem__('drafting_record_sha256', 'b' * 64))
def test_drafting_commit_mismatch_rejected(): validator_rejects(lambda d: rec(d, NO_RULE_ID).__setitem__('drafting_commit', 'c' * 40))
def test_absolute_path_rejected(): validator_rejects(lambda d: d.__setitem__('answers_path', 'C:\\temp\\answers.json'))
def test_rule_with_unknown_state_rejected():
    def m(d):
        r = next(x for x in d['records'] if x['decided']['rule'] is not None and x['disposition'] != 'APPROVED_AS_DRAFTED')
        r['decided']['rule'] = rule(('production', 'UNKNOWN'))
    validator_rejects(m)

def test_changed_and_rejected_carry_both_texts_and_approved_identical():
    d = built()
    keys = {tuple(r) for r in d['records']}
    assert len(keys) == 1 and list(keys.pop()) == list(d['records'][0])
    for r in d['records']:
        assert set(r['drafted']) == set(r['decided']) == set(MODULE.SIDE_KEYS)
        if r['disposition'] == 'APPROVED_AS_DRAFTED':
            assert r['decided'] == r['drafted'] and r['amendment_present'] is False
        else:
            assert r['decided'] != r['drafted'] and r['amendment_present'] is True
        assert r['interpretation']['accepted_as_basis_of_this_decision_only'] is True
        assert r['header_statement_ref'] == 'earlier_assessment_knowledge_statement'
        assert r['approver'] == 'Oscar Mack' and r['approver_roles'] == ['EMS_GOVERNANCE_AUTHORITY', 'HAYES_VERIFY_DEVELOPER']
        assert (r['scope_note'] is not None) == (r['control_id'] in MODULE.SCOPE_NOTE_IDS)

def supersede(d, old_index, new_id=None):
    old = d['records'][old_index]
    new = copy.deepcopy(old)
    new['decision_id'] = new_id or f'AA4-GOV-{len(d["records"]) + 1:03d}'
    new['supersedes'] = old['decision_id']
    d['records'].append(new)
    return new

def test_supersession_keeps_old_and_validates():
    d = built(); new = supersede(d, 0)
    MODULE.validate_decisions(d)
    jsonschema.Draft202012Validator(MODULE.decisions_schema()).validate(d)
    assert new['decision_id'] == 'AA4-GOV-022' and d['records'][0]['decision_id'] == 'AA4-GOV-001' and len(d['records']) == 22

def test_supersession_other_control_rejected():
    def m(d): supersede(d, 0)['supersedes'] = d['records'][1]['decision_id']
    validator_rejects(m)

def test_supersession_later_id_rejected():
    def m(d): supersede(d, 0)['supersedes'] = 'AA4-GOV-030'
    validator_rejects(m)

def test_supersession_self_rejected():
    def m(d):
        n = supersede(d, 0); n['supersedes'] = n['decision_id']
    validator_rejects(m)

def test_two_unsuperseded_for_one_control_rejected():
    def m(d): supersede(d, 0)['supersedes'] = None
    validator_rejects(m)

def test_build_deterministic_and_text_form():
    a, b = built(), built()
    assert a == b
    t = MODULE.decisions_text(a)
    assert t == MODULE.decisions_text(b) and t.endswith('\n') and t == json.dumps(a, indent=2, sort_keys=True) + '\n'
    assert not MODULE.V2.contains_absolute(a)

def test_wording_equality_with_approval_file():
    s = APPROVAL['statements']
    assert MODULE.DUAL_ROLE_STATEMENT == s['dual_role_statement']
    assert MODULE.EARLIER_ASSESSMENT_STATEMENT == s['earlier_assessment_knowledge_statement']
    assert MODULE.TYPED_BY_AUTHORITY_STATEMENT == s['answers_typed_by_authority_statement']
    for k, text in s.items(): assert hashlib.sha256(text.encode('utf-8')).hexdigest() == APPROVAL['statement_sha256'][k]
    d = built()
    assert d['wording_approval']['statement_sha256'] == APPROVAL['statement_sha256']

def test_schema_file_equals_function_and_is_valid():
    s = load(MODULE.DECISIONS_SCHEMA)
    assert s == MODULE.decisions_schema()
    jsonschema.Draft202012Validator.check_schema(s)

def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, capture_output=True)

def git_ready():
    try: r = git('rev-parse', '--is-shallow-repository')
    except OSError: return 'git is unavailable'
    if r.returncode != 0: return 'not a git repository'
    if r.stdout.decode().strip() == 'true': return 'shallow repository, history is incomplete'
    return None

def needs_git(fn):
    reason = git_ready()
    return pytest.mark.skipif(reason is not None, reason=reason or '')(fn)

def lf(b): return b.replace(b'\r\n', b'\n')

@needs_git
def test_drafting_commit_is_ancestor_and_holds_proposals():
    assert git('merge-base', '--is-ancestor', MODULE.DRAFTING_COMMIT, 'HEAD').returncode == 0
    files = git('show', '--name-only', '--pretty=format:', MODULE.DRAFTING_COMMIT).stdout.decode().split()
    assert MODULE.PROPOSALS_REL in files
    assert MODULE.DRAFTING_RECORD_REL not in files

@needs_git
def test_proposals_frozen_since_drafting_commit():
    old = git('show', f'{MODULE.DRAFTING_COMMIT}:{MODULE.PROPOSALS_REL}')
    assert old.returncode == 0
    assert lf(old.stdout) == lf(MODULE.PROPOSALS.read_bytes())

@needs_git
def test_drafting_record_and_frozen_inputs_unchanged():
    assert git('diff', '--quiet', 'HEAD', '--', MODULE.DRAFTING_RECORD_REL).returncode == 0
    assert DRAFTING['drafting_commit'] == MODULE.DRAFTING_COMMIT
    assert DRAFTING['proposals_sha256'] == MODULE.V2.digest(MODULE.PROPOSALS)
    for path in ('registry/control_catalog.yaml', '.planning/phases/01-rule-shape-and-decision-states/01-FIELD-DEFINITIONS.md'):
        assert git('diff', '--quiet', 'HEAD', '--', path).returncode == 0, path

def test_term_scan_detects_and_allows_dual_role_sentence():
    for t in TERMS: assert t in scan(f'prefix {t} suffix')
    assert scan(MODULE.DUAL_ROLE_STATEMENT) == [] and 'Hayes Verify' in MODULE.DUAL_ROLE_STATEMENT

def test_term_scan_built_output_and_source():
    assert scan(MODULE.decisions_text(built())) == []
    assert scan(SCRIPT.read_text(encoding='utf-8')) == []
    assert 'DEMO3-W1-REQ-001' not in MODULE.decisions_text(built())

@pytest.mark.skipif(not MODULE.DECISIONS.exists(), reason='decisions not yet built')
def test_term_scan_real_decisions_file():
    assert scan(MODULE.DECISIONS.read_text(encoding='utf-8')) == []
    assert scan(MODULE.DECISIONS.name) == []

@pytest.mark.skipif(not MODULE.DECISIONS.exists(), reason='decisions not yet built')
def test_real_decisions_file_valid_and_reproducible():
    d = load(MODULE.DECISIONS)
    MODULE.validate_decisions(d)
    jsonschema.Draft202012Validator(load(MODULE.DECISIONS_SCHEMA)).validate(d)
    assert d['answers_sha256'] == MODULE.answers_digest(MODULE.ANSWERS)
    assert lf(MODULE.DECISIONS.read_bytes()) == MODULE.decisions_text(MODULE.build_from_files()).encode('utf-8')

def test_source_hygiene():
    src = SCRIPT.read_text(encoding='utf-8')
    code = '\n'.join(x for x in src.split('\n') if not x.lstrip().startswith('#'))
    assert not re.search('generated', code, re.IGNORECASE)
    assert 'APPROVE_ALL' not in src
    for name in ('PROPOSALS', 'DRAFTING_RECORD'):
        assert f'dump({name}' not in src and f'{name}.write' not in src and f'open({name}' not in src
    assert 'control_catalog' not in src and 'FIELD-DEFINITIONS' not in src
    assert 'FORBIDDEN_ID_RE' not in src and 'walk_forbidden' not in src

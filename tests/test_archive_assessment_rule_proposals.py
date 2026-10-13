import copy
import hashlib
import importlib.util
import json
import re
import subprocess
from pathlib import Path

import jsonschema
import pytest

TERMS = ['RiskMVP', '42aa362c76980a934fbaa470e603b48c7ef4b0b7', '42aa362', 'Hayes', '2026-10-01', 'EMS_NOT_APPLICABLE_RULE_ABSENT', 'DEMO3-W1-REQ-001']

SCRIPT = Path(__file__).parents[1] / 'scripts' / 'validate_archive_assessment_rule_proposals.py'
SPEC = importlib.util.spec_from_file_location('aa_rule_proposals', SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
AuthorityError = MODULE.AuthorityError
ROOT = MODULE.ROOT
PLACEHOLDER = 'Placeholder statement one. Placeholder statement two.'

def build_fixture():
    live = MODULE.live_catalog()
    proposals = []
    for cid in MODULE.CONTROL_IDS:
        e = live[cid]
        ci = {k: e[k] for k in MODULE.CATALOG_INPUT_REQUIRED + MODULE.CATALOG_INPUT_OPTIONAL if k in e}
        proposals.append({'control_id': cid, 'proposed_outcome': 'PROPOSE_NO_RULE', 'proposed_rule': None, 'catalog_inputs': ci,
            'interpretation': {'label': MODULE.INTERPRETATION_LABEL, 'text': 'placeholder'}, 'rationale': PLACEHOLDER, 'confidence': 'LOW', 'alternative_considered': None, 'shape_limitation': None})
    return dict(MODULE.expected_header(), proposals=proposals)

FIXTURE = build_fixture()

def build_record_fixture():
    return {'status': MODULE.RECORD_STATUS, 'drafting_commit': 'a' * 40, 'proposals_path': 'registry/p.json', 'proposals_sha256': 'b' * 64, 'catalog_path': 'registry/control_catalog.yaml',
        'catalog_sha256': 'c' * 64, 'catalog_git_blob_id': 'd' * 40, 'brief_path': 'docs/b.md', 'brief_sha256': 'e' * 64, 'brief_commit': 'f' * 40,
        'brief_approval': {'approver': 'Approver', 'role': 'Role', 'date': '2026-01-01', 'scope': 'scope'}, 'validator_script': 'scripts/v.py', 'validator_result': 'PASS',
        'correction_rounds': 0, 'discarded_attempts': [], 'drafted_on': '2026-01-01', 'isolation_method': 'Isolation by instruction and brief design.',
        'drafter': {'kind': 'AI agent', 'model_id': 'model', 'holds_ems_authority': False}, 'statement': MODULE.RECORD_STATEMENT}

def fx(): return copy.deepcopy(FIXTURE)

def invalid(mutator):
    value = fx()
    mutator(value)
    with pytest.raises(AuthorityError):
        MODULE.validate_proposals(value)

def ok(mutator):
    value = fx()
    mutator(value)
    MODULE.validate_proposals(value)
    jsonschema.Draft202012Validator(MODULE.schema()).validate(value)

def schema_rejects(mutator):
    value = fx()
    mutator(value)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(MODULE.schema()).validate(value)

def both_reject(mutator):
    invalid(mutator)
    schema_rejects(mutator)

def rule(*pairs): return {'combination': 'ALL_CONDITIONS_MUST_MATCH', 'conditions': [{'field': f, 'state': s} for f, s in pairs]}

def prop(a, i=0): return a['proposals'][i]

def to_rule(r, alt=True):
    def m(a):
        p = prop(a); p['proposed_outcome'] = 'PROPOSE_RULE'; p['proposed_rule'] = r
    return m

def rec_invalid(mutator):
    r = build_record_fixture(); mutator(r)
    with pytest.raises(AuthorityError): MODULE.validate_record(r)
    with pytest.raises(jsonschema.ValidationError): jsonschema.Draft202012Validator(MODULE.record_schema()).validate(r)

def test_fixture_validates_under_validator_and_schema(): ok(lambda a: None)
def test_fixture_uses_one_uniform_outcome(): assert {p['proposed_outcome'] for p in FIXTURE['proposals']} == {'PROPOSE_NO_RULE'}
def test_fixture_covers_all_21_controls(): assert [p['control_id'] for p in FIXTURE['proposals']] == MODULE.CONTROL_IDS and len(MODULE.CONTROL_IDS) == 21

@pytest.mark.parametrize('field', ['production', 'internet_exposed', 'contains_customer_data', 'ai_enabled'])
@pytest.mark.parametrize('state', ['KNOWN_TRUE', 'KNOWN_FALSE'])
def test_rule_with_usable_field_passes(field, state): ok(to_rule(rule((field, state))))

def test_alternative_and_shape_limitation_pass():
    def m(a):
        p = prop(a); p['alternative_considered'] = {'outcome': 'PROPOSE_RULE', 'why': 'because'}; p['shape_limitation'] = {'scope': p['catalog_inputs']['scope'], 'note': 'note'}
    ok(m)

@pytest.mark.parametrize('field', ['tier', 'owner', 'service_criticality', 'data_classification', 'region'])
def test_unusable_rule_field_fails_closed(field): both_reject(to_rule(rule((field, 'KNOWN_TRUE'))))
def test_unknown_state_fails_closed(): both_reject(to_rule(rule(('production', 'UNKNOWN'))))
def test_empty_conditions_fails_closed(): both_reject(to_rule(rule()))
def test_extra_key_in_rule_fails_closed(): both_reject(to_rule(dict(rule(('production', 'KNOWN_FALSE')), reason='x')))
def test_extra_key_in_condition_fails_closed(): both_reject(to_rule({'combination': 'ALL_CONDITIONS_MUST_MATCH', 'conditions': [{'field': 'production', 'state': 'KNOWN_FALSE', 'negate': True}]}))
def test_wrong_combination_fails_closed(): both_reject(to_rule(dict(rule(('production', 'KNOWN_FALSE')), combination='ANY_CONDITION_MAY_MATCH')))
def test_propose_rule_with_null_rule_fails_closed(): both_reject(lambda a: prop(a).__setitem__('proposed_outcome', 'PROPOSE_RULE'))
def test_propose_no_rule_with_rule_fails_closed(): both_reject(lambda a: prop(a).__setitem__('proposed_rule', rule(('production', 'KNOWN_FALSE'))))
def test_status_other_than_draft_fails_closed(): both_reject(lambda a: a.__setitem__('status', 'PUBLISHED'))
def test_frame_unknown_flag_flipped_fails_closed(): both_reject(lambda a: a['drafting_frame'].__setitem__('unknown_is_never_not_applicable', False))
def test_frame_resolution_row_dropped_fails_closed(): both_reject(lambda a: a['drafting_frame']['resolution'].pop())
def test_frame_field_definition_emptied_fails_closed(): both_reject(lambda a: a['drafting_frame']['field_definitions'].__setitem__('production', ''))
def test_catalog_sha256_altered_fails_closed(): invalid(lambda a: a['catalog_source'].__setitem__('sha256', '0' * 64))
def test_catalog_blob_id_altered_fails_closed(): invalid(lambda a: a['catalog_source'].__setitem__('git_blob_id', '0' * 40))
def test_missing_control_fails_closed(): both_reject(lambda a: a['proposals'].pop())
def test_duplicate_control_fails_closed(): invalid(lambda a: a['proposals'].__setitem__(1, copy.deepcopy(a['proposals'][0])))
def test_unknown_control_fails_closed(): both_reject(lambda a: prop(a).__setitem__('control_id', 'EMS-CTRL-999'))
def test_22nd_control_fails_closed(): both_reject(lambda a: a['proposals'].append(copy.deepcopy(a['proposals'][0])))
def test_count_20_fails_closed(): both_reject(lambda a: a['proposals'].pop(5))
def test_extra_proposal_key_fails_closed(): both_reject(lambda a: prop(a).__setitem__('extra', 1))
def test_authority_key_fails_closed(): both_reject(lambda a: prop(a).__setitem__('not_applicable_authority', 'x'))
def test_decision_id_key_fails_closed(): both_reject(lambda a: prop(a).__setitem__('decision_id', 'x'))
def test_governance_id_in_rationale_fails_closed(): invalid(lambda a: prop(a).__setitem__('rationale', 'First sentence AA4-GOV-001. Second sentence.'))
def test_wrong_interpretation_label_fails_closed(): both_reject(lambda a: prop(a)['interpretation'].__setitem__('label', 'EMS_SOURCE'))
def test_missing_interpretation_label_fails_closed(): both_reject(lambda a: prop(a)['interpretation'].pop('label'))
def test_confidence_certain_fails_closed(): both_reject(lambda a: prop(a).__setitem__('confidence', 'CERTAIN'))
def test_alternative_equal_to_outcome_fails_closed(): invalid(lambda a: prop(a).__setitem__('alternative_considered', {'outcome': 'PROPOSE_NO_RULE', 'why': 'x'}))
def test_shape_limitation_scope_mismatch_fails_closed(): invalid(lambda a: prop(a).__setitem__('shape_limitation', {'scope': 'NOT_THE_SCOPE', 'note': 'x'}))
def test_absolute_path_fails_closed(): invalid(lambda a: prop(a)['interpretation'].__setitem__('text', 'C:/temp/x.json'))

def test_duplicate_condition_field_fails_closed_validator_only(): invalid(to_rule(rule(('production', 'KNOWN_FALSE'), ('production', 'KNOWN_TRUE'))))
def test_one_sentence_rationale_fails_closed_validator_only(): invalid(lambda a: prop(a).__setitem__('rationale', 'Only one sentence.'))
def test_five_sentence_rationale_fails_closed_validator_only(): invalid(lambda a: prop(a).__setitem__('rationale', 'One. Two. Three. Four. Five.'))
def test_catalog_inputs_drift_fails_closed_validator_only(): invalid(lambda a: prop(a)['catalog_inputs'].__setitem__('scope_owner', 'Somebody Else'))
def test_catalog_inputs_missing_scope_owner_fails_closed_validator_only(): invalid(lambda a: prop(a)['catalog_inputs'].pop('scope_owner'))

def test_committed_proposals_schema_equals_schema_function(): assert json.loads(MODULE.SCHEMA.read_text(encoding='utf-8')) == MODULE.schema()
def test_committed_record_schema_equals_record_schema_function(): assert json.loads(MODULE.RECORD_SCHEMA.read_text(encoding='utf-8')) == MODULE.record_schema()
def test_committed_schemas_are_valid():
    jsonschema.Draft202012Validator.check_schema(json.loads(MODULE.SCHEMA.read_text(encoding='utf-8')))
    jsonschema.Draft202012Validator.check_schema(json.loads(MODULE.RECORD_SCHEMA.read_text(encoding='utf-8')))

def test_record_fixture_validates():
    r = build_record_fixture(); MODULE.validate_record(r); jsonschema.Draft202012Validator(MODULE.record_schema()).validate(r)
def test_record_bad_commit_hex_fails_closed(): rec_invalid(lambda r: r.__setitem__('drafting_commit', 'xyz'))
def test_record_negative_correction_rounds_fails_closed(): rec_invalid(lambda r: r.__setitem__('correction_rounds', -1))
def test_record_validator_result_fail_fails_closed(): rec_invalid(lambda r: r.__setitem__('validator_result', 'FAIL'))
def test_record_drafter_authority_fails_closed(): rec_invalid(lambda r: r['drafter'].__setitem__('holds_ems_authority', True))
def test_record_statement_altered_fails_closed(): rec_invalid(lambda r: r.__setitem__('statement', 'altered'))
def test_record_isolation_phrase_missing_fails_closed(): rec_invalid(lambda r: r.__setitem__('isolation_method', 'some other method'))

def test_validator_source_has_no_generated_dir_or_scan_terms():
    src = SCRIPT.read_text(encoding='utf-8')
    assert 'generated' not in src
    assert not scan(src)
def test_validator_source_does_not_write_proposals():
    src = SCRIPT.read_text(encoding='utf-8')
    assert 'PROPOSALS.write_text' not in src and 'dump(PROPOSALS' not in src

def scan(text): return [t for t in TERMS if re.search(re.escape(t), text, re.IGNORECASE)]

def test_term_scan_detects_each_term():
    for t in TERMS: assert scan(f'prefix {t} suffix') == [t] or t in scan(f'prefix {t} suffix')
    assert 'RiskMVP' in scan('the riskmvp repo')
    assert '42aa362' in scan('commit 42AA362 here')
    assert scan('nothing to see') == []

def gated(path): return pytest.mark.skipif(not path.exists(), reason='not yet written')

@pytest.mark.parametrize('path', [pytest.param(MODULE.PROPOSALS, marks=gated(MODULE.PROPOSALS), id='proposals'), pytest.param(MODULE.BRIEF, marks=gated(MODULE.BRIEF), id='brief'), pytest.param(MODULE.RECORD, marks=gated(MODULE.RECORD), id='record')])
def test_term_scan_real_files(path):
    assert scan(path.read_text(encoding='utf-8')) == []
    assert scan(path.name) == []

def test_term_scan_file_names():
    for p in (MODULE.PROPOSALS, MODULE.BRIEF, MODULE.RECORD): assert scan(p.name) == []

def load(p): return json.loads(p.read_text(encoding='utf-8'))

def git_out(*args):
    try: r = subprocess.run(['git', *args], cwd=ROOT, capture_output=True)
    except FileNotFoundError: pytest.skip('git unavailable')
    assert r.returncode == 0
    return r.stdout

@gated(MODULE.PROPOSALS)
def test_real_proposals_validate_under_validator_and_schema():
    p = load(MODULE.PROPOSALS); MODULE.validate_proposals(p); jsonschema.Draft202012Validator(MODULE.schema()).validate(p)

@gated(MODULE.PROPOSALS)
def test_catalog_drift_real_proposals_match_live_catalog():
    live = MODULE.live_catalog()
    for p in load(MODULE.PROPOSALS)['proposals']:
        for k, v in p['catalog_inputs'].items(): assert live[p['control_id']][k] == v

@gated(MODULE.PROPOSALS)
def test_catalog_fingerprint_matches_blob_bytes():
    blob = git_out('hash-object', MODULE.CATALOG_REL).decode('ascii').strip()
    data = git_out('cat-file', 'blob', blob)
    src = load(MODULE.PROPOSALS)['catalog_source']
    assert src['git_blob_id'] == blob and src['sha256'] == hashlib.sha256(data).hexdigest()

@gated(MODULE.PROPOSALS)
def test_real_proposals_header_status_and_ids():
    p = load(MODULE.PROPOSALS)
    exp = MODULE.expected_header()
    for k in MODULE.HEADER_KEYS: assert p[k] == exp[k]
    assert p['status'] == 'DRAFT_NO_AUTHORITY'
    assert sorted(x['control_id'] for x in p['proposals']) == sorted(MODULE.CONTROL_IDS)

def fenced_after(text, heading):
    i = text.index(heading)
    m = re.search(r'```json\s*\n(.*?)\n```', text[i:], re.DOTALL)
    assert m
    return m, i

@gated(MODULE.BRIEF)
def test_brief_catalog_extract_equals_live_catalog():
    text = MODULE.BRIEF.read_text(encoding='utf-8')
    m, _ = fenced_after(text, '## Catalog extract')
    extract = json.loads(m.group(1))
    live = MODULE.live_catalog()
    assert extract == [live[c] for c in MODULE.CONTROL_IDS]
    assert all('description' not in e for e in extract)

@gated(MODULE.BRIEF)
def test_brief_header_equals_expected_header():
    m, _ = fenced_after(MODULE.BRIEF.read_text(encoding='utf-8'), '## Header to copy')
    assert json.loads(m.group(1)) == MODULE.expected_header()

@gated(MODULE.BRIEF)
def test_brief_has_no_control_ids_outside_extract():
    text = MODULE.BRIEF.read_text(encoding='utf-8')
    m, i = fenced_after(text, '## Catalog extract')
    rest = text[:i] + text[i:][:m.start()] + text[i:][m.end():]
    assert 'EMS-CTRL-' not in rest

@gated(MODULE.RECORD)
def test_real_record_validates():
    r = load(MODULE.RECORD); MODULE.validate_record(r); jsonschema.Draft202012Validator(MODULE.record_schema()).validate(r)

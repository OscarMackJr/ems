import copy
import hashlib
import importlib.util
import json
import re
import tempfile
from pathlib import Path

import jsonschema
import pytest

TERMS = ['RiskMVP', '42aa362c76980a934fbaa470e603b48c7ef4b0b7', '42aa362', '2026-10-01', 'EMS_NOT_APPLICABLE_RULE_ABSENT']

SCRIPT = Path(__file__).parents[1] / 'scripts' / 'build_archive_assessment_governance_decisions.py'
SPEC = importlib.util.spec_from_file_location('aa_governance_decisions', SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
AuthorityError = MODULE.AuthorityError
PROPOSALS = json.loads(MODULE.PROPOSALS.read_text(encoding='utf-8'))
BY_ID = {p['control_id']: p for p in PROPOSALS['proposals']}
RULE_ID = next(c for c in MODULE.CONTROL_IDS if BY_ID[c]['proposed_outcome'] == 'PROPOSE_RULE')
NO_RULE_ID = 'EMS-CTRL-009'
TWO = 'First decided sentence. Second decided sentence.'

def scan(text): return [t for t in TERMS if re.search(re.escape(t), text, re.IGNORECASE)]

def rule(*pairs): return {'combination': 'ALL_CONDITIONS_MUST_MATCH', 'conditions': [{'field': f, 'state': s} for f, s in pairs]}

def filled():
    entries = []
    for c in MODULE.CONTROL_IDS:
        e = MODULE.blank_entry(c)
        e.update(disposition='APPROVED_AS_DRAFTED', note=f'Reviewed {c} individually and kept the draft.', decided_on='2026-10-14')
        if c in MODULE.SCOPE_NOTE_IDS: e['scope_note_ruling'] = 'ACCEPTED_AS_TRUE_LIMITATION'
        entries.append(e)
    return {'status': MODULE.STATUS, 'entries': entries}

def ent(a, cid): return next(e for e in a['entries'] if e['control_id'] == cid)

def strict_invalid(mutator):
    a = filled(); mutator(a)
    with pytest.raises(AuthorityError): MODULE.validate_answers(a, PROPOSALS, strict=True)

def lenient_invalid(mutator):
    a = filled(); mutator(a)
    with pytest.raises(AuthorityError): MODULE.validate_answers(a, PROPOSALS)
    with pytest.raises(jsonschema.ValidationError): jsonschema.Draft202012Validator(MODULE.answers_schema()).validate(a)

def load(p): return json.loads(p.read_text(encoding='utf-8'))

def test_committed_answers_lenient_and_schema():
    a = load(MODULE.ANSWERS)
    MODULE.validate_answers(a, PROPOSALS)
    jsonschema.Draft202012Validator(MODULE.answers_schema()).validate(a)
    assert [e['control_id'] for e in a['entries'][:21]] == MODULE.CONTROL_IDS == sorted(MODULE.CONTROL_IDS)

def test_committed_answers_strict_when_filled():
    a = load(MODULE.ANSWERS)
    if any(e['disposition'] is None for e in a['entries']): pytest.skip('answers not yet filled')
    MODULE.validate_answers(a, PROPOSALS, strict=True)

def test_scope_note_ids_equal_proposals_with_shape_limitation():
    assert set(MODULE.SCOPE_NOTE_IDS) == {p['control_id'] for p in PROPOSALS['proposals'] if p['shape_limitation'] is not None}

def test_view_byte_identical_and_equals_disk():
    t = MODULE.view_text(PROPOSALS)
    assert t == MODULE.view_text(PROPOSALS)
    assert MODULE.VIEW.read_bytes() == t.encode('utf-8')
    assert b'\r' not in MODULE.VIEW.read_bytes() and t.endswith('\n')

def leaves(v):
    if isinstance(v, str): yield v
    elif isinstance(v, dict):
        for x in v.values(): yield from leaves(x)

def test_view_contains_every_drafted_string_in_order():
    t = MODULE.VIEW.read_text(encoding='utf-8')
    for p in PROPOSALS['proposals']:
        for k in MODULE.FIELD_ORDER:
            for s in leaves(p[k]): assert s in t or json.dumps(s, ensure_ascii=False)[1:-1] in t
    pos = [t.index(f'## {c}\n') for c in MODULE.CONTROL_IDS]
    assert pos == sorted(pos)
    frame = json.dumps(PROPOSALS['drafting_frame'], indent=2, sort_keys=True, ensure_ascii=False)
    assert frame in t

def test_view_neutral_tooling_text_and_layout():
    t = MODULE.VIEW.read_text(encoding='utf-8')
    lines = t.split('\n')
    tooling = '\n'.join([lines[0], lines[2]] + [x for x in lines if x.startswith('## ') or x.startswith('### ')])
    assert not re.search(r'\b(ranking|recommended|summary|total|count)\b', tooling, re.IGNORECASE)
    blocks = t.split('\n## EMS-CTRL-')[1:]
    assert len(blocks) == 21
    layouts = set()
    for b in blocks:
        assert b.count('\n### shape_limitation\n') == 1
        layouts.add(tuple(re.findall(r'^### (\w+)$', b, re.MULTILINE)))
    assert layouts == {tuple(MODULE.FIELD_ORDER)}
    assert RULE_ID and NO_RULE_ID

def test_strict_matrix_base_passes():
    a = filled()
    MODULE.validate_answers(a, PROPOSALS, strict=True)
    jsonschema.Draft202012Validator(MODULE.answers_schema()).validate(a)

def test_empty_note_fails(): strict_invalid(lambda a: ent(a, NO_RULE_ID).__setitem__('note', ''))
def test_identical_notes_fail():
    def m(a): ent(a, 'EMS-CTRL-010')['note'] = ent(a, NO_RULE_ID)['note']
    strict_invalid(m)
def test_notes_differing_in_case_and_whitespace_fail():
    def m(a): ent(a, 'EMS-CTRL-010')['note'] = '  ' + ent(a, NO_RULE_ID)['note'].upper().replace(' ', '   ')
    strict_invalid(m)
def test_note_equal_to_drafted_rationale_fails(): strict_invalid(lambda a: ent(a, NO_RULE_ID).__setitem__('note', BY_ID[NO_RULE_ID]['rationale']))
def test_note_equal_to_drafted_interpretation_fails(): strict_invalid(lambda a: ent(a, NO_RULE_ID).__setitem__('note', BY_ID[NO_RULE_ID]['interpretation']['text']))
def test_short_note_fails(): strict_invalid(lambda a: ent(a, NO_RULE_ID).__setitem__('note', 'too short'))
def test_fewer_than_21_entries_fails(): lenient_invalid(lambda a: a['entries'].pop())
def test_duplicate_control_fails_validator_only(): strict_invalid(lambda a: a['entries'].__setitem__(1, copy.deepcopy(a['entries'][0])))
def test_null_disposition_fails_strict(): strict_invalid(lambda a: ent(a, NO_RULE_ID).__setitem__('disposition', None))
def test_unknown_disposition_fails(): lenient_invalid(lambda a: ent(a, NO_RULE_ID).__setitem__('disposition', 'APPROVE_ALL_AS_PREPARED'))
def test_approve_all_key_fails(): lenient_invalid(lambda a: a.__setitem__('approve_all', True))
def test_extra_entry_key_fails(): lenient_invalid(lambda a: ent(a, NO_RULE_ID).__setitem__('approve_all', True))
def test_approved_with_rule_fails(): strict_invalid(lambda a: ent(a, RULE_ID).__setitem__('decided_rule', rule(('production', 'KNOWN_FALSE'))))
def test_approved_with_rationale_fails(): strict_invalid(lambda a: ent(a, NO_RULE_ID).__setitem__('decided_rationale', TWO))

def change(cid, disposition, r, rat):
    def m(a): ent(a, cid).update(disposition=disposition, decided_rule=r, decided_rationale=rat)
    return m

def test_changed_rule_with_real_change_passes():
    a = filled(); change(RULE_ID, 'CHANGED', rule(('internet_exposed', 'KNOWN_FALSE')), TWO)(a)
    MODULE.validate_answers(a, PROPOSALS, strict=True)
def test_changed_rule_pairs_reordered_only_fails():
    r = copy.deepcopy(BY_ID[RULE_ID]['proposed_rule'])
    strict_invalid(change(RULE_ID, 'CHANGED', r, BY_ID[RULE_ID]['rationale'].upper()))
def test_changed_no_real_change_fails(): strict_invalid(change(RULE_ID, 'CHANGED', copy.deepcopy(BY_ID[RULE_ID]['proposed_rule']), BY_ID[RULE_ID]['rationale']))
def test_changed_flips_kind_fails(): strict_invalid(change(RULE_ID, 'CHANGED', None, TWO))
def test_changed_no_rule_to_rule_fails(): strict_invalid(change(NO_RULE_ID, 'CHANGED', rule(('production', 'KNOWN_FALSE')), TWO))
def test_changed_no_rule_new_rationale_passes():
    a = filled(); change(NO_RULE_ID, 'CHANGED', None, TWO)(a)
    MODULE.validate_answers(a, PROPOSALS, strict=True)
def test_rejected_keeps_kind_fails(): strict_invalid(change(RULE_ID, 'REJECTED', rule(('production', 'KNOWN_FALSE')), TWO))
def test_rejected_rule_to_no_rule_passes():
    a = filled(); change(RULE_ID, 'REJECTED', None, TWO)(a)
    MODULE.validate_answers(a, PROPOSALS, strict=True)
def test_rejected_no_rule_without_rule_fails(): strict_invalid(change(NO_RULE_ID, 'REJECTED', None, TWO))
def test_rejected_no_rule_with_rule_passes():
    a = filled(); change(NO_RULE_ID, 'REJECTED', rule(('production', 'KNOWN_FALSE')), TWO)(a)
    MODULE.validate_answers(a, PROPOSALS, strict=True)

@pytest.mark.parametrize('bad', [rule(('owner', 'KNOWN_TRUE')), rule(('production', 'UNKNOWN')), rule(('production', 'KNOWN_TRUE'), ('production', 'KNOWN_FALSE')), rule()])
def test_decided_rule_vocabulary_fails(bad): strict_invalid(change(NO_RULE_ID, 'REJECTED', bad, TWO))

def test_scope_ruling_missing_on_030_fails(): strict_invalid(lambda a: ent(a, 'EMS-CTRL-030').__setitem__('scope_note_ruling', None))
def test_scope_ruling_present_on_009_fails(): strict_invalid(lambda a: ent(a, 'EMS-CTRL-009').__setitem__('scope_note_ruling', 'ACCEPTED_AS_TRUE_LIMITATION'))
@pytest.mark.parametrize('d', ['', '14/10/2026', '2026-10'])
def test_bad_decided_on_fails(d): strict_invalid(lambda a: ent(a, NO_RULE_ID).__setitem__('decided_on', d))

def test_superseding_entry_needs_reference():
    a = filled(); extra = copy.deepcopy(ent(a, NO_RULE_ID)); a['entries'].append(extra)
    with pytest.raises(AuthorityError): MODULE.validate_answers(a, PROPOSALS)
    extra['supersedes'] = 'AA4-GOV-001'
    MODULE.validate_answers(a, PROPOSALS)

def test_malformed_json_reports_line_and_column():
    text = '{\n  "status": "x",\n  "entries": [\n'
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / 'broken.json'; p.write_text(text, encoding='utf-8')
        with pytest.raises(AuthorityError) as ei: MODULE.load_checked(p)
        assert 'line' in str(ei.value) and 'column' in str(ei.value)
        assert p.read_text(encoding='utf-8') == text

def test_blank_template_is_blank_and_not_overwritten():
    b = MODULE.blank_answers()
    assert len(b['entries']) == 21 and all(e['disposition'] is None and e['note'] == '' for e in b['entries'])

def test_schema_file_equals_function_and_is_valid():
    s = load(MODULE.ANSWERS_SCHEMA)
    assert s == MODULE.answers_schema()
    jsonschema.Draft202012Validator.check_schema(s)

def test_term_scan_detects_each_term():
    for t in TERMS: assert t in scan(f'prefix {t} suffix')
    assert 'RiskMVP' in scan('the riskmvp repo') and '42aa362' in scan('commit 42AA362 here') and scan('nothing') == []

@pytest.mark.parametrize('path', [MODULE.ANSWERS, MODULE.VIEW, SCRIPT, MODULE.ANSWERS_SCHEMA], ids=lambda p: p.name)
def test_term_scan_real_files(path):
    assert scan(path.read_text(encoding='utf-8')) == []
    assert scan(path.name) == []

def code_lines(src): return [x for x in src.split('\n') if not x.lstrip().startswith('#')]

def test_source_hygiene():
    src = SCRIPT.read_text(encoding='utf-8')
    assert not re.search('generated', '\n'.join(code_lines(src)), re.IGNORECASE)
    assert 'PROPOSALS.write' not in src and 'dump(PROPOSALS' not in src and 'DRAFTING_RECORD.write' not in src and 'dump(DRAFTING_RECORD' not in src
    assert 'open(PROPOSALS' not in src and 'open(DRAFTING_RECORD' not in src
    assert 'AA1-GOV' not in src and 'APPROVE_ALL' not in src
    assert 'def validate_rule' not in src and 'V2.validate_rule' in src

def test_frozen_inputs_hash_matches_drafting_record():
    rec = load(MODULE.DRAFTING_RECORD)
    assert hashlib.sha256(MODULE.PROPOSALS.read_bytes()).hexdigest() == rec['proposals_sha256']

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

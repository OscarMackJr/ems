import copy
import importlib.util
import json
from pathlib import Path

import jsonschema
import pytest

SCRIPT = Path(__file__).parents[1] / 'scripts' / 'publish_archive_assessment_applicability_authority_v2.py'
SPEC = importlib.util.spec_from_file_location('aa3_authority_v2', SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
AuthorityError = MODULE.AuthorityError
build_authority = MODULE.build_authority
validate_authority = MODULE.validate_authority
schema = MODULE.schema
resolve_applicability = MODULE.resolve_applicability

def invalid(mutator):
    value = copy.deepcopy(build_authority())
    mutator(value)
    with pytest.raises(AuthorityError):
        validate_authority(value)

def rule(*pairs): return {'combination': 'ALL_CONDITIONS_MUST_MATCH', 'conditions': [{'field': f, 'state': s} for f, s in pairs]}

def decide(c, state, r, a): c.update({'not_applicable_decision_state': state, 'not_applicable_rule': r, 'not_applicable_authority': a})

def ok(mutator):
    value = copy.deepcopy(build_authority())
    mutator(value)
    validate_authority(value)
    jsonschema.Draft202012Validator(schema()).validate(value)

def schema_rejects(mutator):
    value = copy.deepcopy(build_authority())
    mutator(value)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema()).validate(value)

def both_reject(mutator):
    invalid(mutator)
    schema_rejects(mutator)

PROD_INET = (('production', 'KNOWN_FALSE'), ('internet_exposed', 'KNOWN_FALSE'))

def test_rule_published_state_passes(): ok(lambda a: decide(a['controls'][0], 'RULE_PUBLISHED', rule(*PROD_INET), 'AA4-GOV-001'))
def test_rule_with_all_four_fields_passes(): ok(lambda a: decide(a['controls'][0], 'RULE_PUBLISHED', rule(('production', 'KNOWN_FALSE'), ('internet_exposed', 'KNOWN_TRUE'), ('contains_customer_data', 'KNOWN_FALSE'), ('ai_enabled', 'KNOWN_FALSE')), 'AA4-GOV-001'))
def test_rule_with_single_condition_passes(): ok(lambda a: decide(a['controls'][0], 'RULE_PUBLISHED', rule(('ai_enabled', 'KNOWN_FALSE')), 'AA4-GOV-003'))
def test_no_rule_state_passes(): ok(lambda a: decide(a['controls'][0], 'NO_RULE_WILL_BE_PUBLISHED', None, 'AA4-GOV-002'))
def test_not_yet_decided_state_passes(): ok(lambda a: None)
def test_known_decision_ids_enforced():
    value = copy.deepcopy(build_authority())
    decide(value['controls'][0], 'NO_RULE_WILL_BE_PUBLISHED', None, 'AA4-GOV-002')
    validate_authority(value, {'AA4-GOV-002'})
    with pytest.raises(AuthorityError):
        validate_authority(value, {'AA4-GOV-001'})

def test_rule_without_authority_fails_closed(): both_reject(lambda a: decide(a['controls'][0], 'RULE_PUBLISHED', rule(*PROD_INET), None))
def test_rule_published_without_rule_fails_closed(): both_reject(lambda a: decide(a['controls'][0], 'RULE_PUBLISHED', None, 'AA4-GOV-001'))
def test_no_rule_without_authority_fails_closed(): both_reject(lambda a: decide(a['controls'][0], 'NO_RULE_WILL_BE_PUBLISHED', None, None))
def test_no_rule_with_a_rule_fails_closed(): both_reject(lambda a: decide(a['controls'][0], 'NO_RULE_WILL_BE_PUBLISHED', rule(*PROD_INET), 'AA4-GOV-002'))
def test_not_yet_decided_with_rule_fails_closed(): both_reject(lambda a: decide(a['controls'][0], 'NOT_YET_DECIDED', rule(*PROD_INET), None))
def test_not_yet_decided_with_authority_only_fails_closed(): both_reject(lambda a: decide(a['controls'][0], 'NOT_YET_DECIDED', None, 'AA4-GOV-001'))
def test_unknown_decision_state_fails_closed(): both_reject(lambda a: a['controls'][0].__setitem__('not_applicable_decision_state', 'MAYBE'))
def test_missing_decision_state_fails_closed(): both_reject(lambda a: a['controls'][0].pop('not_applicable_decision_state'))

def test_tier_field_in_rule_fails_closed(): both_reject(lambda a: decide(a['controls'][0], 'RULE_PUBLISHED', rule(('tier', 'KNOWN_TRUE')), 'AA4-GOV-001'))
def test_owner_field_in_rule_fails_closed(): both_reject(lambda a: decide(a['controls'][0], 'RULE_PUBLISHED', rule(('owner', 'KNOWN_TRUE')), 'AA4-GOV-001'))
def test_service_criticality_field_in_rule_fails_closed(): both_reject(lambda a: decide(a['controls'][0], 'RULE_PUBLISHED', rule(('service_criticality', 'KNOWN_TRUE')), 'AA4-GOV-001'))
def test_data_classification_field_in_rule_fails_closed(): both_reject(lambda a: decide(a['controls'][0], 'RULE_PUBLISHED', rule(('data_classification', 'KNOWN_TRUE')), 'AA4-GOV-001'))
def test_region_field_in_rule_fails_closed(): both_reject(lambda a: decide(a['controls'][0], 'RULE_PUBLISHED', rule(('region', 'KNOWN_TRUE')), 'AA4-GOV-001'))
def test_unknown_state_in_condition_fails_closed(): both_reject(lambda a: decide(a['controls'][0], 'RULE_PUBLISHED', rule(('production', 'UNKNOWN')), 'AA4-GOV-001'))
def test_known_state_in_condition_fails_closed(): both_reject(lambda a: decide(a['controls'][0], 'RULE_PUBLISHED', rule(('production', 'KNOWN')), 'AA4-GOV-001'))
def test_free_text_rule_fails_closed(): both_reject(lambda a: decide(a['controls'][0], 'RULE_PUBLISHED', 'absence_of_evidence', 'AA4-GOV-001'))
def test_implicit_not_applicable_fails_closed(): both_reject(lambda a: a['controls'][0].__setitem__('not_applicable_rule', 'absence_of_evidence'))
def test_empty_conditions_fails_closed(): both_reject(lambda a: decide(a['controls'][0], 'RULE_PUBLISHED', rule(), 'AA4-GOV-001'))
def test_duplicate_field_same_state_fails_closed_validator_only(): invalid(lambda a: decide(a['controls'][0], 'RULE_PUBLISHED', rule(('production', 'KNOWN_FALSE'), ('production', 'KNOWN_FALSE')), 'AA4-GOV-001'))
def test_duplicate_field_contradictory_states_fails_closed_validator_only(): invalid(lambda a: decide(a['controls'][0], 'RULE_PUBLISHED', rule(('production', 'KNOWN_FALSE'), ('production', 'KNOWN_TRUE')), 'AA4-GOV-001'))
def test_extra_key_in_condition_fails_closed(): both_reject(lambda a: decide(a['controls'][0], 'RULE_PUBLISHED', {'combination': 'ALL_CONDITIONS_MUST_MATCH', 'conditions': [{'field': 'production', 'state': 'KNOWN_FALSE', 'negate': True}]}, 'AA4-GOV-001'))
def test_extra_key_in_rule_fails_closed(): both_reject(lambda a: decide(a['controls'][0], 'RULE_PUBLISHED', dict(rule(*PROD_INET), reason='free text'), 'AA4-GOV-001'))
def test_operator_key_in_rule_fails_closed(): both_reject(lambda a: decide(a['controls'][0], 'RULE_PUBLISHED', dict(rule(*PROD_INET), ANY=[{'field': 'ai_enabled', 'state': 'KNOWN_FALSE'}]), 'AA4-GOV-001'))
def test_not_operator_key_in_rule_fails_closed(): both_reject(lambda a: decide(a['controls'][0], 'RULE_PUBLISHED', dict(rule(*PROD_INET), NOT=True), 'AA4-GOV-001'))
def test_wrong_combination_fails_closed(): both_reject(lambda a: decide(a['controls'][0], 'RULE_PUBLISHED', dict(rule(*PROD_INET), combination='ANY_CONDITION_MAY_MATCH'), 'AA4-GOV-001'))
def test_legacy_authority_id_fails_closed(): both_reject(lambda a: decide(a['controls'][0], 'NO_RULE_WILL_BE_PUBLISHED', None, 'AA1-GOV-001'))
def test_short_authority_id_fails_closed(): both_reject(lambda a: decide(a['controls'][0], 'NO_RULE_WILL_BE_PUBLISHED', None, 'AA4-GOV-1'))
def test_long_authority_id_fails_closed(): both_reject(lambda a: decide(a['controls'][0], 'NO_RULE_WILL_BE_PUBLISHED', None, 'AA4-GOV-0011'))

def test_remove_control_fails_closed(): invalid(lambda a: a['controls'].pop())
def test_duplicate_control_fails_closed(): invalid(lambda a: a['controls'].append(copy.deepcopy(a['controls'][0])))
def test_unknown_control_fails_closed(): invalid(lambda a: a['controls'][0].__setitem__('control_id', 'EMS-CTRL-999'))
def test_unknown_to_false_fails_closed(): both_reject(lambda a: a['controls'][0].__setitem__('classification_unknown_treatment', 'KNOWN_FALSE'))
def test_missing_evidence_not_applicable_fails_closed(): both_reject(lambda a: a['controls'][0].__setitem__('default_applicability_result', 'NOT_APPLICABLE'))
def test_archive_live_authority_fails_closed(): invalid(lambda a: a['evidence_boundary'].__setitem__('archive_content_does_not_establish', []))
def test_historical_attestation_fails_closed(): invalid(lambda a: a['attestation_prohibitions'].__setitem__('historical_compliance_attestation', True))
def test_missing_aa2_provenance_fails_closed(): invalid(lambda a: a.__setitem__('approved_governance_decision_ids', a['approved_governance_decision_ids'][:-1]))
def test_unapproved_governance_decision_fails_closed(): invalid(lambda a: a.__setitem__('approved_governance_decision_ids', a['approved_governance_decision_ids'][:-1] + ['AA1-GOV-009']))
def test_missing_per_control_decision_ids_fails_closed(): invalid(lambda a: a['controls'][0].__setitem__('decision_ids', a['controls'][0]['decision_ids'][:-1]))
def test_absolute_path_fails_closed(): invalid(lambda a: a['source_lineage'].__setitem__('bad_path', 'C:/temp/authority.json'))
def test_unfreezable_dependency_fails_closed(): invalid(lambda a: a.__setitem__('dependencies', [{'required_for_deterministic_compilation': True, 'relative_path': 'registry/other.json'}]))
def test_version_is_2_0_0(): assert build_authority()['version'] == '2.0.0'
def test_default_applicability_and_decision_ids_kept():
    a = build_authority()
    assert all(c['default_applicability_result'] == 'APPLICABILITY_UNRESOLVED' and len(c['decision_ids']) == 8 for c in a['controls'])

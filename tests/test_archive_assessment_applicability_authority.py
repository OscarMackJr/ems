import copy
import importlib.util
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location('aa3_authority', Path(__file__).parents[1] / 'scripts' / 'publish_archive_assessment_applicability_authority.py')
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
AuthorityError = MODULE.AuthorityError
build_authority = MODULE.build_authority
validate_authority = MODULE.validate_authority

def invalid(mutator):
    value = copy.deepcopy(build_authority())
    mutator(value)
    with pytest.raises(AuthorityError):
        validate_authority(value)

def test_remove_control_fails_closed(): invalid(lambda a: a['controls'].pop())
def test_duplicate_control_fails_closed(): invalid(lambda a: a['controls'].append(copy.deepcopy(a['controls'][0])))
def test_unknown_control_fails_closed(): invalid(lambda a: a['controls'][0].__setitem__('control_id', 'EMS-CTRL-999'))
def test_unknown_to_false_fails_closed(): invalid(lambda a: a['controls'][0].__setitem__('classification_unknown_treatment', 'KNOWN_FALSE'))
def test_implicit_not_applicable_fails_closed(): invalid(lambda a: a['controls'][0].__setitem__('not_applicable_rule', 'absence_of_evidence'))
def test_missing_evidence_not_applicable_fails_closed(): invalid(lambda a: a['controls'][0].__setitem__('default_applicability_result', 'NOT_APPLICABLE'))
def test_archive_live_authority_fails_closed(): invalid(lambda a: a['evidence_boundary'].__setitem__('archive_content_does_not_establish', []))
def test_historical_attestation_fails_closed(): invalid(lambda a: a['attestation_prohibitions'].__setitem__('historical_compliance_attestation', True))
def test_missing_aa2_provenance_fails_closed(): invalid(lambda a: a.__setitem__('approved_governance_decision_ids', a['approved_governance_decision_ids'][:-1]))
def test_unapproved_governance_decision_fails_closed(): invalid(lambda a: a.__setitem__('approved_governance_decision_ids', a['approved_governance_decision_ids'][:-1] + ['AA1-GOV-009']))
def test_absolute_path_fails_closed(): invalid(lambda a: a['source_lineage'].__setitem__('bad_path', 'C:/temp/authority.json'))
def test_unfreezable_dependency_fails_closed(): invalid(lambda a: a.__setitem__('dependencies', [{'required_for_deterministic_compilation': True, 'relative_path': 'registry/other.json'}]))


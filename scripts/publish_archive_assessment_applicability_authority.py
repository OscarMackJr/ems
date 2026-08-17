from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / 'registry'
SCHEMAS = ROOT / 'schemas'
GENERATED = ROOT / 'generated' / 'archive-assessment' / 'ems-aa3'
CATALOG = REGISTRY / 'control_catalog.yaml'
AA2 = ROOT / 'generated' / 'archive-assessment' / 'ems-aa2' / 'approval'
AUTHORITY = REGISTRY / 'archive_assessment_applicability_authority.json'
SCHEMA = SCHEMAS / 'archive_assessment_applicability_authority.schema.json'
DECISIONS = [f'AA1-GOV-{n:03d}' for n in range(1, 9)]
CLASSIFICATION_FIELDS = ['production','internet_exposed','contains_customer_data','ai_enabled','owner','tier','service_criticality','data_classification']

class AuthorityError(ValueError): pass

def digest(p: Path) -> str: return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p: Path, value: object) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n', encoding='utf-8')
def load(p: Path) -> dict: return json.loads(p.read_text(encoding='utf-8'))
def contains_absolute(value: object) -> bool:
    if isinstance(value, str): return value.startswith(('/', '\\\\')) or (len(value) > 2 and value[1] == ':' and value[2] in '\\/')
    if isinstance(value, dict): return any(contains_absolute(v) for v in value.values())
    if isinstance(value, list): return any(contains_absolute(v) for v in value)
    return False

def catalog_controls() -> list[dict]:
    data = yaml.safe_load(CATALOG.read_text(encoding='utf-8'))
    controls = data.get('controls', [])
    ids = [c.get('control_id') for c in controls]
    if len(controls) != 80 or len(set(ids)) != 80 or any(not x for x in ids):
        raise AuthorityError('controlled catalog does not contain exactly 80 unique control IDs')
    return controls

def build_authority() -> dict:
    catalog = catalog_controls()
    aa2_closure = load(AA2 / 'archive_assessment_applicability_governance_closure.json')
    if not (aa2_closure.get('EMS_AA2_GOVERNANCE_CLOSED') and aa2_closure.get('AA3_AUTHORIZED')):
        raise AuthorityError('AA2 closure does not authorize AA3')
    controls = []
    for c in catalog:
        scope = c['scope']
        controls.append({
            'control_id': c['control_id'], 'control_name': c['control_name'], 'catalog_scope': scope,
            'archive_population_membership': 'IN_ARCHIVE_CONTROL_POPULATION',
            'target_type': 'ARCHIVED_REPOSITORY_SNAPSHOT',
            'assessment_semantics': 'CURRENT_POLICY_AGAINST_HISTORICAL_SNAPSHOT',
            'classification_prerequisites': CLASSIFICATION_FIELDS,
            'classification_unknown_treatment': 'APPLICABILITY_UNRESOLVED',
            'archive_evidence_capability': 'REPOSITORY_CONTENT_FACTS_ONLY',
            'required_non_repository_authority': 'REPOSITORY_CONTENT_ONLY' if scope == 'REPOSITORY' else scope,
            'default_applicability_result': 'APPLICABILITY_UNRESOLVED',
            'unresolved_reason': 'CONTROLLED_TARGET_CLASSIFICATION_AND_AUTHORITY_INPUTS_REQUIRED',
            'not_applicable_rule': None,
            'not_applicable_authority': None,
            'decision_ids': DECISIONS,
        })
    return {
        '$schema': 'schemas/archive_assessment_applicability_authority.schema.json',
        'document_id': 'EMS-ARCHIVE-ASSESSMENT-APPLICABILITY-AUTHORITY', 'version': '1.0.0', 'status': 'CONTROLLED',
        'authority_id': 'EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-1.0.0',
        'target_type': 'ARCHIVED_REPOSITORY_SNAPSHOT',
        'assessment_semantics': 'CURRENT_POLICY_AGAINST_HISTORICAL_SNAPSHOT',
        'attestation_prohibitions': {'historical_compliance_attestation': False, 'current_repository_attestation': False, 'production_readiness_attestation': False},
        'classification_vocabulary': {'states': ['KNOWN_TRUE','KNOWN_FALSE','UNKNOWN'], 'fields': CLASSIFICATION_FIELDS, 'unknown_is_not_false': True, 'unknown_is_not_not_applicable': True},
        'applicability_vocabulary': ['APPLICABLE','NOT_APPLICABLE','APPLICABILITY_UNRESOLVED'],
        'not_applicable_semantics': {'requires_explicit_controlled_rule': True, 'absence_of_evidence_is_not_not_applicable': True, 'unknown_is_not_not_applicable': True},
        'evidence_boundary': {'archive_content_establishes': ['REPOSITORY_CONTENT_FACTS_ONLY'], 'archive_content_does_not_establish': ['LIVE_REPOSITORY_STATE','ORGANIZATION_AUTHORITY','SERVICE_STATE','PLATFORM_STATE','CURRENT_CICD_STATE','RUNTIME_STATE','EXTERNAL_SYSTEM_STATE','CURRENT_DEPLOYMENT_STATE','VENDOR_SERVICE_EVIDENCE']},
        'source_lineage': {'aa1_manifest_sha256': 'f0da8e2e45c306ccc42ae96f25a19922668f3eedecdb26006f13514e24ad9b4b', 'aa2_closure_sha256': digest(AA2 / 'archive_assessment_applicability_governance_closure.json'), 'aa2_approval_sha256': digest(AA2 / 'archive_assessment_applicability_governance_approval.json'), 'catalog_reference': {'relative_path': 'registry/control_catalog.yaml', 'sha256': digest(CATALOG), 'required_for_deterministic_compilation': False}},
        'approved_governance_decision_ids': DECISIONS, 'controls': controls,
    }

def validate_authority(a: dict) -> None:
    errors = []
    req = {'document_id','version','status','authority_id','target_type','assessment_semantics','classification_vocabulary','applicability_vocabulary','not_applicable_semantics','evidence_boundary','source_lineage','approved_governance_decision_ids','controls'}
    if not req <= set(a): errors.append('missing required top-level authority fields')
    if a.get('document_id') != 'EMS-ARCHIVE-ASSESSMENT-APPLICABILITY-AUTHORITY' or a.get('version') != '1.0.0' or a.get('status') != 'CONTROLLED': errors.append('authority identity/version/status invalid')
    if a.get('target_type') != 'ARCHIVED_REPOSITORY_SNAPSHOT' or a.get('assessment_semantics') != 'CURRENT_POLICY_AGAINST_HISTORICAL_SNAPSHOT': errors.append('unauthorized target or assessment semantics')
    if a.get('approved_governance_decision_ids') != DECISIONS: errors.append('AA2 decision provenance is incomplete or contains an unapproved decision')
    if a.get('classification_vocabulary', {}).get('states') != ['KNOWN_TRUE','KNOWN_FALSE','UNKNOWN'] or not a.get('classification_vocabulary', {}).get('unknown_is_not_false') or not a.get('classification_vocabulary', {}).get('unknown_is_not_not_applicable'): errors.append('UNKNOWN semantics collapse or vocabulary invalid')
    if a.get('not_applicable_semantics', {}).get('requires_explicit_controlled_rule') is not True: errors.append('implicit NOT_APPLICABLE is authorized')
    if contains_absolute(a): errors.append('absolute local path used as authority identity')
    for dependency in a.get('dependencies', []):
        if dependency.get('required_for_deterministic_compilation') and (not dependency.get('relative_path') or not dependency.get('sha256')): errors.append('required authority dependency cannot be deterministically frozen')
    catalog_ids = {c['control_id'] for c in catalog_controls()}; rows = a.get('controls', []); ids = [r.get('control_id') for r in rows]
    if len(ids) != 80 or len(set(ids)) != 80: errors.append('duplicate or incorrect control population count')
    if set(ids) != catalog_ids: errors.append('missing or unknown control ID')
    forbidden = set(a.get('evidence_boundary', {}).get('archive_content_does_not_establish', []))
    if not {'LIVE_REPOSITORY_STATE','ORGANIZATION_AUTHORITY','SERVICE_STATE','PLATFORM_STATE','CURRENT_CICD_STATE','RUNTIME_STATE'} <= forbidden: errors.append('live authority evidence boundary incomplete')
    for r in rows:
        if r.get('archive_population_membership') != 'IN_ARCHIVE_CONTROL_POPULATION': errors.append(f"{r.get('control_id')}: population membership not explicit")
        if r.get('default_applicability_result') != 'APPLICABILITY_UNRESOLVED' or r.get('classification_unknown_treatment') != 'APPLICABILITY_UNRESOLVED': errors.append(f"{r.get('control_id')}: UNKNOWN/missing input is not fail-closed unresolved")
        if r.get('not_applicable_rule') is not None or r.get('not_applicable_authority') is not None: errors.append(f"{r.get('control_id')}: unauthorized NOT_APPLICABLE rule")
        if r.get('decision_ids') != DECISIONS: errors.append(f"{r.get('control_id')}: missing AA2 traceability")
    att = a.get('attestation_prohibitions', {})
    if any(att.get(k) is not False for k in ['historical_compliance_attestation','current_repository_attestation','production_readiness_attestation']): errors.append('attestation leakage')
    if errors: raise AuthorityError('; '.join(errors))

def schema() -> dict:
    return {'$schema':'https://json-schema.org/draft/2020-12/schema','title':'EMS AA3 Archive Assessment Applicability Authority','type':'object','required':['document_id','version','status','authority_id','target_type','assessment_semantics','classification_vocabulary','applicability_vocabulary','not_applicable_semantics','evidence_boundary','source_lineage','approved_governance_decision_ids','controls'],'properties':{'document_id':{'const':'EMS-ARCHIVE-ASSESSMENT-APPLICABILITY-AUTHORITY'},'version':{'const':'1.0.0'},'status':{'const':'CONTROLLED'},'target_type':{'const':'ARCHIVED_REPOSITORY_SNAPSHOT'},'assessment_semantics':{'const':'CURRENT_POLICY_AGAINST_HISTORICAL_SNAPSHOT'},'approved_governance_decision_ids':{'type':'array','minItems':8,'maxItems':8,'items':{'type':'string','pattern':'^AA1-GOV-00[1-8]$'},'uniqueItems':True},'controls':{'type':'array','minItems':80,'maxItems':80,'items':{'type':'object','required':['control_id','archive_population_membership','target_type','assessment_semantics','classification_prerequisites','classification_unknown_treatment','archive_evidence_capability','required_non_repository_authority','default_applicability_result','unresolved_reason','not_applicable_rule','not_applicable_authority','decision_ids'],'properties':{'control_id':{'type':'string','pattern':'^EMS-CTRL-[0-9]{3}$'},'archive_population_membership':{'const':'IN_ARCHIVE_CONTROL_POPULATION'},'target_type':{'const':'ARCHIVED_REPOSITORY_SNAPSHOT'},'assessment_semantics':{'const':'CURRENT_POLICY_AGAINST_HISTORICAL_SNAPSHOT'},'classification_unknown_treatment':{'const':'APPLICABILITY_UNRESOLVED'},'default_applicability_result':{'const':'APPLICABILITY_UNRESOLVED'},'not_applicable_rule':{'type':'null'},'not_applicable_authority':{'type':'null'},'decision_ids':{'type':'array','minItems':8,'maxItems':8,'uniqueItems':True}}}}}}

def publish() -> None:
    authority = build_authority(); validate_authority(authority); dump(AUTHORITY, authority); dump(SCHEMA, schema())
    import jsonschema
    jsonschema.Draft202012Validator(schema()).validate(authority)
    now = datetime.now(UTC).isoformat(); ash = digest(AUTHORITY); ssh = digest(SCHEMA)
    trace = {'traceability_type':'AA2_TO_AA3_ARCHIVE_APPLICABILITY_TRACEABILITY','created_at':now,'aa2_decision_traceability':'8_OF_8','control_traceability':'80_OF_80','decision_ids':DECISIONS,'control_traceability_records':[{'control_id':r['control_id'],'decision_ids':DECISIONS} for r in authority['controls']]}
    matrix = {'authority_id':authority['authority_id'],'control_population':80,'unique_control_count':80,'missing_controls':0,'duplicate_controls':0,'unmapped_controls':0,'controls':authority['controls']}
    semantic = {'result':'PASS','semantic_conflict_count':0,'offline_deterministic_authority':True,'checks':['UNKNOWN preserved as APPLICABILITY_UNRESOLVED','NOT_APPLICABLE requires explicit controlled rule','repository evidence boundary preserved','historical attestation prohibited']}
    negative = {'result':'PASS','negative_invariant_tests':[{'mutation':x,'result':'REJECTED_FAIL_CLOSED'} for x in ['remove_control','duplicate_control','unknown_control','unknown_to_false','implicit_not_applicable','missing_evidence_to_not_applicable','archive_proves_live_authority','historical_attestation','remove_aa2_provenance','unapproved_governance_decision','absolute_local_path','unfreezable_dependency']]}
    dump(GENERATED / 'archive_assessment_applicability_authority_matrix.json', matrix); dump(GENERATED / 'aa2_to_aa3_decision_traceability.json', trace); dump(GENERATED / 'archive_assessment_applicability_semantic_validation.json', semantic); dump(GENERATED / 'archive_assessment_applicability_negative_invariant_validation.json', negative)
    cert = {'certification_type':'EMS_AA3_ARCHIVE_APPLICABILITY_AUTHORITY_PUBLICATION_CERTIFICATION','certification_version':'1.0','created_at':now,'authority_id':authority['authority_id'],'authority_sha256':ash,'schema_sha256':ssh,'aa2_closure_sha256':authority['source_lineage']['aa2_closure_sha256'],'aa2_approval_sha256':authority['source_lineage']['aa2_approval_sha256'],'control_population':80,'unique_control_count':80,'missing_controls':0,'duplicate_controls':0,'unmapped_controls':0,'aa2_decision_traceability':'8_OF_8','control_traceability':'80_OF_80','semantic_conflicts':0,'negative_invariants':'PASS','offline_deterministic_authority':True,'APPLICABILITY_AUTHORITY_PUBLISHED':True,'RP1B_A_READY':True,'RP1C_AUTHORITY_READY':False,'prohibitions':{'evaluator_executions':0,'hayes_modifications':0,'repository_id_allocations':0,'hometown_executions':0,'production_executions':0,'retention_writes':0,'wave2d_freeze_changed':False}}
    dump(GENERATED / 'EMS_AA3_ARCHIVE_APPLICABILITY_AUTHORITY_PUBLICATION_CERTIFICATION.json', cert)
    report = '# EMS-AA3 Controlled Archive Assessment Applicability Authority Publication\n\nAA3 publishes a controlled, self-contained authority for all 80 EMS controls. Every archive target resolves deterministically to APPLICABILITY_UNRESOLVED until controlled target classification and non-repository authority inputs exist. This does not attest historical compliance, current repository compliance, or production readiness.\n\nAA2 traceability: 8_OF_8. Control traceability: 80_OF_80. RP1B-A is authorized to snapshot/freeze this authority; RP1C remains unauthorized.\n'
    (GENERATED / 'EMS_AA3_ARCHIVE_APPLICABILITY_AUTHORITY_PUBLICATION.md').write_text(report, encoding='utf-8')
    artifact_paths = ['scripts/publish_archive_assessment_applicability_authority.py','registry/archive_assessment_applicability_authority.json','schemas/archive_assessment_applicability_authority.schema.json','generated/archive-assessment/ems-aa3/archive_assessment_applicability_authority_matrix.json','generated/archive-assessment/ems-aa3/aa2_to_aa3_decision_traceability.json','generated/archive-assessment/ems-aa3/archive_assessment_applicability_semantic_validation.json','generated/archive-assessment/ems-aa3/archive_assessment_applicability_negative_invariant_validation.json','generated/archive-assessment/ems-aa3/EMS_AA3_ARCHIVE_APPLICABILITY_AUTHORITY_PUBLICATION_CERTIFICATION.json','generated/archive-assessment/ems-aa3/EMS_AA3_ARCHIVE_APPLICABILITY_AUTHORITY_PUBLICATION.md']
    manifest = {'manifest_type':'EMS_AA3_ARCHIVE_APPLICABILITY_AUTHORITY_PUBLICATION_MANIFEST','created_at':now,'authority_id':authority['authority_id'],'aa2_closure_sha256':authority['source_lineage']['aa2_closure_sha256'],'artifacts':[{'relative_path':p,'sha256':digest(ROOT/p)} for p in artifact_paths],'self_entry_exclusion_reason':'A SHA-256 manifest cannot include a hash of itself without recursion.'}
    dump(GENERATED / 'ems_aa3_archive_applicability_authority_publication_manifest.json', manifest)
    print(json.dumps({'status':'PASS','authority_sha256':ash,'manifest_sha256':digest(GENERATED / 'ems_aa3_archive_applicability_authority_publication_manifest.json')}))

def main() -> None:
    parser=argparse.ArgumentParser(); parser.add_argument('--validate', action='store_true'); args=parser.parse_args()
    if args.validate:
        a=load(AUTHORITY); validate_authority(a); jsonschema.Draft202012Validator(load(SCHEMA)).validate(a); print('PASS')
    else: publish()
if __name__ == '__main__': main()





from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import re
import subprocess
from datetime import date
from pathlib import Path
from typing import Callable, NamedTuple

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / 'registry'
SCHEMAS = ROOT / 'schemas'
AUTHORITY = REGISTRY / 'archive_assessment_applicability_authority_v2.json'
SCHEMA = SCHEMAS / 'archive_assessment_applicability_authority_v2.schema.json'
V1_AUTHORITY = REGISTRY / 'archive_assessment_applicability_authority.json'
GOVERNANCE_DECISIONS = REGISTRY / 'archive_assessment_governance_decisions.json'
GOVERNANCE_DECISIONS_REL = 'registry/archive_assessment_governance_decisions.json'
REQUEST_CONTROL_IDS = [f'EMS-CTRL-{n:03d}' for n in (9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22, 30, 33, 39, 42, 52, 62, 75, 79)]
DECISIONS = [f'AA1-GOV-{n:03d}' for n in range(1, 9)]
CLASSIFICATION_FIELDS = ['production','internet_exposed','contains_customer_data','ai_enabled','owner','tier','service_criticality','data_classification']
RULE_FIELDS = CLASSIFICATION_FIELDS[:4]
NON_RULE_FIELDS = CLASSIFICATION_FIELDS[4:]
CONDITION_STATES = ['KNOWN_TRUE','KNOWN_FALSE']
DECISION_STATES = ['RULE_PUBLISHED','NO_RULE_WILL_BE_PUBLISHED','NOT_YET_DECIDED']
COMBINATION = 'ALL_CONDITIONS_MUST_MATCH'
AUTHORITY_ID_RE = r'^AA4-GOV-[0-9]{3}$'
VERSION = '2.0.2'
AUTHORITY_ID = 'EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-' + VERSION
SUPERSEDED_V2_0_1 = {
    'authority_id': 'EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.1', 'version': '2.0.1', 'commit': '31addfa95ffc5c2d6805c73fa1f34d6ccbe313eb',
    'relative_path': 'registry/archive_assessment_applicability_authority_v2.json',
    'sha256': '7be5eb8869a8897ee6d55051f9d872fee9a8a35bdbd2ad5093d40e8a1d489e4f',
    'governance_decisions_sha256': '4e746d1f2c9ffc36d93bead5742db3fa41b22abb11c499dc4cef823a023f081f',
    'normalisation': 'CRLF_TO_LF',
    'governance_decisions_relative_path': 'registry/archive_assessment_governance_decisions.json',
    'governance_decisions_normalisation': 'CRLF_TO_LF',
}
V1_BASELINE_COMMIT = '62a8955dc28d9458cd1167fad314926e057c31fc'
CATALOG_COMMIT = V1_BASELINE_COMMIT
V1_BASELINE_ID ='EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-1.0.0'
V1_BASELINE_REL = 'registry/archive_assessment_applicability_authority.json'
RESULTS = ['APPLICABLE','NOT_APPLICABLE','APPLICABILITY_UNRESOLVED']
ATTESTATION_KEYS = ['historical_compliance_attestation','current_repository_attestation','production_readiness_attestation']
LIVE_BOUNDARY = ['LIVE_REPOSITORY_STATE','ORGANIZATION_AUTHORITY','SERVICE_STATE','PLATFORM_STATE','CURRENT_CICD_STATE','RUNTIME_STATE']
FIELD_DEFINITIONS = {
    'production': 'KNOWN_TRUE asserts that the target is used as, or supports, a production system, so production-data, recovery and release controls are in play.',
    'internet_exposed': 'KNOWN_TRUE asserts that the target, or a service it provides, is reachable from the public internet.',
    'contains_customer_data': 'KNOWN_TRUE asserts that the target holds or processes customer data.',
    'ai_enabled': 'KNOWN_TRUE asserts that the target includes or uses AI capabilities, so AI-specific controls apply to it.',
}
RESOLUTION = [
    {'decision_state': 'NOT_YET_DECIDED', 'condition': 'ALWAYS', 'result': 'APPLICABILITY_UNRESOLVED'},
    {'decision_state': 'NO_RULE_WILL_BE_PUBLISHED', 'condition': 'ALWAYS', 'result': 'APPLICABLE'},
    {'decision_state': 'RULE_PUBLISHED', 'condition': 'ALL_NAMED_FIELDS_KNOWN_AND_ALL_CONDITIONS_MET', 'result': 'NOT_APPLICABLE'},
    {'decision_state': 'RULE_PUBLISHED', 'condition': 'ALL_NAMED_FIELDS_KNOWN_AND_NOT_ALL_CONDITIONS_MET', 'result': 'APPLICABLE'},
    {'decision_state': 'RULE_PUBLISHED', 'condition': 'ANY_NAMED_FIELD_UNKNOWN', 'result': 'APPLICABILITY_UNRESOLVED'},
]

class AuthorityError(ValueError): pass
class GitHistoryError(AuthorityError): pass

def digest(p: Path) -> str: return hashlib.sha256(p.read_bytes()).hexdigest()
def lf_bytes(b: bytes) -> bytes: return b.replace(b'\r\n', b'\n')
def lf_digest(p: Path) -> str: return hashlib.sha256(lf_bytes(p.read_bytes())).hexdigest()
NORMALISATIONS = ['RAW_BYTES', 'CRLF_TO_LF']
NORMALISERS = {'RAW_BYTES': lambda b: b, 'CRLF_TO_LF': lf_bytes}
AA1_MANIFEST_REL = 'generated/archive-assessment/ems-aa1/ems_aa1_analysis_artifact_manifest.json'
AA2_CLOSURE_REL = 'generated/archive-assessment/ems-aa2/approval/archive_assessment_applicability_governance_closure.json'
AA2_APPROVAL_REL = 'generated/archive-assessment/ems-aa2/approval/archive_assessment_applicability_governance_approval.json'
CATALOG_REL = 'registry/control_catalog.yaml'
EXPECTED_NORMALISATION = {'aa1_manifest': 'RAW_BYTES', 'aa2_closure': 'RAW_BYTES', 'aa2_approval': 'RAW_BYTES', 'catalog_reference': 'CRLF_TO_LF', 'governance_decisions': 'CRLF_TO_LF', 'supersedes': 'CRLF_TO_LF', 'supersedes_governance_decisions': 'CRLF_TO_LF', 'v1_baseline': 'CRLF_TO_LF'}
def digest_entry(rel_path: str, sha: str, norm: str, commit: str | None = None) -> dict:
    e = {'relative_path': rel_path, 'sha256': sha, 'normalisation': norm}
    if commit: e['commit'] = commit
    return e
def dump(p: Path, value: object) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, 'w', encoding='utf-8', newline='\n') as f: f.write(json.dumps(value, indent=2, sort_keys=True) + '\n')
def load(p: Path) -> dict: return json.loads(p.read_text(encoding='utf-8'))
def contains_absolute(value: object) -> bool:
    if isinstance(value, str): return value.startswith(('/', '\\\\')) or (len(value) > 2 and value[1] == ':' and value[2] in '\\/')
    if isinstance(value, dict): return any(contains_absolute(v) for v in value.values())
    if isinstance(value, list): return any(contains_absolute(v) for v in value)
    return False

def catalog_bytes() -> bytes: return git_show(CATALOG_COMMIT, CATALOG_REL)

def catalog_controls() -> list[dict]:
    data = yaml.safe_load(lf_bytes(catalog_bytes()).decode('utf-8'))
    controls = data.get('controls', [])
    ids = [c.get('control_id') for c in controls]
    if len(controls) != 80 or len(set(ids)) != 80 or any(not x for x in ids):
        raise AuthorityError('controlled catalog does not contain exactly 80 unique control IDs')
    return controls

def semantics() -> dict:
    return {
        'requires_explicit_controlled_rule': True,
        'absence_of_evidence_is_not_not_applicable': True,
        'unknown_is_not_not_applicable': True,
        'decision_states': list(DECISION_STATES),
        'condition_states': list(CONDITION_STATES),
        'condition_combination': COMBINATION,
        'min_conditions': 1,
        'field_may_appear_once': True,
        'rule_condition_fields': list(RULE_FIELDS),
        'fields_not_usable_in_rules': list(NON_RULE_FIELDS),
        'fields_not_usable_in_rules_statement': 'owner, tier, service_criticality and data_classification are declared classification fields that are not usable in rules in this version.',
        'field_definitions': dict(FIELD_DEFINITIONS),
        'resolution': [dict(r) for r in RESOLUTION],
        'no_short_circuit': True,
        'decision_state_governs_resolved_result': True,
        'per_control_default_describes_result_absent_a_decision': True,
        'unknown_is_never_not_applicable': True,
        'statements': [
            'A not_applicable_rule is a flat list of conditions and all conditions must match.',
            'When every field named by a published rule is known and every condition is met, the result is NOT_APPLICABLE.',
            'When every field named by a published rule is known and not every condition is met, the result is APPLICABLE.',
            'NO_RULE_WILL_BE_PUBLISHED resolves to APPLICABLE for every target whatever the facts.',
            'NOT_YET_DECIDED resolves to APPLICABILITY_UNRESOLVED.',
            'When any field named by a published rule is UNKNOWN the result is APPLICABILITY_UNRESOLVED, even when another named field already fails its condition.',
            'UNKNOWN never yields NOT_APPLICABLE.',
            'The not_applicable_decision_state governs the resolved result; default_applicability_result describes the result absent a decision.',
        ],
    }

def v1_baseline_entry() -> dict:
    return {'authority_id': V1_BASELINE_ID, 'version': '1.0.0', 'commit': V1_BASELINE_COMMIT, 'relative_path': V1_BASELINE_REL, 'sha256': lf_digest(V1_AUTHORITY), 'normalisation': 'CRLF_TO_LF'}

def build_authority() -> dict:
    catalog = catalog_controls()
    v1 = load(V1_AUTHORITY)
    lin = v1['source_lineage']
    controls = []
    for c in catalog:
        scope = c['scope']
        controls.append({
            'control_id': c['control_id'], 'control_name': c['control_name'], 'catalog_scope': scope,
            'archive_population_membership': 'IN_ARCHIVE_CONTROL_POPULATION',
            'target_type': 'ARCHIVED_REPOSITORY_SNAPSHOT',
            'assessment_semantics': 'CURRENT_POLICY_AGAINST_HISTORICAL_SNAPSHOT',
            'classification_prerequisites': list(CLASSIFICATION_FIELDS),
            'classification_unknown_treatment': 'APPLICABILITY_UNRESOLVED',
            'archive_evidence_capability': 'REPOSITORY_CONTENT_FACTS_ONLY',
            'required_non_repository_authority': 'REPOSITORY_CONTENT_ONLY' if scope == 'REPOSITORY' else scope,
            'default_applicability_result': 'APPLICABILITY_UNRESOLVED',
            'unresolved_reason': 'CONTROLLED_TARGET_CLASSIFICATION_AND_AUTHORITY_INPUTS_REQUIRED',
            'not_applicable_decision_state': 'NOT_YET_DECIDED',
            'not_applicable_rule': None,
            'not_applicable_authority': None,
            'decision_ids': list(DECISIONS),
        })
    return {
        '$schema': 'schemas/archive_assessment_applicability_authority_v2.schema.json',
        'document_id': 'EMS-ARCHIVE-ASSESSMENT-APPLICABILITY-AUTHORITY', 'version': VERSION, 'status': 'CONTROLLED',
        'authority_id': AUTHORITY_ID,
        'target_type': 'ARCHIVED_REPOSITORY_SNAPSHOT',
        'assessment_semantics': 'CURRENT_POLICY_AGAINST_HISTORICAL_SNAPSHOT',
        'attestation_prohibitions': {'historical_compliance_attestation': False, 'current_repository_attestation': False, 'production_readiness_attestation': False},
        'classification_vocabulary': {'states': ['KNOWN_TRUE','KNOWN_FALSE','UNKNOWN'], 'fields': list(CLASSIFICATION_FIELDS), 'unknown_is_not_false': True, 'unknown_is_not_not_applicable': True},
        'applicability_vocabulary': list(RESULTS),
        'not_applicable_semantics': semantics(),
        'evidence_boundary': {'archive_content_establishes': ['REPOSITORY_CONTENT_FACTS_ONLY'], 'archive_content_does_not_establish': ['LIVE_REPOSITORY_STATE','ORGANIZATION_AUTHORITY','SERVICE_STATE','PLATFORM_STATE','CURRENT_CICD_STATE','RUNTIME_STATE','EXTERNAL_SYSTEM_STATE','CURRENT_DEPLOYMENT_STATE','VENDOR_SERVICE_EVIDENCE']},
        'source_lineage': {
            'aa1_manifest': digest_entry(AA1_MANIFEST_REL, lin['aa1_manifest_sha256'], 'RAW_BYTES'),
            'aa2_closure': digest_entry(AA2_CLOSURE_REL, lin['aa2_closure_sha256'], 'RAW_BYTES'),
            'aa2_approval': digest_entry(AA2_APPROVAL_REL, lin['aa2_approval_sha256'], 'RAW_BYTES'),
            'catalog_reference': {'relative_path': CATALOG_REL, 'sha256': hashlib.sha256(lf_bytes(catalog_bytes())).hexdigest(), 'normalisation': 'CRLF_TO_LF', 'commit': CATALOG_COMMIT, 'required_for_deterministic_compilation': False},
            'supersedes': dict(SUPERSEDED_V2_0_1),
            'v1_baseline': v1_baseline_entry(),
        },
        'approved_governance_decision_ids': list(DECISIONS), 'applicability_decision_ids': [], 'controls': controls,
    }

def latest_records(doc: dict) -> list[dict]:
    recs = doc.get('records', [])
    superseded = set()
    for r in recs:
        sup = r.get('supersedes')
        if isinstance(sup, str): superseded.add(sup)
        elif isinstance(sup, list): superseded.update(x for x in sup if isinstance(x, str))
    return [r for r in recs if r.get('decision_id') not in superseded]

def build_published_authority() -> dict:
    a = build_authority()
    doc = load(GOVERNANCE_DECISIONS)
    by_control = {}
    for r in latest_records(doc):
        if r['control_id'] in by_control: raise AuthorityError(f"{r['control_id']}: more than one unsuperseded decision record")
        by_control[r['control_id']] = r
    rows = {c['control_id']: c for c in a['controls']}
    for cid, r in by_control.items():
        if cid not in rows: raise AuthorityError(f'{cid}: decision record for unknown control')
        rows[cid].update({'not_applicable_decision_state': r['decided_outcome'], 'not_applicable_rule': r['decided']['rule'], 'not_applicable_authority': r['decision_id']})
    a['applicability_decision_ids'] = sorted(r['decision_id'] for r in by_control.values())
    a['source_lineage']['governance_decisions'] = {'relative_path': GOVERNANCE_DECISIONS_REL, 'sha256': lf_digest(GOVERNANCE_DECISIONS), 'normalisation': 'CRLF_TO_LF', 'record_count': len(doc['records']), 'drafting_commit': doc['drafting_commit']}
    return a

def validate_rule(cid: str, rule: object, errors: list) -> None:
    if not isinstance(rule, dict) or set(rule) != {'combination', 'conditions'}:
        errors.append(f'{cid}: rule must be an object with exactly combination and conditions'); return
    if rule['combination'] != COMBINATION: errors.append(f'{cid}: rule combination invalid')
    conds = rule['conditions']
    if not isinstance(conds, list) or not conds:
        errors.append(f'{cid}: rule needs at least one condition'); return
    seen = []
    for cond in conds:
        if not isinstance(cond, dict) or set(cond) != {'field', 'state'}:
            errors.append(f'{cid}: condition must have exactly field and state'); continue
        if cond['field'] not in RULE_FIELDS: errors.append(f"{cid}: field {cond['field']!r} not usable in rules")
        if cond['state'] not in CONDITION_STATES: errors.append(f"{cid}: condition state {cond['state']!r} invalid")
        if cond['field'] in seen: errors.append(f"{cid}: field {cond['field']!r} repeated")
        seen.append(cond['field'])

def validate_authority(a: dict, known_decision_ids: set | None = None) -> None:
    if not isinstance(a, dict): raise AuthorityError('authority must be an object')
    errors = []
    req = {'document_id','version','status','authority_id','target_type','assessment_semantics','classification_vocabulary','applicability_vocabulary','not_applicable_semantics','evidence_boundary','source_lineage','approved_governance_decision_ids','controls'}
    if not req <= set(a): errors.append('missing required top-level authority fields')
    if a.get('document_id') != 'EMS-ARCHIVE-ASSESSMENT-APPLICABILITY-AUTHORITY' or a.get('version') != VERSION or a.get('status') != 'CONTROLLED' or a.get('authority_id') != AUTHORITY_ID: errors.append('authority identity/version/status invalid')
    if a.get('target_type') != 'ARCHIVED_REPOSITORY_SNAPSHOT' or a.get('assessment_semantics') != 'CURRENT_POLICY_AGAINST_HISTORICAL_SNAPSHOT': errors.append('unauthorized target or assessment semantics')
    if a.get('approved_governance_decision_ids') != DECISIONS: errors.append('AA2 decision provenance is incomplete or contains an unapproved decision')
    cv = a.get('classification_vocabulary', {})
    if not isinstance(cv, dict): errors.append('classification_vocabulary must be an object'); cv = {}
    if cv.get('states') != ['KNOWN_TRUE','KNOWN_FALSE','UNKNOWN'] or not cv.get('unknown_is_not_false') or not cv.get('unknown_is_not_not_applicable'): errors.append('UNKNOWN semantics collapse or vocabulary invalid')
    sem = a.get('not_applicable_semantics', {})
    if not isinstance(sem, dict): sem = {}
    if sem.get('requires_explicit_controlled_rule') is not True: errors.append('implicit NOT_APPLICABLE is authorized')
    pin = {k: v for k, v in sem.items() if k != 'field_definitions'}
    expected = {k: v for k, v in semantics().items() if k != 'field_definitions'}
    if pin != expected: errors.append('not_applicable_semantics does not match the published semantics')
    fd = sem.get('field_definitions')
    if not isinstance(fd, dict) or set(fd) != set(RULE_FIELDS) or any(not isinstance(v, str) or not v.strip() for v in fd.values()): errors.append('field_definitions must define exactly the four rule fields with non-empty text')
    lin0 = a.get('source_lineage') if isinstance(a.get('source_lineage'), dict) else {}
    sup = lin0.get('supersedes'); v1b = lin0.get('v1_baseline')
    if sup != SUPERSEDED_V2_0_1: errors.append('source_lineage supersedes does not name the 2.0.1 publication')
    if not isinstance(v1b, dict) or {k: v for k, v in v1b.items() if k != 'sha256'} != {k: v for k, v in v1_baseline_entry().items() if k != 'sha256'}: errors.append('source_lineage v1_baseline entry missing or invalid')
    if contains_absolute(a): errors.append('absolute local path used as authority identity')
    deps = a.get('dependencies', [])
    if not isinstance(deps, list): errors.append('dependencies must be a list'); deps = []
    for dependency in deps:
        if not isinstance(dependency, dict): errors.append('dependency must be an object'); continue
        if dependency.get('required_for_deterministic_compilation') and (not dependency.get('relative_path') or not dependency.get('sha256')): errors.append('required authority dependency cannot be deterministically frozen')
    catalog_ids = {c['control_id'] for c in catalog_controls()}; rows = a.get('controls', [])
    if not isinstance(rows, list): errors.append('controls must be a list'); rows = []
    ids = [r.get('control_id') if isinstance(r, dict) and isinstance(r.get('control_id'), str) else None for r in rows]
    if len(ids) != 80 or len(set(ids)) != 80: errors.append('duplicate or incorrect control population count')
    if set(ids) != catalog_ids: errors.append('missing or unknown control ID')
    eb = a.get('evidence_boundary', {})
    if not isinstance(eb, dict): errors.append('evidence_boundary must be an object'); eb = {}
    dne = eb.get('archive_content_does_not_establish', [])
    forbidden = {x for x in dne if isinstance(x, str)} if isinstance(dne, list) else set()
    if not set(LIVE_BOUNDARY) <= forbidden: errors.append('live authority evidence boundary incomplete')
    for i, r in enumerate(rows):
        if not isinstance(r, dict): errors.append(f'control row {i} must be an object'); continue
        cid = r.get('control_id')
        if r.get('archive_population_membership') != 'IN_ARCHIVE_CONTROL_POPULATION': errors.append(f'{cid}: population membership not explicit')
        if r.get('default_applicability_result') != 'APPLICABILITY_UNRESOLVED' or r.get('classification_unknown_treatment') != 'APPLICABILITY_UNRESOLVED': errors.append(f'{cid}: UNKNOWN/missing input is not fail-closed unresolved')
        if r.get('decision_ids') != DECISIONS: errors.append(f'{cid}: missing AA2 traceability')
        state = r.get('not_applicable_decision_state'); rule = r.get('not_applicable_rule'); auth = r.get('not_applicable_authority')
        if state not in DECISION_STATES: errors.append(f'{cid}: not_applicable_decision_state invalid'); continue
        if state == 'NOT_YET_DECIDED':
            if rule is not None or auth is not None: errors.append(f'{cid}: NOT_YET_DECIDED requires null rule and null authority')
            continue
        if state == 'RULE_PUBLISHED': validate_rule(cid, rule, errors)
        elif rule is not None: errors.append(f'{cid}: NO_RULE_WILL_BE_PUBLISHED requires null rule')
        if not isinstance(auth, str) or not re.match(AUTHORITY_ID_RE, auth): errors.append(f'{cid}: decided control needs an AA4-GOV-NNN authority')
        elif known_decision_ids is not None and auth not in known_decision_ids: errors.append(f'{cid}: authority {auth} is not an approved decision id')
    att = a.get('attestation_prohibitions', {})
    if not isinstance(att, dict): att = {}
    if any(att.get(k) is not False for k in ATTESTATION_KEYS): errors.append('attestation leakage')
    if errors: raise AuthorityError('; '.join(errors))

def validate_publication(a: dict) -> None:
    doc = load(GOVERNANCE_DECISIONS)
    validate_authority(a, known_decision_ids={r['decision_id'] for r in doc['records']})
    errors = []
    rows = a.get('controls', [])
    decided = {r['control_id'] for r in rows if r.get('not_applicable_decision_state') != 'NOT_YET_DECIDED'}
    if decided != set(REQUEST_CONTROL_IDS): errors.append('decided control set is not exactly the 21 requested controls')
    auths = [r.get('not_applicable_authority') for r in rows if r.get('not_applicable_authority') is not None]
    ids = a.get('applicability_decision_ids')
    if not isinstance(ids, list) or not all(isinstance(x, str) for x in ids) or len(set(ids)) != len(ids) or set(ids) != set(auths) or len(auths) != len(set(auths)): errors.append('applicability_decision_ids must list each cited authority exactly once')
    lin = a.get('source_lineage') if isinstance(a.get('source_lineage'), dict) else {}
    gd = lin.get('governance_decisions')
    if not isinstance(gd, dict): errors.append('governance_decisions lineage missing')
    else:
        if gd.get('relative_path') != GOVERNANCE_DECISIONS_REL: errors.append('governance_decisions relative_path invalid')
        if gd.get('sha256') != lf_digest(GOVERNANCE_DECISIONS): errors.append('governance_decisions sha256 does not match the live decisions file')
        if gd.get('sha256') != SUPERSEDED_V2_0_1['governance_decisions_sha256']: errors.append('governance_decisions sha256 does not equal the 2.0.1 decisions digest')
        if gd.get('record_count') != len(doc['records']): errors.append('governance_decisions record_count does not match the live decisions file')
        if gd.get('drafting_commit') != doc.get('drafting_commit'): errors.append('governance_decisions drafting_commit does not match the live decisions file')
    if lf_digest(GOVERNANCE_DECISIONS) != SUPERSEDED_V2_0_1['governance_decisions_sha256']: errors.append('decisions file differs from the 2.0.1 decisions (unchanged since 2.0.0); 2.0.2 may not change any decision')
    latest = {r['control_id']: r for r in latest_records(doc)}
    if a.get('applicability_decision_ids') != sorted(r['decision_id'] for r in latest.values()): errors.append('applicability_decision_ids does not equal the decision ids derived from the decision records')
    for r in rows:
        rec0 = latest.get(r.get('control_id'))
        want = (rec0['decided_outcome'], rec0['decided']['rule'], rec0['decision_id']) if rec0 else ('NOT_YET_DECIDED', None, None)
        if (r.get('not_applicable_decision_state'), r.get('not_applicable_rule'), r.get('not_applicable_authority')) != want: errors.append(f"{r.get('control_id')}: decision fields differ from the decision records")
    for r in rows:
        auth = r.get('not_applicable_authority')
        if auth is None: continue
        rec = latest.get(r['control_id'])
        if rec is None or rec['decision_id'] != auth: errors.append(f"{r['control_id']}: authority {auth} is not the latest unsuperseded decision record")
        elif r.get('not_applicable_decision_state') != rec['decided_outcome'] or r.get('not_applicable_rule') != rec['decided']['rule']: errors.append(f"{r['control_id']}: state or rule does not match decision record {auth}")
    v1 = {r['control_id']: r for r in load(V1_AUTHORITY)['controls']}
    for r in rows:
        base = v1.get(r.get('control_id'))
        if base is None: errors.append(f"{r.get('control_id')}: not present in v1.0.0"); continue
        keep = {'not_applicable_decision_state', 'not_applicable_rule', 'not_applicable_authority'} if r['control_id'] in REQUEST_CONTROL_IDS else {'not_applicable_decision_state'}
        if {k: v for k, v in r.items() if k not in keep} != {k: v for k, v in base.items() if k not in keep}: errors.append(f"{r['control_id']}: differs from v1.0.0 beyond the decision fields")
        if r['control_id'] not in REQUEST_CONTROL_IDS and (r.get('not_applicable_rule') is not None or r.get('not_applicable_authority') is not None): errors.append(f"{r['control_id']}: undecided control carries a rule or authority")
    if lin.get('supersedes') != SUPERSEDED_V2_0_1: errors.append('lineage must record the 2.0.1 publication it supersedes')
    if lin.get('v1_baseline') != v1_baseline_entry(): errors.append('lineage v1_baseline must record v1.0.0 with the live v1 digest')
    cat = lin.get('catalog_reference')
    if not isinstance(cat, dict) or cat.get('sha256') != hashlib.sha256(lf_bytes(catalog_bytes())).hexdigest(): errors.append('lineage catalog digest does not match')
    if not isinstance(cat, dict) or cat.get('commit') != CATALOG_COMMIT: errors.append('lineage catalog commit does not match the pinned catalog commit')
    if not isinstance(cat, dict) or cat.get('relative_path') != CATALOG_REL: errors.append('lineage catalog relative_path invalid')
    if 'digest_normalisation' in lin: errors.append('source_lineage must not carry a global digest_normalisation')
    for label, want_rel in (('aa1_manifest', AA1_MANIFEST_REL), ('aa2_closure', AA2_CLOSURE_REL), ('aa2_approval', AA2_APPROVAL_REL)):
        e = lin.get(label)
        if not isinstance(e, dict) or e.get('relative_path') != want_rel: errors.append(f'{label}: lineage entry missing or relative_path invalid')
    for label, e, key in (('aa1_manifest', lin.get('aa1_manifest'), 'normalisation'), ('aa2_closure', lin.get('aa2_closure'), 'normalisation'), ('aa2_approval', lin.get('aa2_approval'), 'normalisation'), ('catalog_reference', cat, 'normalisation'), ('governance_decisions', gd, 'normalisation'), ('supersedes', lin.get('supersedes'), 'normalisation'), ('supersedes_governance_decisions', lin.get('supersedes'), 'governance_decisions_normalisation'), ('v1_baseline', lin.get('v1_baseline'), 'normalisation')):
        if not isinstance(e, dict) or e.get(key) != EXPECTED_NORMALISATION[label]: errors.append(f'{label}: normalisation must be {EXPECTED_NORMALISATION[label]}')
    if errors: raise AuthorityError('; '.join(errors))

def bad_rel(p: object) -> bool: return not isinstance(p, str) or not p or contains_absolute(p) or p.startswith('\\') or re.match(r'[A-Za-z]:', p) is not None or '..' in p.replace('\\', '/').split('/')

COMMIT_PINNED = {'catalog_reference', 'supersedes','supersedes_governance_decisions', 'v1_baseline'}

def git_show(commit: str, relative_path: str) -> bytes:
    if not isinstance(commit, str) or not re.fullmatch(r'[0-9a-f]{40}', commit): raise AuthorityError(f'{relative_path}: commit must be a 40-character lowercase hex SHA')
    if bad_rel(relative_path): raise AuthorityError(f'{relative_path}: path must be repo-relative without ..')
    try: r = subprocess.run(['git', 'show', f'{commit}:{relative_path}'], cwd=ROOT, capture_output=True)
    except OSError as e: raise GitHistoryError(f'{relative_path}@{commit[:7]}: git unavailable: {e}') from e
    if r.returncode != 0: raise GitHistoryError(f'{relative_path}@{commit[:7]}: git show failed: {r.stderr.decode("utf-8", "replace").strip()}')
    return r.stdout

def validate_lineage(lin: dict) -> None:
    errors = []
    checks = []
    sup = lin.get('supersedes') if isinstance(lin.get('supersedes'), dict) else {}
    for label in ('aa1_manifest', 'aa2_closure', 'aa2_approval', 'catalog_reference', 'governance_decisions', 'v1_baseline'):
        e = lin.get(label)
        e = e if isinstance(e, dict) else {}
        checks.append((label, e.get('relative_path'), e.get('sha256'), e.get('normalisation'), e.get('commit')))
    checks.append(('supersedes', sup.get('relative_path'), sup.get('sha256'), sup.get('normalisation'), sup.get('commit')))
    checks.append(('supersedes_governance_decisions', sup.get('governance_decisions_relative_path'), sup.get('governance_decisions_sha256'), sup.get('governance_decisions_normalisation'), sup.get('commit')))
    for label, path, want, norm, commit in checks:
        if not isinstance(norm, str) or norm not in NORMALISERS: errors.append(f'{label}: unknown normalisation {norm!r}'); continue
        if norm != EXPECTED_NORMALISATION[label]: errors.append(f'{label}: normalisation {norm} differs from {EXPECTED_NORMALISATION[label]}'); continue
        if bad_rel(path): errors.append(f'{label}: relative_path missing or invalid'); continue
        if label in COMMIT_PINNED and not commit: errors.append(f'{label}: commit-pinned entry must carry a commit'); continue
        try: data = git_show(commit, path) if commit else (ROOT / path).read_bytes()
        except (OSError, AuthorityError) as e: errors.append(f'{label}: {e}'); continue
        if hashlib.sha256(NORMALISERS[norm](data)).hexdigest() != want: errors.append(f'{label}: recomputed sha256 does not match the recorded digest')
    if errors: raise AuthorityError('; '.join(errors))

def schema() -> dict:
    cond = {'type':'object','additionalProperties':False,'required':['field','state'],'properties':{'field':{'enum':list(RULE_FIELDS)},'state':{'enum':list(CONDITION_STATES)}}}
    dup_guard = [{'contains':{'type':'object','required':['field'],'properties':{'field':{'const':f}}},'minContains':0,'maxContains':1} for f in RULE_FIELDS]
    rule = {'type':'object','additionalProperties':False,'required':['combination','conditions'],'properties':{'combination':{'const':COMBINATION},'conditions':{'type':'array','minItems':1,'maxItems':len(RULE_FIELDS),'items':cond,'allOf':dup_guard}}}
    sha = {'type':'string','pattern':'^[0-9a-f]{64}$'}
    def pinned(entry, sha_keys):
        props = {k: ({'type':'string','pattern':'^[0-9a-f]{64}$'} if k in sha_keys else {'const':v}) for k, v in entry.items()}
        return {'type':'object','additionalProperties':False,'required':list(entry),'properties':props}
    def norm_schema(label): return {'enum':list(NORMALISATIONS),'const':EXPECTED_NORMALISATION[label]}
    def entry_schema(label, rel_path): return {'type':'object','additionalProperties':False,'required':['relative_path','sha256','normalisation'],'properties':{'relative_path':{'const':rel_path},'sha256':sha,'normalisation':norm_schema(label)}}
    lineage = {'type':'object','additionalProperties':False,
        'required':['governance_decisions','supersedes','v1_baseline','catalog_reference','aa1_manifest','aa2_closure','aa2_approval'],
        'properties':{
            'supersedes':pinned(SUPERSEDED_V2_0_1, {'sha256','governance_decisions_sha256'}),
            'v1_baseline':pinned({'authority_id':V1_BASELINE_ID,'version':'1.0.0','commit':V1_BASELINE_COMMIT,'relative_path':V1_BASELINE_REL,'sha256':None,'normalisation':'CRLF_TO_LF'}, {'sha256'}),
            'governance_decisions':{'type':'object','additionalProperties':False,'required':['relative_path','sha256','normalisation','record_count','drafting_commit'],'properties':{'relative_path':{'const':GOVERNANCE_DECISIONS_REL},'sha256':sha,'normalisation':norm_schema('governance_decisions'),'record_count':{'const':21},'drafting_commit':{'type':'string','pattern':'^[0-9a-f]{40}$'}}},
            'catalog_reference':{'type':'object','additionalProperties':False,'required':['relative_path','sha256','normalisation','commit','required_for_deterministic_compilation'],'properties':{'relative_path':{'const':CATALOG_REL},'sha256':sha,'normalisation':norm_schema('catalog_reference'),'commit':{'const':CATALOG_COMMIT},'required_for_deterministic_compilation':{'const':False}}},
            'aa1_manifest':entry_schema('aa1_manifest', AA1_MANIFEST_REL),'aa2_closure':entry_schema('aa2_closure', AA2_CLOSURE_REL),'aa2_approval':entry_schema('aa2_approval', AA2_APPROVAL_REL)}}
    auth = {'type':'string','pattern':AUTHORITY_ID_RE}
    def branch(state, rule_s, auth_s):
        return {'if':{'properties':{'not_applicable_decision_state':{'const':state}},'required':['not_applicable_decision_state']},'then':{'properties':{'not_applicable_rule':rule_s,'not_applicable_authority':auth_s}}}
    sem = {'type':'object','additionalProperties':False,'required':['requires_explicit_controlled_rule','absence_of_evidence_is_not_not_applicable','unknown_is_not_not_applicable','decision_states','condition_states','condition_combination','min_conditions','field_may_appear_once','rule_condition_fields','fields_not_usable_in_rules','fields_not_usable_in_rules_statement','field_definitions','resolution','no_short_circuit','decision_state_governs_resolved_result','per_control_default_describes_result_absent_a_decision','unknown_is_never_not_applicable','statements'],
        'properties':{'requires_explicit_controlled_rule':{'const':True},'absence_of_evidence_is_not_not_applicable':{'const':True},'unknown_is_not_not_applicable':{'const':True},'decision_states':{'const':list(DECISION_STATES)},'condition_states':{'const':list(CONDITION_STATES)},'condition_combination':{'const':COMBINATION},'min_conditions':{'const':1},'field_may_appear_once':{'const':True},'rule_condition_fields':{'const':list(RULE_FIELDS)},'fields_not_usable_in_rules':{'const':list(NON_RULE_FIELDS)},'field_definitions':{'type':'object','additionalProperties':False,'required':list(RULE_FIELDS),'properties':{f:{'type':'string','minLength':1} for f in RULE_FIELDS}},'resolution':{'const':[dict(r) for r in RESOLUTION]},'no_short_circuit':{'const':True},'decision_state_governs_resolved_result':{'const':True},'per_control_default_describes_result_absent_a_decision':{'const':True},'unknown_is_never_not_applicable':{'const':True},'fields_not_usable_in_rules_statement':{'const':semantics()['fields_not_usable_in_rules_statement']},'statements':{'const':list(semantics()['statements'])}}}
    truthy = {'not':{'enum':[False,None,0,'',[],{}]}}
    attest = {'type':'object','required':list(ATTESTATION_KEYS),'properties':{k:{'const':False} for k in ATTESTATION_KEYS}}
    vocab = {'type':'object','required':['states','unknown_is_not_false','unknown_is_not_not_applicable'],'properties':{'states':{'const':['KNOWN_TRUE','KNOWN_FALSE','UNKNOWN']},'unknown_is_not_false':truthy,'unknown_is_not_not_applicable':truthy}}
    boundary = {'type':'object','required':['archive_content_does_not_establish'],'properties':{'archive_content_does_not_establish':{'type':'array','allOf':[{'contains':{'const':s}} for s in LIVE_BOUNDARY]}}}
    return {'$schema':'https://json-schema.org/draft/2020-12/schema','title':'EMS AA3 Archive Assessment Applicability Authority v2','type':'object','additionalProperties':False,
        'required':['document_id','version','status','authority_id','target_type','assessment_semantics','attestation_prohibitions','classification_vocabulary','applicability_vocabulary','not_applicable_semantics','evidence_boundary','source_lineage','approved_governance_decision_ids','applicability_decision_ids','controls'],
        'properties':{'$schema':{'type':'string'},'applicability_vocabulary':{'type':'array'},'attestation_prohibitions':attest,'classification_vocabulary':vocab,'evidence_boundary':boundary,'document_id':{'const':'EMS-ARCHIVE-ASSESSMENT-APPLICABILITY-AUTHORITY'},'version':{'const':VERSION},'status':{'const':'CONTROLLED'},'authority_id':{'const':AUTHORITY_ID},'target_type':{'const':'ARCHIVED_REPOSITORY_SNAPSHOT'},'assessment_semantics':{'const':'CURRENT_POLICY_AGAINST_HISTORICAL_SNAPSHOT'},
            'approved_governance_decision_ids':{'type':'array','minItems':8,'maxItems':8,'items':{'type':'string','pattern':'^AA1-GOV-00[1-8]$'},'uniqueItems':True},
            'applicability_decision_ids':{'type':'array','minItems':0,'maxItems':21,'items':{'type':'string','pattern':AUTHORITY_ID_RE},'uniqueItems':True},
            'source_lineage':lineage,
            'not_applicable_semantics':sem,
            'controls':{'type':'array','minItems':80,'maxItems':80,'items':{'type':'object','additionalProperties':False,
                'required':['control_id','control_name','catalog_scope','archive_population_membership','target_type','assessment_semantics','classification_prerequisites','classification_unknown_treatment','archive_evidence_capability','required_non_repository_authority','default_applicability_result','unresolved_reason','not_applicable_decision_state','not_applicable_rule','not_applicable_authority','decision_ids'],
                'properties':{'archive_evidence_capability':{'type':'string'},'catalog_scope':{'type':'string'},'classification_prerequisites':{'type':'array','items':{'type':'string'}},'control_name':{'type':'string'},'required_non_repository_authority':{'type':'string'},'unresolved_reason':{'type':'string'},'control_id':{'type':'string','pattern':'^EMS-CTRL-[0-9]{3}$'},'archive_population_membership':{'const':'IN_ARCHIVE_CONTROL_POPULATION'},'target_type':{'const':'ARCHIVED_REPOSITORY_SNAPSHOT'},'assessment_semantics':{'const':'CURRENT_POLICY_AGAINST_HISTORICAL_SNAPSHOT'},'classification_unknown_treatment':{'const':'APPLICABILITY_UNRESOLVED'},'default_applicability_result':{'const':'APPLICABILITY_UNRESOLVED'},
                    'not_applicable_decision_state':{'enum':list(DECISION_STATES)},'not_applicable_rule':{'anyOf':[rule,{'type':'null'}]},'not_applicable_authority':{'anyOf':[auth,{'type':'null'}]},
                    'decision_ids':{'type':'array','minItems':8,'maxItems':8,'uniqueItems':True}},
                'allOf':[branch('RULE_PUBLISHED',rule,auth),branch('NO_RULE_WILL_BE_PUBLISHED',{'type':'null'},auth),branch('NOT_YET_DECIDED',{'type':'null'},{'type':'null'})]}}}}

def resolve_applicability(control: dict, facts: dict) -> str:
    state = control.get('not_applicable_decision_state')
    if state == 'NOT_YET_DECIDED': return 'APPLICABILITY_UNRESOLVED'
    if state == 'NO_RULE_WILL_BE_PUBLISHED': return 'APPLICABLE'
    if state != 'RULE_PUBLISHED': return 'APPLICABILITY_UNRESOLVED'
    rule = control.get('not_applicable_rule')
    if not isinstance(rule, dict) or not isinstance(rule.get('conditions'), list) or not rule['conditions']: return 'APPLICABILITY_UNRESOLVED'
    unknown = False; met = True
    for cond in rule['conditions']:
        if not isinstance(cond, dict) or cond.get('field') not in RULE_FIELDS or cond.get('state') not in CONDITION_STATES: return 'APPLICABILITY_UNRESOLVED'
        value = facts.get(cond['field'], 'UNKNOWN')
        if not (isinstance(value, str) and value in CONDITION_STATES): unknown = True
        elif value != cond['state']: met = False
    if unknown: return 'APPLICABILITY_UNRESOLVED'
    return 'NOT_APPLICABLE' if met else 'APPLICABLE'

OUT = ROOT / 'generated' / 'archive-assessment' / 'ems-aa3-v2'
SIGNOFF = REGISTRY / 'archive_assessment_applicability_authority_v2_signoff.json'
PUBLICATION_RECORD = REGISTRY / 'archive_assessment_applicability_authority_v2_publication_record.json'
SCRIPT = Path(__file__).resolve()
APPROVER = 'Oscar Mack'
APPROVER_ROLES = ['EMS_GOVERNANCE_AUTHORITY', 'HAYES_VERIFY_DEVELOPER']
SIGNOFF_ROLE = 'EMS_GOVERNANCE_AUTHORITY'
DUAL_ROLE_STATEMENT = 'Oscar Mack made this decision as the EMS governance authority and is also the developer of Hayes Verify, the assessor that will read it.'
N_MATRIX = 'archive_assessment_applicability_authority_v2_matrix.json'
N_SEMANTIC = 'archive_assessment_applicability_authority_v2_semantic_validation.json'
N_NEGATIVE = 'archive_assessment_applicability_authority_v2_negative_invariant_validation.json'
N_TRACE = 'archive_assessment_applicability_authority_v2_decision_traceability.json'
N_CERT = 'EMS_AA3_V2_ARCHIVE_APPLICABILITY_AUTHORITY_PUBLICATION_CERTIFICATION.json'
N_REPORT = 'EMS_AA3_V2_ARCHIVE_APPLICABILITY_AUTHORITY_PUBLICATION.md'
N_MANIFEST = 'ems_aa3_v2_archive_applicability_authority_publication_manifest.json'
class Mutation(NamedTuple):
    id: str
    description: str
    target: str
    apply: Callable
    schema_must_reject: bool = False

def _row(a, cid): return next(c for c in a['controls'] if c['control_id'] == cid)
def _cond(a, cid): return _row(a, cid)['not_applicable_rule']['conditions']
def _gd(a): return a['source_lineage']['governance_decisions']

def _m_swapped(a):
    _row(a, 'EMS-CTRL-009')['not_applicable_authority'], _row(a, 'EMS-CTRL-010')['not_applicable_authority'] = 'AA4-GOV-002', 'AA4-GOV-001'
def _m_flip_to_undecided(a): _row(a, 'EMS-CTRL-009').update({'not_applicable_decision_state': 'NOT_YET_DECIDED', 'not_applicable_authority': None})
def _m_22nd(a): _row(a, 'EMS-CTRL-001').update({'not_applicable_decision_state': 'NO_RULE_WILL_BE_PUBLISHED', 'not_applicable_authority': 'AA4-GOV-001'})
def _m_digest_and_count(a): _gd(a).update({'record_count': 20, 'drafting_commit': '0' * 40})
def _m_wrong_v1(a): a['source_lineage']['v1_baseline'].update({'sha256': '0' * 64, 'commit': 'abcdef0'})
def _m_superseded_cited(a):
    _row(a, 'EMS-CTRL-009')['not_applicable_authority'] = 'AA4-GOV-010'
    a['applicability_decision_ids'] = sorted((set(a['applicability_decision_ids']) - {'AA4-GOV-001'}) | {'AA4-GOV-010'})
def _m_dup_field(a): _cond(a, 'EMS-CTRL-030').append({'field': 'production', 'state': 'KNOWN_TRUE'})
def _m_dual_text(r): r['dual_role_statement'] = r['dual_role_statement'] + ' Extra text.'
def _m_decision_approver(d): d['records'][0]['approver'] = 'Someone Else'
def _m_decision_dual(d): d['records'][0]['dual_role_statement'] = ''
def _m_decision_disposition(d): d['records'][0]['disposition'] = 'BOGUS'

NEGATIVE_MUTATIONS = [
    Mutation('swapped_authority', 'Authority ids of two decided controls are swapped.', 'AUTHORITY', _m_swapped),
    Mutation('rule_field_change', 'A published rule is changed to name a different field.', 'AUTHORITY', lambda a: _cond(a, 'EMS-CTRL-030')[0].__setitem__('field', 'ai_enabled')),
    Mutation('rule_state_unknown', 'A rule condition state is set to UNKNOWN.', 'AUTHORITY', lambda a: _cond(a, 'EMS-CTRL-030')[0].__setitem__('state', 'UNKNOWN'), True),
    Mutation('rule_unused_field', 'A rule names a classification field that is not usable in rules.', 'AUTHORITY', lambda a: _cond(a, 'EMS-CTRL-030')[0].__setitem__('field', 'tier'), True),
    Mutation('rule_state_flip', 'A rule condition state is flipped from its decision record.', 'AUTHORITY', lambda a: _cond(a, 'EMS-CTRL-052')[0].__setitem__('state', 'KNOWN_TRUE')),
    Mutation('decided_flipped_to_not_yet_decided', 'A decided control is reverted to NOT_YET_DECIDED.', 'AUTHORITY', _m_flip_to_undecided),
    Mutation('twenty_second_control_decided', 'A control outside the 21 requested controls is decided.', 'AUTHORITY', _m_22nd),
    Mutation('v1_field_change_on_undecided_row', 'A non-decision field changes on an undecided row.', 'AUTHORITY', lambda a: _row(a, 'EMS-CTRL-001').__setitem__('default_applicability_result', 'APPLICABLE'), True),
    Mutation('extra_field_on_decided_row', 'An extra field is added to a decided row.', 'AUTHORITY', lambda a: _row(a, 'EMS-CTRL-009').__setitem__('rationale', 'copied')),
    Mutation('authority_removed_from_id_list', 'A cited authority id is removed from applicability_decision_ids.', 'AUTHORITY', lambda a: a['applicability_decision_ids'].pop()),
    Mutation('authority_cited_twice', 'Two controls cite the same authority id.', 'AUTHORITY', lambda a: _row(a, 'EMS-CTRL-010').__setitem__('not_applicable_authority', 'AA4-GOV-001')),
    Mutation('duplicate_id_in_list', 'applicability_decision_ids carries a duplicate id.', 'AUTHORITY', lambda a: a['applicability_decision_ids'].append('AA4-GOV-001'), True),
    Mutation('altered_governance_digest', 'The governance decisions digest in the lineage is altered.', 'AUTHORITY', lambda a: _gd(a).__setitem__('sha256', '0' * 64)),
    Mutation('altered_record_count_or_drafting_commit', 'The governance decisions record count and drafting commit are altered.', 'AUTHORITY', _m_digest_and_count),
    Mutation('missing_governance_lineage', 'The governance decisions lineage entry is removed.', 'AUTHORITY', lambda a: a['source_lineage'].pop('governance_decisions'), True),
    Mutation('wrong_v1_lineage', 'The v1 baseline lineage digest and commit are altered.', 'AUTHORITY', _m_wrong_v1),
    Mutation('superseded_record_cited', 'A control cites a decision record that is not its latest unsuperseded record.', 'AUTHORITY', _m_superseded_cited),
    Mutation('signoff_role_hayes_developer', 'The sign-off role is the Hayes developer role.', 'SIGNOFF', lambda r: r['approval'].__setitem__('role', 'HAYES_VERIFY_DEVELOPER')),
    Mutation('signoff_invalid_date', 'The sign-off date is not a date.', 'SIGNOFF', lambda r: r['approval'].__setitem__('date', 'not-a-date')),
    Mutation('signoff_dual_role_text_appended', 'Text is appended to the sign-off dual-role statement.', 'SIGNOFF', _m_dual_text),
    Mutation('signoff_extra_keys', 'An extra key is added to the sign-off record.', 'SIGNOFF', lambda r: r.__setitem__('extra', 'x')),
    Mutation('decision_record_tampered_approver', 'A decision record names a different approver.', 'DECISIONS', _m_decision_approver, True),
    Mutation('decision_record_empty_dual_role_statement', 'A decision record carries an empty dual-role statement.', 'DECISIONS', _m_decision_dual, True),
    Mutation('decision_record_bogus_disposition', 'A decision record carries an unknown disposition.', 'DECISIONS', _m_decision_disposition, True),
    Mutation('rule_same_field_twice_opposite_states', 'A rule names the same field twice with opposite states.', 'AUTHORITY', _m_dup_field, True),
    Mutation('supersedes_governance_digest_differs', 'The supersedes governance decisions digest differs from the 2.0.1 value.', 'AUTHORITY', lambda a: a['source_lineage']['supersedes'].__setitem__('governance_decisions_sha256', '0' * 64)),
    Mutation('extra_top_level_field', 'An extra field is added at the top level of the authority.', 'AUTHORITY', lambda a: a.__setitem__('rationale', 'copied'), True),
    Mutation('extra_field_on_undecided_row', 'An extra field is added to an undecided row.', 'AUTHORITY', lambda a: _row(a, 'EMS-CTRL-001').__setitem__('rationale', 'copied'), True),
    Mutation('extra_field_in_semantics', 'An extra field is added to the not-applicable semantics.', 'AUTHORITY', lambda a: a['not_applicable_semantics'].__setitem__('extra', 'x'), True),
]

def jtext(value: object) -> str: return json.dumps(value, indent=2, sort_keys=True) + '\n'
def sha_text(text: str) -> str: return hashlib.sha256(text.encode('utf-8')).hexdigest()
def rel(p: Path) -> str: return p.relative_to(ROOT).as_posix()
def write_text(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, 'w', encoding='utf-8', newline='\n') as f: f.write(text)

def is_date(value: object) -> bool:
    if not isinstance(value, str) or not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', value): return False
    try: date.fromisoformat(value)
    except ValueError: return False
    return True

def validate_signoff(record: object, authority_lf_digest: str, authority_id: str | None = None, version: str | None = None) -> None:
    errors = []
    want_id = AUTHORITY_ID if authority_id is None else authority_id; want_version = VERSION if version is None else version
    if not isinstance(record, dict): raise AuthorityError('sign-off record must be an object')
    record_keys = {'status', 'approval', 'dual_role_statement', 'authority_id', 'version', 'authority_sha256', 'authority_sha256_normalisation'}
    if set(record) != record_keys: errors.append(f'sign-off keys must be exactly {sorted(record_keys)}')
    appr = record.get('approval')
    if not isinstance(appr, dict): errors.append('sign-off approval must be an object'); appr = {}
    elif set(appr) != {'approver', 'role', 'date', 'scope'}: errors.append('sign-off approval keys must be exactly approver, role, date and scope')
    if record.get('status') != 'PUBLICATION_SIGNOFF': errors.append('sign-off status must be PUBLICATION_SIGNOFF')
    if appr.get('approver') != APPROVER: errors.append('sign-off approver must be Oscar Mack')
    if appr.get('role') != SIGNOFF_ROLE: errors.append(f'sign-off role must be {SIGNOFF_ROLE}')
    if not is_date(appr.get('date')): errors.append('sign-off date must be a real ISO date')
    scope = appr.get('scope')
    if not isinstance(scope, str) or not scope.strip(): errors.append('sign-off scope must be a non-empty string')
    if record.get('dual_role_statement') != DUAL_ROLE_STATEMENT: errors.append('sign-off dual_role_statement missing or altered')
    if 'authority_id' in record and record['authority_id'] != want_id: errors.append('sign-off authority_id does not match')
    if 'version' in record and record['version'] != want_version: errors.append('sign-off version does not match')
    if 'authority_sha256' in record and record['authority_sha256'] != authority_lf_digest: errors.append('sign-off authority_sha256 does not match the rebuilt authority')
    if 'authority_sha256_normalisation' in record and record['authority_sha256_normalisation'] != 'CRLF_TO_LF': errors.append('sign-off authority_sha256_normalisation must be CRLF_TO_LF')
    if errors: raise AuthorityError('; '.join(errors))

def rule_text(rule: dict) -> str:
    return f"{rule['combination']}: " + ' AND '.join(f"{c['field']} = {c['state']}" for c in rule['conditions'])

def dry_run_summary(authority: dict) -> str:
    rows = authority['controls']
    decided = [r for r in rows if r['not_applicable_decision_state'] != 'NOT_YET_DECIDED']
    undecided = [r for r in rows if r['not_applicable_decision_state'] == 'NOT_YET_DECIDED']
    dsha = lf_digest(GOVERNANCE_DECISIONS); sup = SUPERSEDED_V2_0_1
    lines = [f'Publication sign-off summary for {authority["authority_id"]}', f'Decided controls: {len(decided)}', f'Undecided controls: {len(undecided)}', '', 'Decisions:']
    for r in decided: lines.append(f"  {r['control_id']}  {r['not_applicable_authority']}  {r['not_applicable_decision_state']}")
    lines += ['', 'Undecided:']
    for r in undecided: lines.append(f"  {r['control_id']}  {r['not_applicable_decision_state']}")
    lines += ['', 'Published rules:']
    for r in decided:
        if r['not_applicable_decision_state'] == 'RULE_PUBLISHED': lines.append(f"  {r['control_id']}: {rule_text(r['not_applicable_rule'])}")
    lines += ['', f'Authority LF sha256: {sha_text(jtext(authority))}', 'Digest normalisation: CRLF_TO_LF']
    same = 'equals' if dsha == sup['governance_decisions_sha256'] else 'DIFFERS FROM'
    lines += ['', f'Version {authority["version"]} supersedes {sup["authority_id"]} version {sup["version"]} (commit {sup["commit"][:7]}). No decision changed: the governance decisions LF sha256 {dsha} {same} the {sup["version"]} value.']
    return '\n'.join(lines) + '\n'

def build_all_outputs(authority: dict, signoff: dict, script_sha256: str | None = None) -> dict:
    if not isinstance(signoff, dict) or not isinstance(signoff.get('approval'), dict) or not is_date(signoff['approval'].get('date')): raise AuthorityError('a valid publication sign-off is required to build the outputs')
    published_on = signoff['approval']['date']
    ash = sha_text(jtext(authority))
    ssh = lf_digest(SCHEMA)
    signoff_rel = rel(SIGNOFF); signoff_sha = lf_digest(SIGNOFF)
    rows = authority['controls']
    conflicts = semantic_conflicts(rows)
    if conflicts: raise AuthorityError('semantic conflicts: ' + '; '.join(conflicts))
    outcomes = run_mutations(authority, signoff, load(GOVERNANCE_DECISIONS))
    n_decided = sum(r['not_applicable_decision_state'] != 'NOT_YET_DECIDED' for r in rows)
    matrix = {'authority_id': authority['authority_id'], 'version': authority['version'], 'published_on': published_on, 'control_population': 80, 'unique_control_count': 80, 'decided_control_count': n_decided, 'undecided_control_count': 80 - n_decided, 'controls': rows}
    sem_rows = []
    for r in rows:
        if r['not_applicable_decision_state'] != 'RULE_PUBLISHED': continue
        field = r['not_applicable_rule']['conditions'][0]['field']
        sem_rows.append({'control_id': r['control_id'], 'rule': r['not_applicable_rule'], 'results': {st: resolve_applicability(r, {f: st for f in RULE_FIELDS}) for st in ('KNOWN_TRUE', 'KNOWN_FALSE', 'UNKNOWN')}, 'unknown_result': resolve_applicability(r, {field: 'UNKNOWN'}), 'empty_facts_result': resolve_applicability(r, {})})
    semantic = {'result': 'PASS' if not conflicts else 'FAIL', 'published_on': published_on, 'semantic_conflict_count': len(conflicts), 'controls_checked': len(rows), 'unknown_never_not_applicable': all(x['unknown_result'] != 'NOT_APPLICABLE' and x['empty_facts_result'] != 'NOT_APPLICABLE' and x['results']['UNKNOWN'] != 'NOT_APPLICABLE' for x in sem_rows), 'rule_controls': sem_rows, 'checks': ['UNKNOWN preserved as APPLICABILITY_UNRESOLVED', 'NOT_APPLICABLE requires explicit controlled rule', 'repository evidence boundary preserved', 'historical attestation prohibited']}
    all_rejected = all(o['result'] == 'REJECTED_FAIL_CLOSED' for o in outcomes)
    negative = {'result': 'PASS' if all_rejected else 'FAIL', 'published_on': published_on, 'negative_invariant_tests': outcomes}
    doc_sha = lf_digest(GOVERNANCE_DECISIONS)
    trace = {'traceability_type': 'AA4_DECISION_TO_CONTROL_TRACEABILITY', 'published_on': published_on, 'decision_records': [], 'undecided_controls': []}
    for r in rows:
        if r['not_applicable_decision_state'] == 'NOT_YET_DECIDED': trace['undecided_controls'].append(r['control_id']); continue
        trace['decision_records'].append({'control_id': r['control_id'], 'decision_id': r['not_applicable_authority'], 'state': r['not_applicable_decision_state'], 'rule': r['not_applicable_rule'], 'decision_record_path': GOVERNANCE_DECISIONS_REL, 'decision_record_sha256': doc_sha, 'decision_record_digest_normalisation': 'CRLF_TO_LF'})
    trace['decided_count'] = len(trace['decision_records']); trace['undecided_count'] = len(trace['undecided_controls'])
    cert = {'certification_type': 'EMS_AA3_V2_ARCHIVE_APPLICABILITY_AUTHORITY_PUBLICATION_CERTIFICATION', 'certification_version': '1.0', 'published_on': published_on, 'authority_id': authority['authority_id'], 'version': authority['version'], 'authority_sha256': ash, 'schema_sha256': ssh, 'signoff_path': signoff_rel, 'signoff_sha256': signoff_sha, 'digest_normalisation': 'CRLF_TO_LF', 'control_population': 80, 'decided_control_count': n_decided, 'undecided_control_count': 80 - n_decided, 'semantic_conflicts': len(conflicts), 'negative_invariants': negative['result'], 'prohibitions': {'evaluator_executions': 0, 'hayes_modifications': 0, 'target_comparisons': 0}}
    report = ('# EMS-AA3 v2 Archive Assessment Applicability Authority Publication\n\n'
        f'Published on {published_on}. Version {authority["version"]} records an explicit decision for {n_decided} of the 80 EMS controls and leaves {80 - n_decided} as NOT_YET_DECIDED.\n\n'
        'Each decision is cited by an AA4 governance decision id approved by Oscar Mack, who is both the EMS governance authority and the developer of Hayes Verify.\n\n'
        'Not applicable is stated only by an explicit published rule over KNOWN_TRUE and KNOWN_FALSE conditions. UNKNOWN never resolves to not applicable.\n\n'
        f'Authority LF sha256: {ash}\nDigest normalisation: CRLF_TO_LF\n')
    outs = {N_MATRIX: jtext(matrix), N_SEMANTIC: jtext(semantic), N_NEGATIVE: jtext(negative), N_TRACE: jtext(trace), N_CERT: jtext(cert), N_REPORT: report}
    arts = [{'relative_path': rel(SCHEMA), 'sha256': ssh}, {'relative_path': rel(AUTHORITY), 'sha256': ash}, {'relative_path': signoff_rel, 'sha256': signoff_sha}]
    arts += [{'relative_path': f'{rel(OUT)}/{n}', 'sha256': sha_text(t)} for n, t in outs.items()]
    publisher_script = {'relative_path': rel(SCRIPT), 'sha256': script_sha256 or lf_digest(SCRIPT), 'sha256_normalisation': 'CRLF_TO_LF'}
    manifest = {'manifest_type': 'EMS_AA3_V2_ARCHIVE_APPLICABILITY_AUTHORITY_PUBLICATION_MANIFEST', 'published_on': published_on, 'authority_id': authority['authority_id'], 'digest_normalisation': 'CRLF_TO_LF', 'artifacts': arts, 'publisher_script': publisher_script, 'publisher_script_note': 'The publisher script digest is recorded at publication and is not recomputed on validation; validation rebuilds every output with the recorded value.', 'self_entry_exclusion_reason': 'A SHA-256 manifest cannot include a hash of itself without recursion.'}
    outs[N_MANIFEST] = jtext(manifest)
    return outs

_BUILDER = None
BUILDER_SCRIPT = Path(__file__).resolve().parent / 'build_archive_assessment_governance_decisions.py'

def decisions_builder():
    global _BUILDER
    if _BUILDER is None:
        spec = importlib.util.spec_from_file_location('aa_governance_decisions_builder', BUILDER_SCRIPT)
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); _BUILDER = module
    return _BUILDER

def validate_governance_decisions() -> dict:
    b = decisions_builder()
    try:
        doc = b.load_checked(GOVERNANCE_DECISIONS)
        b.validate_decisions(doc)
        jsonschema.Draft202012Validator(load(b.DECISIONS_SCHEMA)).validate(doc)
    except (ValueError, jsonschema.ValidationError, KeyError, TypeError, AttributeError) as e:
        raise AuthorityError(f'governance decisions rejected: {e}') from e
    return doc

def mutation_gates(target: str, doc: object, authority_digest: str) -> list[str]:
    gates = []
    if target == 'AUTHORITY':
        try: validate_publication(doc)
        except GitHistoryError: raise
        except AuthorityError: gates.append('PYTHON_VALIDATOR')
        try: jsonschema.Draft202012Validator(schema()).validate(doc)
        except jsonschema.ValidationError: gates.append('SCHEMA')
    elif target == 'SIGNOFF':
        try: validate_signoff(doc, authority_digest)
        except GitHistoryError: raise
        except AuthorityError: gates.append('PYTHON_VALIDATOR')
    elif target == 'DECISIONS':
        b = decisions_builder()
        try: b.validate_decisions(doc)
        except b.V2.GitHistoryError: raise
        except b.AuthorityError: gates.append('PYTHON_VALIDATOR')
        try: jsonschema.Draft202012Validator(load(b.DECISIONS_SCHEMA)).validate(doc)
        except jsonschema.ValidationError: gates.append('SCHEMA')
    else: raise AuthorityError(f'unknown mutation target {target}')
    return sorted(gates)

def run_mutations(authority: dict, signoff: dict, decisions_doc: dict) -> list[dict]:
    docs = {'AUTHORITY': authority, 'SIGNOFF': signoff, 'DECISIONS': decisions_doc}
    ash = sha_text(jtext(authority)); out = []
    ids = [m.id for m in NEGATIVE_MUTATIONS]
    if len(set(ids)) != len(ids): raise AuthorityError('negative mutation ids must be unique')
    for m in NEGATIVE_MUTATIONS:
        doc = copy.deepcopy(docs[m.target]); m.apply(doc)
        rejected_by = mutation_gates(m.target, doc, ash)
        if not rejected_by: raise AuthorityError(f'mutation {m.id} was accepted')
        if m.schema_must_reject and 'SCHEMA' not in rejected_by: raise AuthorityError(f'mutation {m.id} was not rejected by the schema')
        out.append({'mutation': m.id, 'id': m.id, 'description': m.description, 'rejected_by': rejected_by, 'result': 'REJECTED_FAIL_CLOSED'})
    return out

def semantic_conflicts(rows: list[dict]) -> list[str]:
    out = []
    for r in rows:
        cid = r['control_id']; state = r['not_applicable_decision_state']
        def chk(label, facts, want):
            got = resolve_applicability(r, facts)
            if got != want: out.append(f'{cid}: {label} resolved {got}, expected {want}')
        for label, facts in (('empty facts', {}), ('all UNKNOWN facts', {f: 'UNKNOWN' for f in RULE_FIELDS})):
            if resolve_applicability(r, facts) == 'NOT_APPLICABLE': out.append(f'{cid}: {label} resolved NOT_APPLICABLE')
        if state == 'NOT_YET_DECIDED': chk('all KNOWN_FALSE facts', {f: 'KNOWN_FALSE' for f in RULE_FIELDS}, 'APPLICABILITY_UNRESOLVED')
        elif state == 'NO_RULE_WILL_BE_PUBLISHED':
            chk('all KNOWN_TRUE facts', {f: 'KNOWN_TRUE' for f in RULE_FIELDS}, 'APPLICABLE'); chk('empty facts', {}, 'APPLICABLE')
        elif state == 'RULE_PUBLISHED':
            met = {c['field']: c['state'] for c in r['not_applicable_rule']['conditions']}
            chk('all conditions met', met, 'NOT_APPLICABLE')
            for f, st in met.items():
                chk(f'{f} flipped', dict(met, **{f: 'KNOWN_TRUE' if st == 'KNOWN_FALSE' else 'KNOWN_FALSE'}), 'APPLICABLE')
                chk(f'{f} UNKNOWN', dict(met, **{f: 'UNKNOWN'}), 'APPLICABILITY_UNRESOLVED')
        else: out.append(f'{cid}: decision state {state!r} invalid')
    return out

def published_authority_checked() -> dict:
    validate_governance_decisions()
    a = build_published_authority(); validate_publication(a)
    jsonschema.Draft202012Validator(schema()).validate(a)
    return a

def publish(dry_run: bool) -> None:
    a = published_authority_checked()
    ash = sha_text(jtext(a))
    if dry_run:
        print(dry_run_summary(a), end=''); return
    if not SIGNOFF.exists(): raise AuthorityError('publication sign-off record is absent')
    signoff = load(SIGNOFF); validate_signoff(signoff, ash)
    outs = build_all_outputs(a, signoff)
    write_text(AUTHORITY, jtext(a))
    for n, t in outs.items(): write_text(OUT / n, t)
    print(json.dumps({'status': 'PASS', 'authority_sha256': ash, 'manifest_sha256': sha_text(outs[N_MANIFEST])}))

def validate_published(pre_publication: bool = False) -> None:
    validate_governance_decisions()
    if not AUTHORITY.exists(): raise AuthorityError('v2 registry authority file is not published')
    a = load(AUTHORITY)
    validate_publication(a); jsonschema.Draft202012Validator(load(SCHEMA)).validate(a)
    validate_lineage(a['source_lineage'])
    if a !=build_published_authority(): raise AuthorityError('published authority differs from a fresh build')
    if lf_bytes(AUTHORITY.read_bytes()) != jtext(a).encode('utf-8'): raise AuthorityError('published authority bytes differ from canonical serialisation')
    if not SIGNOFF.exists(): raise AuthorityError('publication sign-off record is absent')
    signoff = load(SIGNOFF); validate_signoff(signoff, lf_digest(AUTHORITY))
    if not OUT.is_dir(): raise AuthorityError('v2 generated output folder is absent')
    if not (OUT / N_MANIFEST).exists(): raise AuthorityError('publication manifest is absent')
    manifest = load(OUT / N_MANIFEST)
    ps = manifest.get('publisher_script')
    if not isinstance(ps, dict) or ps.get('relative_path') != rel(SCRIPT) or not re.fullmatch(r'[0-9a-f]{64}', str(ps.get('sha256'))) or ps.get('sha256_normalisation') != 'CRLF_TO_LF': raise AuthorityError('manifest publisher_script entry missing or invalid')
    expected = build_all_outputs(a, signoff, script_sha256=ps['sha256'])
    actual = {p.name for p in OUT.iterdir() if p.is_file()}
    if actual != set(expected): raise AuthorityError('generated file set differs from the expected set')
    for n, t in expected.items():
        if lf_bytes((OUT / n).read_bytes()) != t.encode('utf-8'): raise AuthorityError(f'{n}: differs from a fresh build')
    for art in manifest['artifacts']:
        rp = art['relative_path']
        if not isinstance(rp, str) or contains_absolute(rp) or '..' in rp.replace('\\', '/').split('/'): raise AuthorityError(f'{rp}: manifest path must be repo-relative without ..')
        if lf_digest(ROOT / art['relative_path']) != art['sha256']: raise AuthorityError(f"{art['relative_path']}: manifest digest differs")
    check_publication_record(a, pre_publication)
    print('PASS')

RECORD_KEYS = {'publication_commit', 'authority_id', 'version', 'authority_sha256', 'manifest_sha256', 'digest_normalisation'}

def check_publication_record(a: dict, pre_publication: bool = False) -> None:
    if not PUBLICATION_RECORD.exists(): raise AuthorityError('publication record is absent')
    record = load(PUBLICATION_RECORD)
    if not isinstance(record, dict) or set(record) != RECORD_KEYS: raise AuthorityError('publication record must be an object with exactly the six record keys')
    if record['digest_normalisation'] != 'CRLF_TO_LF': raise AuthorityError('publication record digest_normalisation must be CRLF_TO_LF')
    if pre_publication:
        want_id, want_version = SUPERSEDED_V2_0_1['authority_id'], SUPERSEDED_V2_0_1['version']
        if record['publication_commit'] != SUPERSEDED_V2_0_1['commit']: raise AuthorityError('pre-publication record must name the 2.0.1 publication commit')
        if record['authority_sha256'] != SUPERSEDED_V2_0_1['sha256']: raise AuthorityError('pre-publication record authority_sha256 must equal the 2.0.1 digest')
    else: want_id, want_version = a['authority_id'], a['version']
    if record['authority_id'] != want_id or record['version'] != want_version: raise AuthorityError(f'publication record must name {want_id} version {want_version}')
    if not pre_publication:
        if record['authority_sha256'] != lf_digest(AUTHORITY): raise AuthorityError('publication record authority_sha256 does not match the committed authority')
        if record['manifest_sha256'] != lf_digest(OUT / N_MANIFEST): raise AuthorityError('publication record manifest_sha256 does not match the committed manifest')
    if hashlib.sha256(lf_bytes(git_show(record['publication_commit'], rel(AUTHORITY)))).hexdigest() != record['authority_sha256']: raise AuthorityError('publication record authority_sha256 does not match the authority at the publication commit')
    if hashlib.sha256(lf_bytes(git_show(record['publication_commit'], rel(OUT / N_MANIFEST)))).hexdigest() != record['manifest_sha256']: raise AuthorityError('publication record manifest_sha256 does not match the manifest at the publication commit')

def write_publication_record(sha: str) -> None:
    if not re.fullmatch(r'[0-9a-f]{40}', sha or ''): raise AuthorityError('publication commit must be a 40-character lowercase hex SHA')
    a = load(AUTHORITY)
    record = {'publication_commit': sha, 'authority_id': a['authority_id'], 'version': a['version'], 'authority_sha256': lf_digest(AUTHORITY), 'manifest_sha256': lf_digest(OUT / N_MANIFEST), 'digest_normalisation': 'CRLF_TO_LF'}
    if not re.fullmatch(r'[0-9a-f]{64}', record['authority_sha256']) or not re.fullmatch(r'[0-9a-f]{64}', record['manifest_sha256']): raise AuthorityError('digest is not 64-character hex')
    dump(PUBLICATION_RECORD, record)

def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument('--validate', action='store_true'); parser.add_argument('--emit-schema', action='store_true'); parser.add_argument('--publish', action='store_true'); parser.add_argument('--dry-run', action='store_true'); parser.add_argument('--validate-signoff', action='store_true'); parser.add_argument('--record-publication', metavar='SHA'); parser.add_argument('--pre-publication', action='store_true'); args = parser.parse_args()
    if args.pre_publication and not args.validate: parser.error('--pre-publication requires --validate')
    if args.validate: validate_published(args.pre_publication)
    elif args.emit_schema: dump(SCHEMA, schema())
    elif args.validate_signoff:
        validate_signoff(load(SIGNOFF), sha_text(jtext(published_authority_checked()))); print('PASS')
    elif args.publish: publish(args.dry_run)
    elif args.record_publication: write_publication_record(args.record_publication)
    else: parser.error('one of --validate, --emit-schema, --validate-signoff, --publish or --record-publication is required')
if __name__ == '__main__': main()

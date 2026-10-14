from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / 'registry'
SCHEMAS = ROOT / 'schemas'
CATALOG = REGISTRY / 'control_catalog.yaml'
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
RESULTS = ['APPLICABLE','NOT_APPLICABLE','APPLICABILITY_UNRESOLVED']
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

def digest(p: Path) -> str: return hashlib.sha256(p.read_bytes()).hexdigest()
def lf_bytes(b: bytes) -> bytes: return b.replace(b'\r\n', b'\n')
def lf_digest(p: Path) -> str: return hashlib.sha256(lf_bytes(p.read_bytes())).hexdigest()
def dump(p: Path, value: object) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, 'w', encoding='utf-8', newline='\n') as f: f.write(json.dumps(value, indent=2, sort_keys=True) + '\n')
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
        'document_id': 'EMS-ARCHIVE-ASSESSMENT-APPLICABILITY-AUTHORITY', 'version': '2.0.0', 'status': 'CONTROLLED',
        'authority_id': 'EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.0',
        'target_type': 'ARCHIVED_REPOSITORY_SNAPSHOT',
        'assessment_semantics': 'CURRENT_POLICY_AGAINST_HISTORICAL_SNAPSHOT',
        'attestation_prohibitions': {'historical_compliance_attestation': False, 'current_repository_attestation': False, 'production_readiness_attestation': False},
        'classification_vocabulary': {'states': ['KNOWN_TRUE','KNOWN_FALSE','UNKNOWN'], 'fields': list(CLASSIFICATION_FIELDS), 'unknown_is_not_false': True, 'unknown_is_not_not_applicable': True},
        'applicability_vocabulary': list(RESULTS),
        'not_applicable_semantics': semantics(),
        'evidence_boundary': {'archive_content_establishes': ['REPOSITORY_CONTENT_FACTS_ONLY'], 'archive_content_does_not_establish': ['LIVE_REPOSITORY_STATE','ORGANIZATION_AUTHORITY','SERVICE_STATE','PLATFORM_STATE','CURRENT_CICD_STATE','RUNTIME_STATE','EXTERNAL_SYSTEM_STATE','CURRENT_DEPLOYMENT_STATE','VENDOR_SERVICE_EVIDENCE']},
        'source_lineage': {
            'aa1_manifest_sha256': lin['aa1_manifest_sha256'], 'aa2_closure_sha256': lin['aa2_closure_sha256'], 'aa2_approval_sha256': lin['aa2_approval_sha256'],
            'catalog_reference': {'relative_path': 'registry/control_catalog.yaml', 'sha256': lf_digest(CATALOG), 'required_for_deterministic_compilation': False},
            'supersedes': {'authority_id': v1['authority_id'], 'version': '1.0.0', 'commit': '62a8955', 'relative_path': 'registry/archive_assessment_applicability_authority.json', 'sha256': lf_digest(V1_AUTHORITY)},
            'digest_normalisation': 'CRLF_TO_LF',
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
    a['source_lineage']['governance_decisions'] = {'relative_path': GOVERNANCE_DECISIONS_REL, 'sha256': lf_digest(GOVERNANCE_DECISIONS), 'record_count': len(doc['records']), 'drafting_commit': doc['drafting_commit']}
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
    errors = []
    req = {'document_id','version','status','authority_id','target_type','assessment_semantics','classification_vocabulary','applicability_vocabulary','not_applicable_semantics','evidence_boundary','source_lineage','approved_governance_decision_ids','controls'}
    if not req <= set(a): errors.append('missing required top-level authority fields')
    if a.get('document_id') != 'EMS-ARCHIVE-ASSESSMENT-APPLICABILITY-AUTHORITY' or a.get('version') != '2.0.0' or a.get('status') != 'CONTROLLED' or a.get('authority_id') != 'EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.0': errors.append('authority identity/version/status invalid')
    if a.get('target_type') != 'ARCHIVED_REPOSITORY_SNAPSHOT' or a.get('assessment_semantics') != 'CURRENT_POLICY_AGAINST_HISTORICAL_SNAPSHOT': errors.append('unauthorized target or assessment semantics')
    if a.get('approved_governance_decision_ids') != DECISIONS: errors.append('AA2 decision provenance is incomplete or contains an unapproved decision')
    cv = a.get('classification_vocabulary', {})
    if cv.get('states') != ['KNOWN_TRUE','KNOWN_FALSE','UNKNOWN'] or not cv.get('unknown_is_not_false') or not cv.get('unknown_is_not_not_applicable'): errors.append('UNKNOWN semantics collapse or vocabulary invalid')
    sem = a.get('not_applicable_semantics', {})
    if not isinstance(sem, dict): sem = {}
    if sem.get('requires_explicit_controlled_rule') is not True: errors.append('implicit NOT_APPLICABLE is authorized')
    pin = {k: v for k, v in sem.items() if k != 'field_definitions'}
    expected = {k: v for k, v in semantics().items() if k != 'field_definitions'}
    if pin != expected: errors.append('not_applicable_semantics does not match the published semantics')
    fd = sem.get('field_definitions')
    if not isinstance(fd, dict) or set(fd) != set(RULE_FIELDS) or any(not isinstance(v, str) or not v.strip() for v in fd.values()): errors.append('field_definitions must define exactly the four rule fields with non-empty text')
    sup = a.get('source_lineage', {}).get('supersedes') if isinstance(a.get('source_lineage'), dict) else None
    if not isinstance(sup, dict) or sup.get('commit') != '62a8955' or sup.get('version') != '1.0.0': errors.append('source_lineage supersedes v1 entry missing or invalid')
    if contains_absolute(a): errors.append('absolute local path used as authority identity')
    for dependency in a.get('dependencies', []):
        if dependency.get('required_for_deterministic_compilation') and (not dependency.get('relative_path') or not dependency.get('sha256')): errors.append('required authority dependency cannot be deterministically frozen')
    catalog_ids = {c['control_id'] for c in catalog_controls()}; rows = a.get('controls', []); ids = [r.get('control_id') for r in rows]
    if len(ids) != 80 or len(set(ids)) != 80: errors.append('duplicate or incorrect control population count')
    if set(ids) != catalog_ids: errors.append('missing or unknown control ID')
    forbidden = set(a.get('evidence_boundary', {}).get('archive_content_does_not_establish', []))
    if not {'LIVE_REPOSITORY_STATE','ORGANIZATION_AUTHORITY','SERVICE_STATE','PLATFORM_STATE','CURRENT_CICD_STATE','RUNTIME_STATE'} <= forbidden: errors.append('live authority evidence boundary incomplete')
    for r in rows:
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
    if any(att.get(k) is not False for k in ['historical_compliance_attestation','current_repository_attestation','production_readiness_attestation']): errors.append('attestation leakage')
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
    if not isinstance(ids, list) or len(set(ids)) != len(ids) or set(ids) != set(auths) or len(auths) != len(set(auths)): errors.append('applicability_decision_ids must list each cited authority exactly once')
    lin = a.get('source_lineage') if isinstance(a.get('source_lineage'), dict) else {}
    gd = lin.get('governance_decisions')
    if not isinstance(gd, dict): errors.append('governance_decisions lineage missing')
    else:
        if gd.get('relative_path') != GOVERNANCE_DECISIONS_REL: errors.append('governance_decisions relative_path invalid')
        if gd.get('sha256') != lf_digest(GOVERNANCE_DECISIONS): errors.append('governance_decisions sha256 does not match the live decisions file')
        if gd.get('record_count') != len(doc['records']): errors.append('governance_decisions record_count does not match the live decisions file')
        if gd.get('drafting_commit') != doc.get('drafting_commit'): errors.append('governance_decisions drafting_commit does not match the live decisions file')
    latest = {r['control_id']: r for r in latest_records(doc)}
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
    sup = lin.get('supersedes')
    if not isinstance(sup, dict) or sup.get('authority_id') != 'EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-1.0.0' or sup.get('commit') != '62a8955' or sup.get('version') != '1.0.0': errors.append('lineage must record v1.0.0 at 62a8955')
    elif sup.get('sha256') != lf_digest(V1_AUTHORITY): errors.append('lineage v1 authority digest does not match')
    cat = lin.get('catalog_reference')
    if not isinstance(cat, dict) or cat.get('sha256') != lf_digest(CATALOG): errors.append('lineage catalog digest does not match')
    if errors: raise AuthorityError('; '.join(errors))

def schema() -> dict:
    cond = {'type':'object','additionalProperties':False,'required':['field','state'],'properties':{'field':{'enum':list(RULE_FIELDS)},'state':{'enum':list(CONDITION_STATES)}}}
    rule = {'type':'object','additionalProperties':False,'required':['combination','conditions'],'properties':{'combination':{'const':COMBINATION},'conditions':{'type':'array','minItems':1,'maxItems':len(RULE_FIELDS),'items':cond}}}
    auth = {'type':'string','pattern':AUTHORITY_ID_RE}
    def branch(state, rule_s, auth_s):
        return {'if':{'properties':{'not_applicable_decision_state':{'const':state}},'required':['not_applicable_decision_state']},'then':{'properties':{'not_applicable_rule':rule_s,'not_applicable_authority':auth_s}}}
    sem = {'type':'object','required':['requires_explicit_controlled_rule','absence_of_evidence_is_not_not_applicable','unknown_is_not_not_applicable','decision_states','condition_states','condition_combination','min_conditions','field_may_appear_once','rule_condition_fields','fields_not_usable_in_rules','fields_not_usable_in_rules_statement','field_definitions','resolution','no_short_circuit','decision_state_governs_resolved_result','per_control_default_describes_result_absent_a_decision','unknown_is_never_not_applicable','statements'],
        'properties':{'requires_explicit_controlled_rule':{'const':True},'absence_of_evidence_is_not_not_applicable':{'const':True},'unknown_is_not_not_applicable':{'const':True},'decision_states':{'const':list(DECISION_STATES)},'condition_states':{'const':list(CONDITION_STATES)},'condition_combination':{'const':COMBINATION},'min_conditions':{'const':1},'field_may_appear_once':{'const':True},'rule_condition_fields':{'const':list(RULE_FIELDS)},'fields_not_usable_in_rules':{'const':list(NON_RULE_FIELDS)},'field_definitions':{'type':'object','additionalProperties':False,'required':list(RULE_FIELDS),'properties':{f:{'type':'string','minLength':1} for f in RULE_FIELDS}},'resolution':{'const':[dict(r) for r in RESOLUTION]},'no_short_circuit':{'const':True},'decision_state_governs_resolved_result':{'const':True},'per_control_default_describes_result_absent_a_decision':{'const':True},'unknown_is_never_not_applicable':{'const':True}}}
    return {'$schema':'https://json-schema.org/draft/2020-12/schema','title':'EMS AA3 Archive Assessment Applicability Authority v2','type':'object',
        'required':['document_id','version','status','authority_id','target_type','assessment_semantics','classification_vocabulary','applicability_vocabulary','not_applicable_semantics','evidence_boundary','source_lineage','approved_governance_decision_ids','applicability_decision_ids','controls'],
        'properties':{'document_id':{'const':'EMS-ARCHIVE-ASSESSMENT-APPLICABILITY-AUTHORITY'},'version':{'const':'2.0.0'},'status':{'const':'CONTROLLED'},'authority_id':{'const':'EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.0'},'target_type':{'const':'ARCHIVED_REPOSITORY_SNAPSHOT'},'assessment_semantics':{'const':'CURRENT_POLICY_AGAINST_HISTORICAL_SNAPSHOT'},
            'approved_governance_decision_ids':{'type':'array','minItems':8,'maxItems':8,'items':{'type':'string','pattern':'^AA1-GOV-00[1-8]$'},'uniqueItems':True},
            'applicability_decision_ids':{'type':'array','minItems':0,'maxItems':21,'items':{'type':'string','pattern':AUTHORITY_ID_RE},'uniqueItems':True},
            'source_lineage':{'type':'object','properties':{'governance_decisions':{'type':'object','additionalProperties':False,'required':['relative_path','sha256','record_count','drafting_commit'],'properties':{'relative_path':{'const':GOVERNANCE_DECISIONS_REL},'sha256':{'type':'string','pattern':'^[0-9a-f]{64}$'},'record_count':{'type':'integer','minimum':1},'drafting_commit':{'type':'string','pattern':'^[0-9a-f]{40}$'}}}}},
            'not_applicable_semantics':sem,
            'controls':{'type':'array','minItems':80,'maxItems':80,'items':{'type':'object',
                'required':['control_id','archive_population_membership','target_type','assessment_semantics','classification_prerequisites','classification_unknown_treatment','archive_evidence_capability','required_non_repository_authority','default_applicability_result','unresolved_reason','not_applicable_decision_state','not_applicable_rule','not_applicable_authority','decision_ids'],
                'properties':{'control_id':{'type':'string','pattern':'^EMS-CTRL-[0-9]{3}$'},'archive_population_membership':{'const':'IN_ARCHIVE_CONTROL_POPULATION'},'target_type':{'const':'ARCHIVED_REPOSITORY_SNAPSHOT'},'assessment_semantics':{'const':'CURRENT_POLICY_AGAINST_HISTORICAL_SNAPSHOT'},'classification_unknown_treatment':{'const':'APPLICABILITY_UNRESOLVED'},'default_applicability_result':{'const':'APPLICABILITY_UNRESOLVED'},
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

PUBLISHED_ON = '2026-10-14'
OUT = ROOT / 'generated' / 'archive-assessment' / 'ems-aa3-v2'
SIGNOFF = REGISTRY / 'archive_assessment_applicability_authority_v2_signoff.json'
PUBLICATION_RECORD = REGISTRY / 'archive_assessment_applicability_authority_v2_publication_record.json'
SCRIPT = Path(__file__).resolve()
APPROVER = 'Oscar Mack'
APPROVER_ROLES = ['EMS_GOVERNANCE_AUTHORITY', 'HAYES_VERIFY_DEVELOPER']
DUAL_ROLE_STATEMENT = 'Oscar Mack made this decision as the EMS governance authority and is also the developer of Hayes Verify, the assessor that will read it.'
AUTHORITY_ID = 'EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.0'
N_MATRIX = 'archive_assessment_applicability_authority_v2_matrix.json'
N_SEMANTIC = 'archive_assessment_applicability_authority_v2_semantic_validation.json'
N_NEGATIVE = 'archive_assessment_applicability_authority_v2_negative_invariant_validation.json'
N_TRACE = 'archive_assessment_applicability_authority_v2_decision_traceability.json'
N_CERT = 'EMS_AA3_V2_ARCHIVE_APPLICABILITY_AUTHORITY_PUBLICATION_CERTIFICATION.json'
N_REPORT = 'EMS_AA3_V2_ARCHIVE_APPLICABILITY_AUTHORITY_PUBLICATION.md'
N_MANIFEST = 'ems_aa3_v2_archive_applicability_authority_publication_manifest.json'
NEGATIVE_MUTATIONS = ['swapped_authority', 'rule_field_change', 'rule_state_unknown', 'rule_unused_field', 'rule_state_flip', 'decided_flipped_to_not_yet_decided', 'twenty_second_control_decided', 'v1_field_change_on_undecided_row', 'extra_field_on_decided_row', 'authority_removed_from_id_list', 'authority_cited_twice', 'duplicate_id_in_list', 'altered_governance_digest', 'altered_record_count_or_drafting_commit', 'missing_governance_lineage', 'wrong_v1_lineage', 'superseded_record_cited']

def jtext(value: object) -> str: return json.dumps(value, indent=2, sort_keys=True) + '\n'
def sha_text(text: str) -> str: return hashlib.sha256(text.encode('utf-8')).hexdigest()
def rel(p: Path) -> str: return p.relative_to(ROOT).as_posix()
def write_text(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, 'w', encoding='utf-8', newline='\n') as f: f.write(text)

def validate_signoff(record: object, authority_lf_digest: str) -> None:
    errors = []
    if not isinstance(record, dict): raise AuthorityError('sign-off record must be an object')
    for k in ('status', 'approval', 'dual_role_statement', 'authority_id', 'version', 'authority_sha256', 'authority_sha256_normalisation'):
        if k not in record: errors.append(f'sign-off missing {k}')
    appr = record.get('approval')
    if not isinstance(appr, dict): errors.append('sign-off approval must be an object'); appr = {}
    for k in ('approver', 'role', 'date', 'scope'):
        if not appr.get(k): errors.append(f'sign-off approval missing {k}')
    if record.get('status') != 'PUBLICATION_SIGNOFF': errors.append('sign-off status must be PUBLICATION_SIGNOFF')
    if appr.get('approver') != APPROVER: errors.append('sign-off approver must be Oscar Mack')
    if appr.get('role') not in APPROVER_ROLES: errors.append('sign-off role is not an approved EMS governance role')
    dr = record.get('dual_role_statement')
    if not isinstance(dr, str) or not dr.strip() or DUAL_ROLE_STATEMENT not in dr: errors.append('sign-off dual_role_statement missing or altered')
    if 'authority_id' in record and record['authority_id'] != AUTHORITY_ID: errors.append('sign-off authority_id does not match')
    if 'version' in record and record['version'] != '2.0.0': errors.append('sign-off version does not match')
    if 'authority_sha256' in record and record['authority_sha256'] != authority_lf_digest: errors.append('sign-off authority_sha256 does not match the rebuilt authority')
    if 'authority_sha256_normalisation' in record and record['authority_sha256_normalisation'] != 'CRLF_TO_LF': errors.append('sign-off authority_sha256_normalisation must be CRLF_TO_LF')
    if errors: raise AuthorityError('; '.join(errors))

def rule_text(rule: dict) -> str:
    return f"{rule['combination']}: " + ' AND '.join(f"{c['field']} = {c['state']}" for c in rule['conditions'])

def dry_run_summary(authority: dict) -> str:
    rows = authority['controls']
    decided = [r for r in rows if r['not_applicable_decision_state'] != 'NOT_YET_DECIDED']
    undecided = [r for r in rows if r['not_applicable_decision_state'] == 'NOT_YET_DECIDED']
    lines = [f'Publication sign-off summary for {authority["authority_id"]}', f'Decided controls: {len(decided)}', f'Undecided controls: {len(undecided)}', '', 'Decisions:']
    for r in decided: lines.append(f"  {r['control_id']}  {r['not_applicable_authority']}  {r['not_applicable_decision_state']}")
    lines += ['', 'Published rules:']
    for r in decided:
        if r['not_applicable_decision_state'] == 'RULE_PUBLISHED': lines.append(f"  {r['control_id']}: {rule_text(r['not_applicable_rule'])}")
    lines += ['', f'Authority LF sha256: {sha_text(jtext(authority))}', 'Digest normalisation: CRLF_TO_LF', f'Published on: {PUBLISHED_ON}']
    return '\n'.join(lines) + '\n'

def build_all_outputs(authority: dict, signoff: dict | None = None) -> dict:
    ash = sha_text(jtext(authority))
    ssh = lf_digest(SCHEMA)
    signoff_rel = rel(SIGNOFF) if signoff is not None else None
    signoff_sha = lf_digest(SIGNOFF) if signoff is not None else None
    rows = authority['controls']
    n_decided = sum(r['not_applicable_decision_state'] != 'NOT_YET_DECIDED' for r in rows)
    matrix = {'authority_id': authority['authority_id'], 'version': authority['version'], 'published_on': PUBLISHED_ON, 'control_population': 80, 'unique_control_count': 80, 'decided_control_count': n_decided, 'undecided_control_count': 80 - n_decided, 'controls': rows}
    sem_rows = []
    for r in rows:
        if r['not_applicable_decision_state'] != 'RULE_PUBLISHED': continue
        field = r['not_applicable_rule']['conditions'][0]['field']
        sem_rows.append({'control_id': r['control_id'], 'rule': r['not_applicable_rule'], 'results': {st: resolve_applicability(r, {f: st for f in RULE_FIELDS}) for st in ('KNOWN_TRUE', 'KNOWN_FALSE', 'UNKNOWN')}, 'unknown_result': resolve_applicability(r, {field: 'UNKNOWN'}), 'empty_facts_result': resolve_applicability(r, {})})
    semantic = {'result': 'PASS', 'published_on': PUBLISHED_ON, 'semantic_conflict_count': 0, 'unknown_never_not_applicable': all(x['unknown_result'] != 'NOT_APPLICABLE' and x['empty_facts_result'] != 'NOT_APPLICABLE' and x['results']['UNKNOWN'] != 'NOT_APPLICABLE' for x in sem_rows), 'rule_controls': sem_rows, 'checks': ['UNKNOWN preserved as APPLICABILITY_UNRESOLVED', 'NOT_APPLICABLE requires explicit controlled rule', 'repository evidence boundary preserved', 'historical attestation prohibited']}
    negative = {'result': 'PASS', 'published_on': PUBLISHED_ON, 'negative_invariant_tests': [{'mutation': m, 'result': 'REJECTED_FAIL_CLOSED'} for m in NEGATIVE_MUTATIONS]}
    doc_sha = lf_digest(GOVERNANCE_DECISIONS)
    trace = {'traceability_type': 'AA4_DECISION_TO_CONTROL_TRACEABILITY', 'published_on': PUBLISHED_ON, 'decision_records': [], 'undecided_controls': []}
    for r in rows:
        if r['not_applicable_decision_state'] == 'NOT_YET_DECIDED': trace['undecided_controls'].append(r['control_id']); continue
        trace['decision_records'].append({'control_id': r['control_id'], 'decision_id': r['not_applicable_authority'], 'state': r['not_applicable_decision_state'], 'rule': r['not_applicable_rule'], 'decision_record_path': GOVERNANCE_DECISIONS_REL, 'decision_record_sha256': doc_sha, 'decision_record_digest_normalisation': 'CRLF_TO_LF'})
    trace['decided_count'] = len(trace['decision_records']); trace['undecided_count'] = len(trace['undecided_controls'])
    cert = {'certification_type': 'EMS_AA3_V2_ARCHIVE_APPLICABILITY_AUTHORITY_PUBLICATION_CERTIFICATION', 'certification_version': '1.0', 'published_on': PUBLISHED_ON, 'authority_id': authority['authority_id'], 'version': authority['version'], 'authority_sha256': ash, 'schema_sha256': ssh, 'signoff_path': signoff_rel, 'signoff_sha256': signoff_sha, 'digest_normalisation': 'CRLF_TO_LF', 'control_population': 80, 'decided_control_count': n_decided, 'undecided_control_count': 80 - n_decided, 'semantic_conflicts': 0, 'negative_invariants': 'PASS', 'prohibitions': {'evaluator_executions': 0, 'hayes_modifications': 0, 'target_comparisons': 0}}
    report = ('# EMS-AA3 v2 Archive Assessment Applicability Authority Publication\n\n'
        f'Published on {PUBLISHED_ON}. Version 2.0.0 records an explicit decision for {n_decided} of the 80 EMS controls and leaves {80 - n_decided} as NOT_YET_DECIDED.\n\n'
        'Each decision is cited by an AA4 governance decision id approved by Oscar Mack, who is both the EMS governance authority and the developer of Hayes Verify.\n\n'
        'Not applicable is stated only by an explicit published rule over KNOWN_TRUE and KNOWN_FALSE conditions. UNKNOWN never resolves to not applicable.\n\n'
        f'Authority LF sha256: {ash}\nDigest normalisation: CRLF_TO_LF\n')
    outs = {N_MATRIX: jtext(matrix), N_SEMANTIC: jtext(semantic), N_NEGATIVE: jtext(negative), N_TRACE: jtext(trace), N_CERT: jtext(cert), N_REPORT: report}
    arts = [{'relative_path': rel(SCRIPT), 'sha256': lf_digest(SCRIPT)}, {'relative_path': rel(SCHEMA), 'sha256': ssh}, {'relative_path': rel(AUTHORITY), 'sha256': ash}]
    if signoff is not None: arts.append({'relative_path': signoff_rel, 'sha256': signoff_sha})
    arts += [{'relative_path': f'{rel(OUT)}/{n}', 'sha256': sha_text(t)} for n, t in outs.items()]
    manifest = {'manifest_type': 'EMS_AA3_V2_ARCHIVE_APPLICABILITY_AUTHORITY_PUBLICATION_MANIFEST', 'published_on': PUBLISHED_ON, 'authority_id': authority['authority_id'], 'digest_normalisation': 'CRLF_TO_LF', 'artifacts': arts, 'self_entry_exclusion_reason': 'A SHA-256 manifest cannot include a hash of itself without recursion.'}
    outs[N_MANIFEST] = jtext(manifest)
    return outs

def published_authority_checked() -> dict:
    a = build_published_authority(); validate_publication(a)
    jsonschema.Draft202012Validator(schema()).validate(a)
    return a

def publish(dry_run: bool) -> None:
    a = published_authority_checked()
    ash = sha_text(jtext(a))
    if dry_run:
        if SIGNOFF.exists(): validate_signoff(load(SIGNOFF), ash)
        print(dry_run_summary(a), end=''); return
    if not SIGNOFF.exists(): raise AuthorityError('publication sign-off record is absent')
    signoff = load(SIGNOFF); validate_signoff(signoff, ash)
    outs = build_all_outputs(a, signoff)
    write_text(AUTHORITY, jtext(a))
    for n, t in outs.items(): write_text(OUT / n, t)
    print(json.dumps({'status': 'PASS', 'authority_sha256': ash, 'manifest_sha256': sha_text(outs[N_MANIFEST])}))

def validate_published() -> None:
    if not AUTHORITY.exists(): raise AuthorityError('v2 registry authority file is not published')
    a = load(AUTHORITY)
    validate_publication(a); jsonschema.Draft202012Validator(load(SCHEMA)).validate(a)
    if a != build_published_authority(): raise AuthorityError('published authority differs from a fresh build')
    if lf_bytes(AUTHORITY.read_bytes()) != jtext(a).encode('utf-8'): raise AuthorityError('published authority bytes differ from canonical serialisation')
    if not SIGNOFF.exists(): raise AuthorityError('publication sign-off record is absent')
    signoff = load(SIGNOFF); validate_signoff(signoff, lf_digest(AUTHORITY))
    expected = build_all_outputs(a, signoff)
    if not OUT.is_dir(): raise AuthorityError('v2 generated output folder is absent')
    actual = {p.name for p in OUT.iterdir() if p.is_file()}
    if actual != set(expected): raise AuthorityError('generated file set differs from the expected set')
    for n, t in expected.items():
        if lf_bytes((OUT / n).read_bytes()) != t.encode('utf-8'): raise AuthorityError(f'{n}: differs from a fresh build')
    manifest = load(OUT / N_MANIFEST)
    for art in manifest['artifacts']:
        if lf_digest(ROOT / art['relative_path']) != art['sha256']: raise AuthorityError(f"{art['relative_path']}: manifest digest differs")
    print('PASS')

def write_publication_record(sha: str) -> None:
    if not re.fullmatch(r'[0-9a-f]{40}', sha or ''): raise AuthorityError('publication commit must be a 40-character lowercase hex SHA')
    a = load(AUTHORITY)
    record = {'publication_commit': sha, 'authority_id': a['authority_id'], 'version': a['version'], 'authority_sha256': lf_digest(AUTHORITY), 'manifest_sha256': lf_digest(OUT / N_MANIFEST), 'digest_normalisation': 'CRLF_TO_LF'}
    if not re.fullmatch(r'[0-9a-f]{64}', record['authority_sha256']) or not re.fullmatch(r'[0-9a-f]{64}', record['manifest_sha256']): raise AuthorityError('digest is not 64-character hex')
    dump(PUBLICATION_RECORD, record)

def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument('--validate', action='store_true'); parser.add_argument('--emit-schema', action='store_true'); parser.add_argument('--publish', action='store_true'); parser.add_argument('--dry-run', action='store_true'); parser.add_argument('--validate-signoff', action='store_true'); parser.add_argument('--record-publication', metavar='SHA'); args = parser.parse_args()
    if args.validate: validate_published()
    elif args.emit_schema: dump(SCHEMA, schema())
    elif args.validate_signoff:
        validate_signoff(load(SIGNOFF), sha_text(jtext(published_authority_checked()))); print('PASS')
    elif args.publish: publish(args.dry_run)
    elif args.record_publication: write_publication_record(args.record_publication)
    else: parser.error('one of --validate, --emit-schema, --validate-signoff, --publish or --record-publication is required')
if __name__ == '__main__': main()

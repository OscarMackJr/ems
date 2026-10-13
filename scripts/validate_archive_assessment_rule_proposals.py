from __future__ import annotations

import argparse
import hashlib
import importlib.util
import re
import subprocess
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / 'registry'
SCHEMAS = ROOT / 'schemas'
DOCS = ROOT / 'docs'

_spec = importlib.util.spec_from_file_location('aa_applicability_publisher_v2', ROOT / 'scripts' / 'publish_archive_assessment_applicability_authority_v2.py')
V2 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(V2)
AuthorityError = V2.AuthorityError

CATALOG = REGISTRY / 'control_catalog.yaml'
PROPOSALS = REGISTRY / 'archive_assessment_not_applicable_rule_proposals.json'
RECORD = REGISTRY / 'archive_assessment_rule_proposals_drafting_record.json'
BRIEF = DOCS / 'ARCHIVE_ASSESSMENT_RULE_DRAFTER_BRIEF.md'
SCHEMA = SCHEMAS / 'archive_assessment_not_applicable_rule_proposals.schema.json'
RECORD_SCHEMA = SCHEMAS / 'archive_assessment_rule_proposals_drafting_record.schema.json'
CATALOG_REL = 'registry/control_catalog.yaml'
CONTROL_IDS = [f'EMS-CTRL-{n:03d}' for n in (9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22, 30, 33, 39, 42, 52, 62, 75, 79)]
STATUS = 'DRAFT_NO_AUTHORITY'
RECORD_STATUS = 'DRAFTING_RECORD'
OUTCOMES = ['PROPOSE_RULE', 'PROPOSE_NO_RULE']
CONFIDENCE = ['HIGH', 'MEDIUM', 'LOW']
INTERPRETATION_LABEL = 'DRAFTER_ASSUMPTION_NOT_AN_EMS_SOURCE'
CATALOG_INPUT_REQUIRED = ['control_name', 'scope', 'scope_owner', 'evidence_authority']
CATALOG_INPUT_OPTIONAL = ['inheritance_allowed', 'classification_status']
NON_AUTHORITY_STATEMENT = 'This file is a set of drafts. It is not an authority, it binds nothing and it must not be cited as a decision.'
CATALOG_NOTE = 'None of the 21 requested catalog entries carries a description, and the catalog seed rationale field is boilerplate, not a definition.'
RECORD_STATEMENT = 'An AI agent drafted these proposals and holds no EMS authority. The proposals bind nothing until they are decided by the EMS governance authority.'
FORBIDDEN_KEYS = {'not_applicable_authority', 'not_applicable_decision_state', 'decision_id', 'decision_ids'}
FORBIDDEN_ID_RE = re.compile(r'AA[0-9]+-GOV-')
HEX40 = r'^[0-9a-f]{40}$'
HEX64 = r'^[0-9a-f]{64}$'
DATE_RE = r'^[0-9]{4}-[0-9]{2}-[0-9]{2}$'
PROPOSAL_KEYS = ['control_id', 'proposed_outcome', 'proposed_rule', 'catalog_inputs', 'interpretation', 'rationale', 'confidence', 'alternative_considered', 'shape_limitation']
HEADER_KEYS = ['status', 'non_authority_statement', 'drafting_frame', 'catalog_source']
RECORD_KEYS = ['status', 'drafting_commit', 'proposals_path', 'proposals_sha256', 'catalog_path', 'catalog_sha256', 'catalog_git_blob_id', 'brief_path', 'brief_sha256', 'brief_commit', 'brief_approval', 'validator_script', 'validator_result', 'correction_rounds', 'discarded_attempts', 'drafted_on', 'isolation_method', 'drafter', 'statement']
APPROVAL_KEYS = ['approver', 'role', 'date', 'scope']
ISOLATION_PHRASE = 'by instruction and brief design'

def git(*args: str) -> bytes:
    r = subprocess.run(['git', *args], cwd=ROOT, capture_output=True)
    if r.returncode != 0: raise AuthorityError(f'git {args[0]} failed: {r.stderr.decode("utf-8", "replace").strip()}')
    return r.stdout

def catalog_fingerprint() -> dict:
    blob = git('hash-object', CATALOG_REL).decode('ascii').strip()
    data = git('cat-file', 'blob', blob)
    return {'relative_path': CATALOG_REL, 'git_blob_id': blob, 'sha256': hashlib.sha256(data).hexdigest()}

def expected_header() -> dict:
    src = catalog_fingerprint(); src['entries_have_description'] = False; src['note'] = CATALOG_NOTE
    return {'status': STATUS, 'non_authority_statement': NON_AUTHORITY_STATEMENT, 'drafting_frame': V2.semantics(), 'catalog_source': src}

def live_catalog() -> dict:
    return {c['control_id']: c for c in V2.catalog_controls() if c['control_id'] in CONTROL_IDS}

def nonempty(v: object) -> bool: return isinstance(v, str) and bool(v.strip())

def walk_forbidden(value: object, path: str, errors: list) -> None:
    if isinstance(value, dict):
        for k, v in value.items():
            if k in FORBIDDEN_KEYS: errors.append(f'{path}: forbidden key {k!r}')
            walk_forbidden(v, f'{path}.{k}', errors)
    elif isinstance(value, list):
        for i, v in enumerate(value): walk_forbidden(v, f'{path}[{i}]', errors)
    elif isinstance(value, str) and FORBIDDEN_ID_RE.search(value): errors.append(f'{path}: governance decision id string not allowed')

def validate_proposal(p: object, catalog: dict, errors: list) -> None:
    if not isinstance(p, dict): errors.append('proposal must be an object'); return
    cid = p.get('control_id')
    if set(p) != set(PROPOSAL_KEYS): errors.append(f'{cid}: proposal keys must be exactly {PROPOSAL_KEYS}'); return
    outcome = p['proposed_outcome']
    if outcome not in OUTCOMES: errors.append(f'{cid}: proposed_outcome invalid')
    elif outcome == 'PROPOSE_RULE': V2.validate_rule(cid, p['proposed_rule'], errors)
    elif p['proposed_rule'] is not None: errors.append(f'{cid}: PROPOSE_NO_RULE requires null proposed_rule')
    entry = catalog.get(cid)
    ci = p['catalog_inputs']
    if not isinstance(ci, dict): errors.append(f'{cid}: catalog_inputs must be an object')
    else:
        if not set(CATALOG_INPUT_REQUIRED) <= set(ci) or not set(ci) <= set(CATALOG_INPUT_REQUIRED + CATALOG_INPUT_OPTIONAL): errors.append(f'{cid}: catalog_inputs keys invalid')
        for k, v in ci.items():
            if entry is not None and (k not in entry or entry[k] != v): errors.append(f'{cid}: catalog_inputs {k} does not equal the live catalog value')
    it = p['interpretation']
    if not isinstance(it, dict) or set(it) != {'label', 'text'} or it.get('label') != INTERPRETATION_LABEL or not nonempty(it.get('text')): errors.append(f'{cid}: interpretation must carry label {INTERPRETATION_LABEL} and non-empty text')
    r = p['rationale']
    if not nonempty(r) or not 2 <= len(re.findall(r'[.!?](\s|$)', r.strip())) <= 4: errors.append(f'{cid}: rationale must be 2 to 4 sentences')
    if p['confidence'] not in CONFIDENCE: errors.append(f'{cid}: confidence invalid')
    alt = p['alternative_considered']
    if alt is not None and (not isinstance(alt, dict) or set(alt) != {'outcome', 'why'} or alt.get('outcome') not in OUTCOMES or alt.get('outcome') == outcome or not nonempty(alt.get('why'))): errors.append(f'{cid}: alternative_considered invalid')
    sl = p['shape_limitation']
    if sl is not None and (not isinstance(sl, dict) or set(sl) != {'scope', 'note'} or entry is None or sl.get('scope') != entry.get('scope') or not nonempty(sl.get('note'))): errors.append(f'{cid}: shape_limitation invalid')

def validate_proposals(p: dict, catalog: dict | None = None) -> None:
    errors: list = []
    if catalog is None: catalog = live_catalog()
    if not isinstance(p, dict): raise AuthorityError('proposals document must be an object')
    if set(p) != set(HEADER_KEYS + ['proposals']): errors.append('top-level keys must be exactly the header keys and proposals')
    exp = expected_header()
    for k in HEADER_KEYS:
        if p.get(k) != exp[k]: errors.append(f'header field {k} does not equal the expected value')
    items = p.get('proposals')
    if not isinstance(items, list): errors.append('proposals must be a list')
    else:
        ids = [x.get('control_id') if isinstance(x, dict) else None for x in items]
        if len(items) != len(CONTROL_IDS) or len(set(ids)) != len(ids) or set(ids) != set(CONTROL_IDS): errors.append('proposals must cover exactly the 21 requested control ids once each')
        for x in items: validate_proposal(x, catalog, errors)
    walk_forbidden(p, 'proposals', errors)
    if V2.contains_absolute(p): errors.append('absolute path used in proposals')
    if errors: raise AuthorityError('; '.join(errors))

def validate_record(r: dict) -> None:
    errors: list = []
    if not isinstance(r, dict): raise AuthorityError('record must be an object')
    if set(r) != set(RECORD_KEYS): raise AuthorityError(f'record keys must be exactly {RECORD_KEYS}')
    def rx(k, pat):
        if not isinstance(r[k], str) or not re.match(pat, r[k]): errors.append(f'{k} invalid')
    if r['status'] != RECORD_STATUS: errors.append('status invalid')
    rx('drafting_commit', HEX40); rx('proposals_sha256', HEX64); rx('catalog_sha256', HEX64); rx('catalog_git_blob_id', HEX40); rx('brief_sha256', HEX64); rx('brief_commit', HEX40); rx('drafted_on', DATE_RE)
    for k in ('proposals_path', 'catalog_path', 'brief_path', 'validator_script'):
        if not nonempty(r[k]): errors.append(f'{k} invalid')
    ba = r['brief_approval']
    if not isinstance(ba, dict) or set(ba) != set(APPROVAL_KEYS) or any(not nonempty(ba.get(k)) for k in APPROVAL_KEYS) or not re.match(DATE_RE, str(ba.get('date'))): errors.append('brief_approval invalid')
    if r['validator_result'] != 'PASS': errors.append('validator_result must be PASS')
    cr = r['correction_rounds']
    if not isinstance(cr, int) or isinstance(cr, bool) or cr < 0: errors.append('correction_rounds invalid')
    da = r['discarded_attempts']
    if not isinstance(da, list) or any(not isinstance(d, dict) or set(d) != {'reason'} or not nonempty(d.get('reason')) for d in da): errors.append('discarded_attempts invalid')
    if not nonempty(r['isolation_method']) or ISOLATION_PHRASE not in r['isolation_method']: errors.append(f'isolation_method must state {ISOLATION_PHRASE}')
    d = r['drafter']
    if not isinstance(d, dict) or set(d) != {'kind', 'model_id', 'holds_ems_authority'} or d.get('kind') != 'AI agent' or not nonempty(d.get('model_id')) or d.get('holds_ems_authority') is not False: errors.append('drafter invalid')
    if r['statement'] != RECORD_STATEMENT: errors.append('statement does not equal the required statement')
    if V2.contains_absolute(r): errors.append('absolute path used in record')
    if errors: raise AuthorityError('; '.join(errors))

def rule_schema() -> dict:
    cond = {'type': 'object', 'additionalProperties': False, 'required': ['field', 'state'], 'properties': {'field': {'enum': list(V2.RULE_FIELDS)}, 'state': {'enum': list(V2.CONDITION_STATES)}}}
    return {'type': 'object', 'additionalProperties': False, 'required': ['combination', 'conditions'], 'properties': {'combination': {'const': V2.COMBINATION}, 'conditions': {'type': 'array', 'minItems': 1, 'maxItems': len(V2.RULE_FIELDS), 'items': cond}}}

def schema() -> dict:
    s = lambda: {'type': 'string', 'minLength': 1}
    proposal = {'type': 'object', 'additionalProperties': False, 'required': list(PROPOSAL_KEYS), 'properties': {
        'control_id': {'enum': list(CONTROL_IDS)},
        'proposed_outcome': {'enum': list(OUTCOMES)},
        'proposed_rule': {'anyOf': [rule_schema(), {'type': 'null'}]},
        'catalog_inputs': {'type': 'object', 'additionalProperties': False, 'required': list(CATALOG_INPUT_REQUIRED), 'properties': {**{k: s() for k in CATALOG_INPUT_REQUIRED}, 'inheritance_allowed': {'type': 'boolean'}, 'classification_status': s()}},
        'interpretation': {'type': 'object', 'additionalProperties': False, 'required': ['label', 'text'], 'properties': {'label': {'const': INTERPRETATION_LABEL}, 'text': s()}},
        'rationale': s(),
        'confidence': {'enum': list(CONFIDENCE)},
        'alternative_considered': {'anyOf': [{'type': 'null'}, {'type': 'object', 'additionalProperties': False, 'required': ['outcome', 'why'], 'properties': {'outcome': {'enum': list(OUTCOMES)}, 'why': s()}}]},
        'shape_limitation': {'anyOf': [{'type': 'null'}, {'type': 'object', 'additionalProperties': False, 'required': ['scope', 'note'], 'properties': {'scope': s(), 'note': s()}}]}},
        'allOf': [
            {'if': {'properties': {'proposed_outcome': {'const': 'PROPOSE_RULE'}}, 'required': ['proposed_outcome']}, 'then': {'properties': {'proposed_rule': rule_schema()}}},
            {'if': {'properties': {'proposed_outcome': {'const': 'PROPOSE_NO_RULE'}}, 'required': ['proposed_outcome']}, 'then': {'properties': {'proposed_rule': {'type': 'null'}}}}]}
    src = {'type': 'object', 'additionalProperties': False, 'required': ['relative_path', 'git_blob_id', 'sha256', 'entries_have_description', 'note'], 'properties': {'relative_path': {'const': CATALOG_REL}, 'git_blob_id': {'type': 'string', 'pattern': HEX40}, 'sha256': {'type': 'string', 'pattern': HEX64}, 'entries_have_description': {'const': False}, 'note': {'const': CATALOG_NOTE}}}
    return {'$schema': 'https://json-schema.org/draft/2020-12/schema', 'title': 'EMS Archive Assessment Not-Applicable Rule Proposals (draft, no authority)', 'type': 'object', 'additionalProperties': False,
        'required': HEADER_KEYS + ['proposals'],
        'properties': {'status': {'const': STATUS}, 'non_authority_statement': {'const': NON_AUTHORITY_STATEMENT}, 'drafting_frame': {'const': V2.semantics()}, 'catalog_source': src,
            'proposals': {'type': 'array', 'minItems': len(CONTROL_IDS), 'maxItems': len(CONTROL_IDS), 'items': proposal}}}

def record_schema() -> dict:
    s = lambda: {'type': 'string', 'minLength': 1}
    h40 = {'type': 'string', 'pattern': HEX40}; h64 = {'type': 'string', 'pattern': HEX64}; d = {'type': 'string', 'pattern': DATE_RE}
    return {'$schema': 'https://json-schema.org/draft/2020-12/schema', 'title': 'EMS Archive Assessment Rule Proposals Drafting Record', 'type': 'object', 'additionalProperties': False, 'required': list(RECORD_KEYS),
        'properties': {'status': {'const': RECORD_STATUS}, 'drafting_commit': h40, 'proposals_path': s(), 'proposals_sha256': h64, 'catalog_path': s(), 'catalog_sha256': h64, 'catalog_git_blob_id': h40, 'brief_path': s(), 'brief_sha256': h64, 'brief_commit': h40,
            'brief_approval': {'type': 'object', 'additionalProperties': False, 'required': list(APPROVAL_KEYS), 'properties': {'approver': s(), 'role': s(), 'date': d, 'scope': s()}},
            'validator_script': s(), 'validator_result': {'const': 'PASS'}, 'correction_rounds': {'type': 'integer', 'minimum': 0},
            'discarded_attempts': {'type': 'array', 'items': {'type': 'object', 'additionalProperties': False, 'required': ['reason'], 'properties': {'reason': s()}}},
            'drafted_on': d, 'isolation_method': {'type': 'string', 'pattern': ISOLATION_PHRASE},
            'drafter': {'type': 'object', 'additionalProperties': False, 'required': ['kind', 'model_id', 'holds_ems_authority'], 'properties': {'kind': {'const': 'AI agent'}, 'model_id': s(), 'holds_ems_authority': {'const': False}}},
            'statement': {'const': RECORD_STATEMENT}}}

def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument('--validate', action='store_true'); parser.add_argument('--validate-record', action='store_true'); parser.add_argument('--emit-schema', action='store_true'); args = parser.parse_args()
    if args.validate:
        if not PROPOSALS.exists(): raise AuthorityError('proposals file is not present')
        p = V2.load(PROPOSALS); validate_proposals(p); jsonschema.Draft202012Validator(V2.load(SCHEMA)).validate(p); print('PASS')
    elif args.validate_record:
        if not RECORD.exists(): raise AuthorityError('drafting record file is not present')
        r = V2.load(RECORD); validate_record(r); jsonschema.Draft202012Validator(V2.load(RECORD_SCHEMA)).validate(r); print('PASS')
    elif args.emit_schema: V2.dump(SCHEMA, schema()); V2.dump(RECORD_SCHEMA, record_schema())
    else: parser.error('one of --validate, --validate-record or --emit-schema is required')
if __name__ == '__main__': main()

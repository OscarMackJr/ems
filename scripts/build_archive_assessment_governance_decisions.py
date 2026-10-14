from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
from datetime import date
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

PROPOSALS = REGISTRY / 'archive_assessment_not_applicable_rule_proposals.json'
DRAFTING_RECORD = REGISTRY / 'archive_assessment_rule_proposals_drafting_record.json'
ANSWERS = REGISTRY / 'archive_assessment_governance_answers.json'
ANSWERS_SCHEMA = SCHEMAS / 'archive_assessment_governance_answers.schema.json'
DECISIONS = REGISTRY / 'archive_assessment_governance_decisions.json'
DECISIONS_SCHEMA = SCHEMAS / 'archive_assessment_governance_decisions.schema.json'
WORDING_APPROVAL = REGISTRY / 'archive_assessment_governance_wording_approval.json'
DRAFTING_COMMIT = 'dc3b41c9fbb3571a191d2da5164fb73439a0637b'
APPROVER = 'Oscar Mack'
APPROVER_ROLES = ['EMS_GOVERNANCE_AUTHORITY', 'HAYES_VERIFY_DEVELOPER']
DUAL_ROLE_STATEMENT = 'Oscar Mack made this decision as the EMS governance authority and is also the developer of Hayes Verify, the assessor that will read it.'
EARLIER_ASSESSMENT_STATEMENT = 'The deciding authority knew the per-control result of an earlier assessment when making these decisions. The drafts were written without that knowledge. No rule was compared with any target during this phase.'
TYPED_BY_AUTHORITY_STATEMENT = 'The dispositions, notes and any decided rule or rationale in the answers file were typed by Oscar Mack. No AI agent chose, suggested or reworded any of them.'
INTERPRETATION_BASIS = 'Accepted as the basis of this decision only. It is not a definition of the control.'
HEADER_STATEMENT_REF = 'earlier_assessment_knowledge_statement'
HEADER_REFRESH_KEYS = {'frozen_input_sha256_normalisation'}
DECIDED_STATES = ['RULE_PUBLISHED', 'NO_RULE_WILL_BE_PUBLISHED']
KINDS = ['PROPOSE_RULE', 'PROPOSE_NO_RULE']
DECISIONS_STATUS = 'GOVERNANCE_DECISIONS'
HEADER_KEYS = ['status', 'answers_typed_by_authority_statement', 'earlier_assessment_knowledge_statement', 'wording_approval', 'proposals_path', 'proposals_sha256', 'drafting_record_path', 'drafting_record_sha256', 'drafting_commit', 'answers_path', 'answers_sha256', 'answers_sha256_normalisation', 'frozen_input_sha256_normalisation', 'records']
APPROVAL_KEYS = ['approver', 'role', 'date', 'scope', 'source_path', 'statement_sha256']
STATEMENT_KEYS = ['answers_typed_by_authority_statement', 'dual_role_statement', 'earlier_assessment_knowledge_statement']
RECORD_KEYS = ['decision_id', 'control_id', 'disposition', 'decided_outcome', 'drafted', 'decided', 'interpretation', 'note', 'scope_note', 'approver', 'approver_roles', 'dual_role_statement', 'decided_on', 'drafting_commit', 'drafting_record_path', 'header_statement_ref', 'supersedes', 'amendment_present']
SIDE_KEYS = ['outcome', 'rule', 'rationale']
INTERPRETATION_KEYS = ['label', 'text', 'accepted_as_basis_of_this_decision_only', 'basis_statement']
SCOPE_NOTE_KEYS = ['drafted_note', 'ruling']
PROPOSALS_REL = 'registry/archive_assessment_not_applicable_rule_proposals.json'
DRAFTING_RECORD_REL = 'registry/archive_assessment_rule_proposals_drafting_record.json'
ANSWERS_REL = 'registry/archive_assessment_governance_answers.json'
APPROVAL_REL = 'registry/archive_assessment_governance_wording_approval.json'
SHA40_RE = r'^[0-9a-f]{40}$'
SHA64_RE = r'^[0-9a-f]{64}$'
VIEW = DOCS / 'ARCHIVE_ASSESSMENT_RULE_PROPOSALS_VIEW.md'
CONTROL_IDS = [f'EMS-CTRL-{n:03d}' for n in (9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22, 30, 33, 39, 42, 52, 62, 75, 79)]
SCOPE_NOTE_IDS = ['EMS-CTRL-022', 'EMS-CTRL-030', 'EMS-CTRL-042', 'EMS-CTRL-052', 'EMS-CTRL-062', 'EMS-CTRL-075']
DISPOSITIONS = ['APPROVED_AS_DRAFTED', 'CHANGED', 'REJECTED']
SCOPE_RULINGS = ['ACCEPTED_AS_TRUE_LIMITATION', 'NOT_ACCEPTED_AS_TRUE_LIMITATION']
ANSWER_KEYS = ['control_id', 'disposition', 'note', 'decided_rule', 'decided_rationale', 'scope_note_ruling', 'decided_on', 'supersedes']
TOP_KEYS = ['status', 'entries']
STATUS = 'GOVERNANCE_ANSWERS'
NOTE_MIN_CHARS = 20
DATE_RE = r'^[0-9]{4}-[0-9]{2}-[0-9]{2}$'
FIELD_ORDER = ['catalog_inputs', 'interpretation', 'proposed_outcome', 'proposed_rule', 'rationale', 'confidence', 'alternative_considered', 'shape_limitation']

def nonempty(v: object) -> bool: return isinstance(v, str) and bool(v.strip())

def norm(text: str) -> str: return ' '.join(text.casefold().split())

def norm_templated(text: str) -> str: return ' '.join(re.sub(r'ems-ctrl-[0-9]+|[0-9]+', '', norm(text)).split())

def is_date(v: object) -> bool:
    if not isinstance(v, str) or not re.match(DATE_RE, v): return False
    try: date.fromisoformat(v)
    except ValueError: return False
    return True

def drafted_strings(p: object) -> list:
    if isinstance(p, str): return [p]
    if isinstance(p, dict): return [s for v in p.values() for s in drafted_strings(v)]
    if isinstance(p, list): return [s for v in p for s in drafted_strings(v)]
    return []

def sentences_ok(r: object) -> bool: return nonempty(r) and 2 <= len(re.findall(r'[.!?](\s|$)', r.strip())) <= 4

def answers_digest(path: Path) -> str: return V2.lf_digest(path)

def load_checked(path: Path) -> object:
    try: return json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e: raise AuthorityError(f'{path.name}: invalid JSON at line {e.lineno} column {e.colno}: {e.msg}')

def pairs(rule: object) -> set:
    if not isinstance(rule, dict) or not isinstance(rule.get('conditions'), list): return set()
    return {(c.get('field'), c.get('state')) for c in rule['conditions'] if isinstance(c, dict) and isinstance(c.get('field'), str) and isinstance(c.get('state'), str)}

def render(value: object) -> str:
    if isinstance(value, str): return value
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False)

def view_text(proposals: dict) -> str:
    out = ['# Archive Assessment Rule Proposals View', '',
           'This view is derived from the frozen proposals file by scripts/build_archive_assessment_governance_decisions.py and is read-only.', '',
           '## Drafting frame', '', '```json', render(proposals['drafting_frame']), '```', '']
    for p in proposals['proposals']:
        out += [f"## {p['control_id']}", '']
        for k in FIELD_ORDER:
            v = p[k]
            out += [f'### {k}', '']
            if isinstance(v, str): out += [v, '']
            else: out += ['```json', 'null' if v is None else render(v), '```', '']
    return '\n'.join(out).rstrip('\n') + '\n'

def blank_entry(cid: str) -> dict:
    return {'control_id': cid, 'disposition': None, 'note': '', 'decided_rule': None, 'decided_rationale': None, 'scope_note_ruling': None, 'decided_on': '', 'supersedes': None}

def blank_answers() -> dict: return {'status': STATUS, 'entries': [blank_entry(c) for c in CONTROL_IDS]}

def validate_answers(a: object, proposals: dict, strict: bool = False) -> None:
    errors: list = []
    if not isinstance(a, dict): raise AuthorityError('answers document must be an object')
    if set(a) != set(TOP_KEYS): errors.append(f'top-level keys must be exactly {TOP_KEYS}')
    if a.get('status') != STATUS: errors.append('status invalid')
    entries = a.get('entries')
    if not isinstance(entries, list): raise AuthorityError('; '.join(errors + ['entries must be a list']))
    if len(entries) < len(CONTROL_IDS): errors.append('entries must hold at least the 21 control entries')
    first = entries[:len(CONTROL_IDS)]
    ids = [e.get('control_id') if isinstance(e, dict) else None for e in first]
    if ids != CONTROL_IDS: errors.append('the first 21 entries must be the 21 control ids once each in ascending order')
    for i, e in enumerate(entries):
        cid = e.get('control_id') if isinstance(e, dict) else None
        if not isinstance(e, dict) or set(e) != set(ANSWER_KEYS): errors.append(f'entry {i}: keys must be exactly {ANSWER_KEYS}'); continue
        if e['disposition'] is not None and e['disposition'] not in DISPOSITIONS: errors.append(f'{cid}: disposition not in {DISPOSITIONS}')
        if e['scope_note_ruling'] is not None and e['scope_note_ruling'] not in SCOPE_RULINGS: errors.append(f'{cid}: scope_note_ruling invalid')
        if not isinstance(e['note'], str) or not isinstance(e['decided_on'], str): errors.append(f'{cid}: note and decided_on must be strings')
        if e['decided_rationale'] is not None and not isinstance(e['decided_rationale'], str): errors.append(f'{cid}: decided_rationale must be null or a string')
        if i >= len(CONTROL_IDS) and (not isinstance(e['supersedes'], str) or not re.match(V2.AUTHORITY_ID_RE, e['supersedes'])): errors.append(f'entry {i}: entries beyond 21 need a supersedes reference')
        if e['supersedes'] is not None and (not isinstance(e['supersedes'], str) or not re.match(V2.AUTHORITY_ID_RE, e['supersedes'])): errors.append(f'{cid}: supersedes invalid')
        if not isinstance(cid, str) or cid not in CONTROL_IDS: errors.append(f'entry {i}: unknown control {cid!r}')
        if e['decided_rule'] is not None and not isinstance(e['decided_rule'], dict): errors.append(f'{cid}: decided_rule must be null or an object')
        if i < len(CONTROL_IDS):
            if e['supersedes'] is not None: errors.append(f'entry {i}: the first 21 entries cannot supersede')
        elif isinstance(e['supersedes'], str) and re.match(V2.AUTHORITY_ID_RE, e['supersedes']):
            pos = int(e['supersedes'][-3:])
            if not 1 <= pos <= i: errors.append(f'entry {i}: supersedes must name an earlier entry')
            elif not isinstance(entries[pos - 1], dict) or entries[pos - 1].get('control_id') != cid: errors.append(f'entry {i}: supersedes an entry for another control')
    if V2.contains_absolute(a): errors.append('absolute path used in answers')
    if strict and not errors: strict_checks(entries, proposals, errors)
    if errors: raise AuthorityError('; '.join(errors))

def strict_checks(entries: list, proposals: dict, errors: list) -> None:
    by_id = {p['control_id']: p for p in proposals['proposals']}
    seen: dict = {}
    for e in entries:
        cid = e['control_id']; p = by_id[cid]; d = e['disposition']
        if d is None: errors.append(f'{cid}: disposition is required'); continue
        n = e['note']
        if not nonempty(n): errors.append(f'{cid}: note is required')
        else:
            if len(n.strip()) < NOTE_MIN_CHARS: errors.append(f'{cid}: note shorter than {NOTE_MIN_CHARS} characters')
            if norm_templated(n) in {norm_templated(x) for x in drafted_strings(p)}: errors.append(f'{cid}: note repeats drafted text')
            if norm(n) in seen: errors.append(f'{cid}: note repeats the note of {seen[norm(n)]}')
            seen.setdefault(norm(n), cid)
        if not is_date(e['decided_on']): errors.append(f'{cid}: decided_on must be a date')
        ruling = e['scope_note_ruling']
        if cid in SCOPE_NOTE_IDS:
            if ruling is None: errors.append(f'{cid}: scope_note_ruling is required')
        elif ruling is not None: errors.append(f'{cid}: scope_note_ruling must be null')
        drafted_rule = p['proposed_outcome'] == 'PROPOSE_RULE'
        rule, rat = e['decided_rule'], e['decided_rationale']
        if rat is not None and not sentences_ok(rat): errors.append(f'{cid}: decided_rationale must be 2 to 4 sentences')
        if d == 'APPROVED_AS_DRAFTED':
            if rule is not None or rat is not None: errors.append(f'{cid}: APPROVED_AS_DRAFTED carries no decided_rule or decided_rationale')
        elif (d == 'CHANGED' and drafted_rule) or (d == 'REJECTED' and not drafted_rule):
            if d == 'CHANGED':
                if rule is None or not nonempty(rat): errors.append(f'{cid}: CHANGED needs decided_rule and decided_rationale'); continue
                V2.validate_rule(cid, rule, errors)
                if pairs(rule) == pairs(p['proposed_rule']) and norm(rat) == norm(p['rationale']): errors.append(f'{cid}: CHANGED shows no change from the draft')
            else:
                if rule is None or not nonempty(rat): errors.append(f'{cid}: REJECTED of a drafted no-rule needs decided_rule and decided_rationale'); continue
                V2.validate_rule(cid, rule, errors)
        else:
            if rule is not None or not nonempty(rat): errors.append(f'{cid}: {d} needs a null decided_rule and a decided_rationale'); continue
            if d == 'CHANGED' and norm(rat) == norm(p['rationale']): errors.append(f'{cid}: CHANGED shows no change from the draft')

def rule_schema() -> dict:
    cond = {'type': 'object', 'additionalProperties': False, 'required': ['field', 'state'], 'properties': {'field': {'enum': list(V2.RULE_FIELDS)}, 'state': {'enum': list(V2.CONDITION_STATES)}}}
    return {'type': 'object', 'additionalProperties': False, 'required': ['combination', 'conditions'], 'properties': {'combination': {'const': V2.COMBINATION}, 'conditions': {'type': 'array', 'minItems': 1, 'maxItems': len(V2.RULE_FIELDS), 'items': cond}}}

def answers_schema() -> dict:
    entry = {'type': 'object', 'additionalProperties': False, 'required': list(ANSWER_KEYS), 'properties': {
        'control_id': {'enum': list(CONTROL_IDS)},
        'disposition': {'enum': DISPOSITIONS + [None]},
        'note': {'type': 'string'},
        'decided_rule': {'anyOf': [{'type': 'null'}, rule_schema()]},
        'decided_rationale': {'anyOf': [{'type': 'null'}, {'type': 'string', 'minLength': 1}]},
        'scope_note_ruling': {'enum': SCOPE_RULINGS + [None]},
        'decided_on': {'type': 'string', 'pattern': r'^([0-9]{4}-[0-9]{2}-[0-9]{2})?$'},
        'supersedes': {'anyOf': [{'type': 'null'}, {'type': 'string', 'pattern': V2.AUTHORITY_ID_RE}]}}}
    return {'$schema': 'https://json-schema.org/draft/2020-12/schema', 'title': 'EMS Archive Assessment Governance Answers', 'type': 'object', 'additionalProperties': False, 'required': list(TOP_KEYS),
        'properties': {'status': {'const': STATUS}, 'entries': {'type': 'array', 'minItems': len(CONTROL_IDS), 'items': entry}}}

def sha_text(text: str) -> str: return hashlib.sha256(text.encode('utf-8')).hexdigest()

def kind_of(rule: object) -> str: return 'PROPOSE_RULE' if rule is not None else 'PROPOSE_NO_RULE'

def build_decisions(proposals: dict, answers: dict, drafting_record: dict, wording_approval: dict, answers_sha256: str, drafting_record_sha256: str | None = None) -> dict:
    validate_answers(answers, proposals, strict=True)
    for e in answers['entries']:
        if e['disposition'] == 'APPROVED_AS_DRAFTED' and (e['decided_rule'] is not None or e['decided_rationale'] is not None): raise AuthorityError(f"{e['control_id']}: APPROVED_AS_DRAFTED carries no decided_rule or decided_rationale")
        if e['scope_note_ruling'] is not None and e['control_id'] not in SCOPE_NOTE_IDS: raise AuthorityError(f"{e['control_id']}: scope_note_ruling on a control without a scope note")
    by_id = {p['control_id']: p for p in proposals['proposals']}
    ap = wording_approval['approval']
    records = []
    for i, e in enumerate(answers['entries']):
        cid = e['control_id']; p = by_id[cid]; d = e['disposition']
        drafted = {'outcome': p['proposed_outcome'], 'rule': p['proposed_rule'], 'rationale': p['rationale']}
        if d == 'APPROVED_AS_DRAFTED': decided = {'outcome': drafted['outcome'], 'rule': drafted['rule'], 'rationale': drafted['rationale']}
        else: decided = {'outcome': kind_of(e['decided_rule']), 'rule': e['decided_rule'], 'rationale': e['decided_rationale']}
        scope_note = {'drafted_note': p['shape_limitation'], 'ruling': e['scope_note_ruling']} if cid in SCOPE_NOTE_IDS else None
        records.append({'decision_id': f'AA4-GOV-{i + 1:03d}', 'control_id': cid, 'disposition': d,
            'decided_outcome': 'RULE_PUBLISHED' if decided['rule'] is not None else 'NO_RULE_WILL_BE_PUBLISHED',
            'drafted': drafted, 'decided': decided,
            'interpretation': {'label': p['interpretation']['label'], 'text': p['interpretation']['text'], 'accepted_as_basis_of_this_decision_only': True, 'basis_statement': INTERPRETATION_BASIS},
            'note': e['note'], 'scope_note': scope_note, 'approver': APPROVER, 'approver_roles': list(APPROVER_ROLES), 'dual_role_statement': DUAL_ROLE_STATEMENT,
            'decided_on': e['decided_on'], 'drafting_commit': drafting_record['drafting_commit'], 'drafting_record_path': DRAFTING_RECORD_REL,
            'header_statement_ref': HEADER_STATEMENT_REF, 'supersedes': e['supersedes'], 'amendment_present': drafted != decided})
    return {'status': DECISIONS_STATUS, 'answers_typed_by_authority_statement': TYPED_BY_AUTHORITY_STATEMENT, 'earlier_assessment_knowledge_statement': EARLIER_ASSESSMENT_STATEMENT,
        'wording_approval': {'approver': ap['approver'], 'role': ap['role'], 'date': ap['date'], 'scope': ap['scope'], 'source_path': APPROVAL_REL, 'statement_sha256': dict(wording_approval['statement_sha256'])},
        'proposals_path': PROPOSALS_REL, 'proposals_sha256': drafting_record['proposals_sha256'], 'drafting_record_path': DRAFTING_RECORD_REL,
        'drafting_record_sha256': drafting_record_sha256 if drafting_record_sha256 is not None else V2.lf_digest(DRAFTING_RECORD),
        'drafting_commit': drafting_record['drafting_commit'], 'answers_path': ANSWERS_REL, 'answers_sha256': answers_sha256, 'answers_sha256_normalisation': 'CRLF_TO_LF', 'frozen_input_sha256_normalisation': 'CRLF_TO_LF', 'records': records}

def validate_decisions(d: object, proposals: dict | None = None, drafting_record: dict | None = None, wording_approval: dict | None = None) -> None:
    errors: list = []
    if not isinstance(d, dict): raise AuthorityError('decisions document must be an object')
    proposals = proposals if proposals is not None else V2.load(PROPOSALS)
    drafting_record = drafting_record if drafting_record is not None else V2.load(DRAFTING_RECORD)
    by_id = {p['control_id']: p for p in proposals['proposals']}
    if set(d) != set(HEADER_KEYS): errors.append(f'header keys must be exactly {HEADER_KEYS}')
    if d.get('status') != DECISIONS_STATUS: errors.append('status invalid')
    if d.get('answers_typed_by_authority_statement') != TYPED_BY_AUTHORITY_STATEMENT: errors.append('answers_typed_by_authority_statement differs from the approved text')
    if d.get('earlier_assessment_knowledge_statement') != EARLIER_ASSESSMENT_STATEMENT: errors.append('earlier_assessment_knowledge_statement differs from the approved text')
    wa = d.get('wording_approval')
    if not isinstance(wa, dict) or set(wa) != set(APPROVAL_KEYS): errors.append(f'wording_approval keys must be exactly {APPROVAL_KEYS}')
    else:
        if wa['approver'] != APPROVER: errors.append('wording_approval approver invalid')
        approval_doc = wording_approval if wording_approval is not None else V2.load(WORDING_APPROVAL)
        ap = approval_doc['approval']
        if wa != {'approver': ap['approver'], 'role': ap['role'], 'date': ap['date'], 'scope': ap['scope'], 'source_path': APPROVAL_REL, 'statement_sha256': dict(approval_doc['statement_sha256'])}: errors.append('wording_approval differs from the wording approval file')
        expected = {'answers_typed_by_authority_statement': sha_text(TYPED_BY_AUTHORITY_STATEMENT), 'dual_role_statement': sha_text(DUAL_ROLE_STATEMENT), 'earlier_assessment_knowledge_statement': sha_text(EARLIER_ASSESSMENT_STATEMENT)}
        if wa['statement_sha256'] != expected: errors.append('wording_approval statement_sha256 does not match the approved statements')
    for k, live in (('proposals_sha256', V2.lf_digest(PROPOSALS)), ('drafting_record_sha256', V2.lf_digest(DRAFTING_RECORD))):
        if not isinstance(d.get(k), str) or not re.match(SHA64_RE, d[k]): errors.append(f'{k} must be 64 hex characters')
        elif d[k] != live: errors.append(f'{k} does not match the live file')
    if not isinstance(d.get('answers_sha256'), str) or not re.match(SHA64_RE, d['answers_sha256']): errors.append('answers_sha256 must be 64 hex characters')
    elif not ANSWERS.exists() or d['answers_sha256'] != answers_digest(ANSWERS): errors.append('answers_sha256 does not match the live answers file')
    if d.get('answers_sha256_normalisation') != 'CRLF_TO_LF': errors.append('answers_sha256_normalisation invalid')
    if d.get('frozen_input_sha256_normalisation') != 'CRLF_TO_LF': errors.append('frozen_input_sha256_normalisation invalid')
    if d.get('drafting_commit') != DRAFTING_COMMIT or drafting_record.get('drafting_commit') != DRAFTING_COMMIT or not re.match(SHA40_RE, str(d.get('drafting_commit'))): errors.append('drafting_commit invalid')
    for k, v in (('proposals_path', PROPOSALS_REL), ('drafting_record_path', DRAFTING_RECORD_REL), ('answers_path', ANSWERS_REL)):
        if d.get(k) != v: errors.append(f'{k} invalid')
    records = d.get('records')
    if not isinstance(records, list): raise AuthorityError('; '.join(errors + ['records must be a list']))
    if len(records) < len(CONTROL_IDS): errors.append('records must hold at least the 21 control records')
    if [r.get('control_id') if isinstance(r, dict) else None for r in records[:len(CONTROL_IDS)]] != CONTROL_IDS: errors.append('the first 21 records must be the 21 control ids once each in ascending order')
    index: dict = {}
    superseded: set = set()
    for i, r in enumerate(records):
        if not isinstance(r, dict) or set(r) != set(RECORD_KEYS): errors.append(f'record {i}: keys must be exactly {RECORD_KEYS}'); continue
        rid, cid = r['decision_id'], r['control_id']
        if not isinstance(cid, str): errors.append(f'record {i}: control_id invalid'); continue
        if not isinstance(rid, str) or not re.match(V2.AUTHORITY_ID_RE, rid): errors.append(f'record {i}: decision_id invalid'); continue
        if rid in index: errors.append(f'{rid}: duplicate decision_id')
        if rid != f'AA4-GOV-{i + 1:03d}': errors.append(f'{rid}: decision_id must be AA4-GOV-{i + 1:03d} by position')
        index[rid] = (i, cid)
        if cid not in by_id: errors.append(f'{rid}: unknown control {cid}'); continue
        p = by_id[cid]; disp = r['disposition']
        if disp not in DISPOSITIONS: errors.append(f'{rid}: disposition invalid'); continue
        if r['approver'] != APPROVER: errors.append(f'{rid}: approver invalid')
        if r['approver_roles'] != APPROVER_ROLES: errors.append(f'{rid}: approver_roles invalid')
        if r['dual_role_statement'] != DUAL_ROLE_STATEMENT: errors.append(f'{rid}: dual_role_statement differs from the approved text')
        if r['header_statement_ref'] != HEADER_STATEMENT_REF: errors.append(f'{rid}: header_statement_ref invalid')
        if r['drafting_commit'] != DRAFTING_COMMIT: errors.append(f'{rid}: drafting_commit invalid')
        if r['drafting_record_path'] != DRAFTING_RECORD_REL: errors.append(f'{rid}: drafting_record_path invalid')
        if not isinstance(r['note'], str): errors.append(f'{rid}: note must be a string'); continue
        if not nonempty(r['note']): errors.append(f'{rid}: note is required')
        if not is_date(r['decided_on']): errors.append(f'{rid}: decided_on must be a date')
        dr, de = r['drafted'], r['decided']
        if not all(isinstance(x, dict) and set(x) == set(SIDE_KEYS) for x in (dr, de)): errors.append(f'{rid}: drafted and decided need exactly {SIDE_KEYS}'); continue
        if not all(isinstance(x['rationale'], str) for x in (dr, de)): errors.append(f'{rid}: drafted and decided rationale must be strings'); continue
        if dr != {'outcome': p['proposed_outcome'], 'rule': p['proposed_rule'], 'rationale': p['rationale']}: errors.append(f'{rid}: drafted text differs from the live proposal')
        if de['outcome'] != kind_of(de['rule']): errors.append(f'{rid}: decided outcome does not match decided rule')
        if r['decided_outcome'] not in DECIDED_STATES: errors.append(f'{rid}: decided_outcome must be one of {DECIDED_STATES}')
        elif r['decided_outcome'] != ('RULE_PUBLISHED' if de['rule'] is not None else 'NO_RULE_WILL_BE_PUBLISHED'): errors.append(f'{rid}: decided_outcome does not match decided rule')
        if de['rule'] is not None: V2.validate_rule(cid, de['rule'], errors)
        if r['amendment_present'] is not (dr != de): errors.append(f'{rid}: amendment_present invalid')
        if disp == 'APPROVED_AS_DRAFTED':
            if de != dr: errors.append(f'{rid}: APPROVED_AS_DRAFTED needs decided equal to drafted')
        else:
            if not nonempty(de['rationale']): errors.append(f'{rid}: {disp} needs a decided rationale')
            elif not sentences_ok(de['rationale']): errors.append(f'{rid}: decided rationale must be 2 to 4 sentences')
            if disp == 'CHANGED':
                if de['outcome'] != dr['outcome']: errors.append(f'{rid}: CHANGED keeps the drafted kind')
                elif pairs(de['rule']) == pairs(dr['rule']) and norm(de['rationale'] or '') == norm(dr['rationale']): errors.append(f'{rid}: CHANGED shows no change from the draft')
            elif de['outcome'] == dr['outcome']: errors.append(f'{rid}: REJECTED flips the drafted kind')
        if r['interpretation'] != {'label': p['interpretation']['label'], 'text': p['interpretation']['text'], 'accepted_as_basis_of_this_decision_only': True, 'basis_statement': INTERPRETATION_BASIS}: errors.append(f'{rid}: interpretation invalid')
        sn = r['scope_note']
        if cid in SCOPE_NOTE_IDS:
            if not isinstance(sn, dict) or set(sn) != set(SCOPE_NOTE_KEYS) or sn['ruling'] not in SCOPE_RULINGS or sn['drafted_note'] != p['shape_limitation']: errors.append(f'{rid}: scope_note invalid')
        elif sn is not None: errors.append(f'{rid}: scope_note must be null')
        sup = r['supersedes']
        if sup is not None and not isinstance(sup, str): errors.append(f'{rid}: supersedes must be null or a string')
        elif sup is not None:
            if sup == rid: errors.append(f'{rid}: supersedes itself')
            elif sup not in index: errors.append(f'{rid}: supersedes an id that is not an earlier record')
            elif index[sup][1] != cid: errors.append(f'{rid}: supersedes a record for another control')
            else: superseded.add(sup)
    counts: dict = {}
    for rid, (i, cid) in index.items():
        if rid not in superseded: counts[cid] = counts.get(cid, 0) + 1
    for cid in CONTROL_IDS:
        if counts.get(cid, 0) != 1: errors.append(f'{cid}: needs exactly one unsuperseded record')
    if V2.contains_absolute(d): errors.append('absolute path used in decisions')
    if errors: raise AuthorityError('; '.join(errors))

def decisions_schema() -> dict:
    nullable_rule = {'anyOf': [{'type': 'null'}, rule_schema()]}
    side = {'type': 'object', 'additionalProperties': False, 'required': list(SIDE_KEYS), 'properties': {'outcome': {'enum': KINDS}, 'rule': nullable_rule, 'rationale': {'type': 'string', 'minLength': 1}}}
    interp = {'type': 'object', 'additionalProperties': False, 'required': list(INTERPRETATION_KEYS), 'properties': {'label': {'type': 'string', 'minLength': 1}, 'text': {'type': 'string', 'minLength': 1}, 'accepted_as_basis_of_this_decision_only': {'const': True}, 'basis_statement': {'const': INTERPRETATION_BASIS}}}
    scope = {'anyOf': [{'type': 'null'}, {'type': 'object', 'additionalProperties': False, 'required': list(SCOPE_NOTE_KEYS), 'properties': {'drafted_note': {'type': 'object', 'additionalProperties': False, 'required': ['scope', 'note'], 'properties': {'scope': {'type': 'string', 'minLength': 1}, 'note': {'type': 'string', 'minLength': 1}}}, 'ruling': {'enum': SCOPE_RULINGS}}}]}
    record = {'type': 'object', 'additionalProperties': False, 'required': list(RECORD_KEYS), 'properties': {
        'decision_id': {'type': 'string', 'pattern': V2.AUTHORITY_ID_RE}, 'control_id': {'enum': list(CONTROL_IDS)}, 'disposition': {'enum': list(DISPOSITIONS)},
        'decided_outcome': {'enum': list(DECIDED_STATES)}, 'drafted': side, 'decided': side,
        'interpretation': interp, 'note': {'type': 'string', 'minLength': 1}, 'scope_note': scope, 'approver': {'const': APPROVER},
        'approver_roles': {'const': list(APPROVER_ROLES)}, 'dual_role_statement': {'const': DUAL_ROLE_STATEMENT},
        'decided_on': {'type': 'string', 'pattern': DATE_RE}, 'drafting_commit': {'const': DRAFTING_COMMIT}, 'drafting_record_path': {'const': DRAFTING_RECORD_REL},
        'header_statement_ref': {'const': HEADER_STATEMENT_REF}, 'supersedes': {'anyOf': [{'type': 'null'}, {'type': 'string', 'pattern': V2.AUTHORITY_ID_RE}]}, 'amendment_present': {'type': 'boolean'}}}
    sha = {'type': 'string', 'pattern': SHA64_RE}
    approval = {'type': 'object', 'additionalProperties': False, 'required': list(APPROVAL_KEYS), 'properties': {'approver': {'const': APPROVER}, 'role': {'type': 'string', 'minLength': 1}, 'date': {'type': 'string', 'pattern': DATE_RE}, 'scope': {'type': 'string', 'minLength': 1}, 'source_path': {'const': APPROVAL_REL},
        'statement_sha256': {'type': 'object', 'additionalProperties': False, 'required': list(STATEMENT_KEYS), 'properties': {k: sha for k in STATEMENT_KEYS}}}}
    return {'$schema': 'https://json-schema.org/draft/2020-12/schema', 'title': 'EMS Archive Assessment Governance Decisions', 'type': 'object', 'additionalProperties': False, 'required': list(HEADER_KEYS), 'properties': {
        'status': {'const': DECISIONS_STATUS}, 'answers_typed_by_authority_statement': {'const': TYPED_BY_AUTHORITY_STATEMENT}, 'earlier_assessment_knowledge_statement': {'const': EARLIER_ASSESSMENT_STATEMENT},
        'wording_approval': approval, 'proposals_path': {'const': PROPOSALS_REL}, 'proposals_sha256': sha, 'drafting_record_path': {'const': DRAFTING_RECORD_REL}, 'drafting_record_sha256': sha,
        'drafting_commit': {'const': DRAFTING_COMMIT}, 'answers_path': {'const': ANSWERS_REL}, 'answers_sha256': sha, 'answers_sha256_normalisation': {'const': 'CRLF_TO_LF'}, 'frozen_input_sha256_normalisation': {'const': 'CRLF_TO_LF'},
        'records': {'type': 'array', 'minItems': len(CONTROL_IDS), 'items': record}}}

def decisions_text(value: dict) -> str: return json.dumps(value, indent=2, sort_keys=True) + '\n'

def refreshable(existing: object, rebuilt: dict) -> bool:
    if not isinstance(existing, dict) or not isinstance(existing.get('records'), list): return False
    n = len(existing['records'])
    if n > len(rebuilt['records']) or existing['records'] != rebuilt['records'][:n]: return False
    keep = lambda x: {k: v for k, v in x.items() if k not in HEADER_REFRESH_KEYS}
    skip = ('records', 'answers_sha256')
    return {k: v for k, v in keep(existing).items() if k not in skip} == {k: v for k, v in keep(rebuilt).items() if k not in skip}

def build_from_files() -> dict:
    if not ANSWERS.exists(): raise AuthorityError('answers file is not present')
    answers = load_checked(ANSWERS)
    try: jsonschema.Draft202012Validator(answers_schema()).validate(answers)
    except jsonschema.ValidationError as e: raise AuthorityError(f'answers file fails the answers schema: {e.message}')
    return build_decisions(V2.load(PROPOSALS), answers, V2.load(DRAFTING_RECORD), V2.load(WORDING_APPROVAL), answers_digest(ANSWERS))

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--view', action='store_true'); parser.add_argument('--emit-template', action='store_true'); parser.add_argument('--emit-schema', action='store_true')
    parser.add_argument('--validate-answers', action='store_true'); parser.add_argument('--lenient', action='store_true')
    parser.add_argument('--build', action='store_true'); parser.add_argument('--validate', action='store_true')
    args = parser.parse_args()
    if args.view:
        with open(VIEW, 'w', encoding='utf-8', newline='\n') as f: f.write(view_text(V2.load(PROPOSALS)))
    elif args.emit_template:
        if ANSWERS.exists(): raise AuthorityError('answers file already exists and is not overwritten')
        V2.dump(ANSWERS, blank_answers())
    elif args.emit_schema: V2.dump(ANSWERS_SCHEMA, answers_schema()); V2.dump(DECISIONS_SCHEMA, decisions_schema())
    elif args.build:
        doc = build_from_files(); validate_decisions(doc)
        if not DECISIONS.exists(): V2.dump(DECISIONS, doc)
        else:
            raw = DECISIONS.read_bytes()
            if V2.lf_bytes(raw) != decisions_text(doc).encode('utf-8'):
                if not refreshable(load_checked(DECISIONS), doc): raise AuthorityError('decisions file already exists with different content and is not overwritten')
                V2.dump(DECISIONS, doc)
            elif raw != V2.lf_bytes(raw): V2.dump(DECISIONS, doc)
        print('PASS')
    elif args.validate:
        if not DECISIONS.exists(): raise AuthorityError('decisions file is not present')
        doc = load_checked(DECISIONS); validate_decisions(doc)
        if V2.lf_bytes(DECISIONS.read_bytes()).decode('utf-8') != decisions_text(build_from_files()): raise AuthorityError('decisions file differs from a rebuild')
        jsonschema.Draft202012Validator(V2.load(DECISIONS_SCHEMA)).validate(doc); print('PASS')
    elif args.validate_answers:
        if not ANSWERS.exists(): raise AuthorityError('answers file is not present')
        a = load_checked(ANSWERS); validate_answers(a, V2.load(PROPOSALS), strict=not args.lenient)
        jsonschema.Draft202012Validator(V2.load(ANSWERS_SCHEMA)).validate(a); print('PASS')
    else: parser.error('one of --view, --emit-template, --emit-schema, --validate-answers, --build or --validate is required')
if __name__ == '__main__': main()

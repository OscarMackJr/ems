from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
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

def sentences_ok(r: object) -> bool: return nonempty(r) and 2 <= len(re.findall(r'[.!?](\s|$)', r.strip())) <= 4

def answers_digest(path: Path) -> str: return hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest()

def load_checked(path: Path) -> object:
    try: return json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e: raise AuthorityError(f'{path.name}: invalid JSON at line {e.lineno} column {e.colno}: {e.msg}')

def pairs(rule: object) -> set:
    if not isinstance(rule, dict) or not isinstance(rule.get('conditions'), list): return set()
    return {(c.get('field'), c.get('state')) for c in rule['conditions'] if isinstance(c, dict)}

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
    if V2.contains_absolute(a): errors.append('absolute path used in answers')
    if strict and not errors: strict_checks(first, proposals, errors)
    if errors: raise AuthorityError('; '.join(errors))

def strict_checks(first: list, proposals: dict, errors: list) -> None:
    by_id = {p['control_id']: p for p in proposals['proposals']}
    seen: dict = {}
    for e in first:
        cid = e['control_id']; p = by_id[cid]; d = e['disposition']
        if d is None: errors.append(f'{cid}: disposition is required'); continue
        n = e['note']
        if not nonempty(n): errors.append(f'{cid}: note is required')
        else:
            if len(n.strip()) < NOTE_MIN_CHARS: errors.append(f'{cid}: note shorter than {NOTE_MIN_CHARS} characters')
            if norm(n) in (norm(p['rationale']), norm(p['interpretation']['text'])): errors.append(f'{cid}: note repeats drafted text')
            if norm(n) in seen: errors.append(f'{cid}: note repeats the note of {seen[norm(n)]}')
            seen.setdefault(norm(n), cid)
        if not isinstance(e['decided_on'], str) or not re.match(DATE_RE, e['decided_on']): errors.append(f'{cid}: decided_on must be a date')
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

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--view', action='store_true'); parser.add_argument('--emit-template', action='store_true'); parser.add_argument('--emit-schema', action='store_true')
    parser.add_argument('--validate-answers', action='store_true'); parser.add_argument('--lenient', action='store_true')
    args = parser.parse_args()
    if args.view:
        with open(VIEW, 'w', encoding='utf-8', newline='\n') as f: f.write(view_text(V2.load(PROPOSALS)))
    elif args.emit_template:
        if ANSWERS.exists(): raise AuthorityError('answers file already exists and is not overwritten')
        V2.dump(ANSWERS, blank_answers())
    elif args.emit_schema: V2.dump(ANSWERS_SCHEMA, answers_schema())
    elif args.validate_answers:
        if not ANSWERS.exists(): raise AuthorityError('answers file is not present')
        a = load_checked(ANSWERS); validate_answers(a, V2.load(PROPOSALS), strict=not args.lenient)
        jsonschema.Draft202012Validator(V2.load(ANSWERS_SCHEMA)).validate(a); print('PASS')
    else: parser.error('one of --view, --emit-template, --emit-schema or --validate-answers is required')
if __name__ == '__main__': main()

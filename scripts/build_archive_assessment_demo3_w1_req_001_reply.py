from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from datetime import date
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / 'registry'
SCHEMAS = ROOT / 'schemas'

# Frozen copies of the 2.0.1 publisher values at REPLY_PUBLICATION_COMMIT (31addfa); a test proves each one against that blob.
AUTHORITY = REGISTRY / 'archive_assessment_applicability_authority_v2.json'
SCHEMA = SCHEMAS / 'archive_assessment_applicability_authority_v2.schema.json'
GOVERNANCE_DECISIONS = REGISTRY / 'archive_assessment_governance_decisions.json'
GOVERNANCE_DECISIONS_REL = 'registry/archive_assessment_governance_decisions.json'
REQUEST_CONTROL_IDS = [f'EMS-CTRL-{n:03d}' for n in (9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22, 30, 33, 39, 42, 52, 62, 75, 79)]
DECISIONS = [f'AA1-GOV-{n:03d}' for n in range(1, 9)]
DECISION_STATES = ['RULE_PUBLISHED','NO_RULE_WILL_BE_PUBLISHED','NOT_YET_DECIDED']
VERSION = '2.0.1'
AUTHORITY_ID = 'EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-' + VERSION
OUT = ROOT / 'generated' / 'archive-assessment' / 'ems-aa3-v2'
SIGNOFF = REGISTRY / 'archive_assessment_applicability_authority_v2_signoff.json'
PUBLICATION_RECORD = REGISTRY / 'archive_assessment_applicability_authority_v2_publication_record.json'
APPROVER = 'Oscar Mack'
APPROVER_ROLES = ['EMS_GOVERNANCE_AUTHORITY', 'HAYES_VERIFY_DEVELOPER']
SIGNOFF_ROLE = 'EMS_GOVERNANCE_AUTHORITY'
DUAL_ROLE_STATEMENT = 'Oscar Mack made this decision as the EMS governance authority and is also the developer of Hayes Verify, the assessor that will read it.'
N_TRACE = 'archive_assessment_applicability_authority_v2_decision_traceability.json'
N_MANIFEST = 'ems_aa3_v2_archive_applicability_authority_publication_manifest.json'

REPLY_JSON = ROOT / 'registry' / 'archive_assessment_demo3_w1_req_001_reply.json'
REPLY_MD = ROOT / 'docs' / 'DEMO3_W1_REQ_001_REPLY.md'
REPLY_SCHEMA = ROOT / 'schemas' / 'archive_assessment_demo3_w1_req_001_reply.schema.json'
REPLY_SCHEMA_REL = 'schemas/archive_assessment_demo3_w1_req_001_reply.schema.json'
REPLY_PUBLICATION_COMMIT = '31addfa95ffc5c2d6805c73fa1f34d6ccbe313eb'
REPLY_RECORD_COMMIT = '4d9b7c1f41df5fa7575d4653a7d54ff9cf0a192b'
REPLY_SCHEMA_COMMIT = '7debe4aa544b425f2b80306a8510bfe74e568bae'
REQUEST_ID = 'DEMO3-W1-REQ-001'
REQUEST_LABEL = 'EMSREQ-APPLIC-RULES'
DOCUMENT_ID = 'EMS-DEMO3-W1-REQ-001-REPLY'
SCRIPT_REL = 'scripts/build_archive_assessment_demo3_w1_req_001_reply.py'
REMOTE_BRANCH = 'feature/ems-aa3-archive-applicability-authority'
PER_CONTROL_FIELDS = ['not_applicable_decision_state', 'not_applicable_rule', 'not_applicable_authority']
DECIDED_STATES = ['RULE_PUBLISHED', 'NO_RULE_WILL_BE_PUBLISHED']
REPLY_KEYS = ['document_id', 'request_id', 'request_label', 'reply_date', 'from_authority', 'dual_role_statement', 'pin', 'published_shape', 'controls', 'not_yet_decided', 'hayes_side_changes_needed', 'classification_prerequisites_gap_untouched', 'live_resolved_count_stays_zero', 'history_note', 'send_condition']
PIN_KEYS = ['publication_commit', 'authority_id', 'version', 'authority_sha256', 'manifest_sha256', 'digest_normalisation', 'publication_record_commit']
DIGEST_RE = r'^[0-9a-f]{64}$'
ENFORCED_GATES = ['The sign-off approver role must be EMS_GOVERNANCE_AUTHORITY; the Hayes Verify developer role is rejected.', 'The governance decisions are validated against their schema and invariants.', 'The certification results are computed from the checks that run, not recorded as constants.', 'The authority schema is stricter: it rejects unknown fields in a rule, a condition and the source lineage, and a field repeated within one rule; an extra field on a decided control row is rejected by the Python validator.']
FORBIDDEN_WORDS = ('best', 'critical', 'important', 'recommended', 'highest')


class AuthorityError(ValueError): pass
class GitHistoryError(AuthorityError): pass

def lf_bytes(b: bytes) -> bytes: return b.replace(b'\r\n', b'\n')
def load(p: Path) -> dict: return json.loads(p.read_text(encoding='utf-8'))
def contains_absolute(value: object) -> bool:
    if isinstance(value, str): return value.startswith(('/', '\\\\')) or (len(value) > 2 and value[1] == ':' and value[2] in '\\/')
    if isinstance(value, dict): return any(contains_absolute(v) for v in value.values())
    if isinstance(value, list): return any(contains_absolute(v) for v in value)
    return False
def bad_rel(p: object) -> bool: return not isinstance(p, str) or not p or contains_absolute(p) or p.startswith('\\') or re.match(r'[A-Za-z]:', p) is not None or '..' in p.replace('\\', '/').split('/')
def git_show(commit: str, relative_path: str) -> bytes:
    if not isinstance(commit, str) or not re.fullmatch(r'[0-9a-f]{40}', commit): raise AuthorityError(f'{relative_path}: commit must be a 40-character lowercase hex SHA')
    if bad_rel(relative_path): raise AuthorityError(f'{relative_path}: path must be repo-relative without ..')
    try: r = subprocess.run(['git', 'show', f'{commit}:{relative_path}'], cwd=ROOT, capture_output=True)
    except OSError as e: raise GitHistoryError(f'{relative_path}@{commit}: git unavailable: {e}; fetch full history (git fetch --unshallow)') from e
    if r.returncode != 0: raise GitHistoryError(f'{relative_path}@{commit}: git show failed: {r.stderr.decode("utf-8", "replace").strip()}; fetch full history (git fetch --unshallow)')
    return r.stdout
def jtext(value: object) -> str: return json.dumps(value, indent=2, sort_keys=True) + '\n'
def rel(p: Path) -> str: return p.relative_to(ROOT).as_posix()

def latest_records(doc: dict) -> list[dict]:
    recs = doc.get('records', [])
    superseded = set()
    for r in recs:
        sup = r.get('supersedes')
        if isinstance(sup, str): superseded.add(sup)
        elif isinstance(sup, list): superseded.update(x for x in sup if isinstance(x, str))
    return [r for r in recs if r.get('decision_id') not in superseded]

def is_date(value: object) -> bool:
    if not isinstance(value, str) or not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', value): return False
    try: date.fromisoformat(value)
    except ValueError: return False
    return True

def validate_signoff(record: object, authority_lf_digest: str) -> None:
    errors = []
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
    if 'authority_id' in record and record['authority_id'] != AUTHORITY_ID: errors.append('sign-off authority_id does not match')
    if 'version' in record and record['version'] != VERSION: errors.append('sign-off version does not match')
    if 'authority_sha256' in record and record['authority_sha256'] != authority_lf_digest: errors.append('sign-off authority_sha256 does not match the rebuilt authority')
    if 'authority_sha256_normalisation' in record and record['authority_sha256_normalisation'] != 'CRLF_TO_LF': errors.append('sign-off authority_sha256_normalisation must be CRLF_TO_LF')
    if errors: raise AuthorityError('; '.join(errors))

def rule_text(rule: dict) -> str:
    return f"{rule['combination']}: " + ' AND '.join(f"{c['field']} = {c['state']}" for c in rule['conditions'])


def pinned_bytes(commit: str, path: Path) -> bytes:
    return git_show(commit, rel(path))


def pinned_json(commit: str, path: Path) -> dict:
    return json.loads(pinned_bytes(commit, path).decode('utf-8'))


def pinned_digest(commit: str, path: Path) -> str:
    return hashlib.sha256(lf_bytes(pinned_bytes(commit, path))).hexdigest()


def first_sentence(text: str) -> str:
    s = re.split(r'(?<=\.)\s+(?=[A-Z])', text, maxsplit=1)[0]
    if not s or '\n' in s or '\r' in s or not s.endswith('.') or re.search(r'\b(e\.g|i\.e|etc|vs)\.$', s):
        raise AuthorityError('rationale first sentence cannot be cut deterministically')
    return s


def build_reply(authority: dict, record: dict, signoff: dict, decisions: dict) -> dict:
    rows = {r['control_id']: r for r in authority['controls']}
    latest = {r['control_id']: r for r in latest_records(decisions)}
    decided_rows = [r for r in authority['controls'] if r['not_applicable_decision_state'] != 'NOT_YET_DECIDED']
    if sorted(r['control_id'] for r in decided_rows) != sorted(REQUEST_CONTROL_IDS):
        raise AuthorityError('decided control set differs from the 21 requested controls')
    for name, label in (('applicability_decision_ids', 'top_level_field'), ('not_applicable_semantics', 'semantics_block')):
        if name not in authority:
            raise AuthorityError(f'authority lacks the {label} {name}')
    for field in PER_CONTROL_FIELDS:
        if any(field not in r for r in authority['controls']):
            raise AuthorityError(f'authority rows lack the field {field}')
    if any(r.get('decision_ids') != list(DECISIONS) for r in authority['controls']):
        raise AuthorityError('authority rows do not carry the eight AA1-GOV ids')
    controls = []
    for row in sorted(decided_rows, key=lambda r: r['control_id']):
        cid = row['control_id']
        if row['not_applicable_decision_state'] not in DECIDED_STATES:
            raise AuthorityError(f'{cid}: state is not a decided state')
        rec = latest.get(cid)
        if rec is None:
            raise AuthorityError(f'{cid}: no decision record')
        if rec['decided_outcome'] != row['not_applicable_decision_state'] or rec['decision_id'] != row['not_applicable_authority'] or rec['decided']['rule'] != row['not_applicable_rule']:
            raise AuthorityError(f'{cid}: decision record disagrees with the authority row')
        controls.append({'control_id': cid, 'decision_state': row['not_applicable_decision_state'], 'authority': row['not_applicable_authority'], 'rule': row['not_applicable_rule'], 'reason': first_sentence(rec['decided']['rationale'])})
    example = next((r for r in sorted(decided_rows, key=lambda r: r['control_id']) if r['not_applicable_decision_state'] == 'RULE_PUBLISHED'), None)
    if example is None:
        raise AuthorityError('no RULE_PUBLISHED row for the example')
    undecided = [r for r in authority['controls'] if r['not_applicable_decision_state'] == 'NOT_YET_DECIDED']
    if len(undecided) + len(controls) != len(rows):
        raise AuthorityError('control counts do not add up')
    validate_signoff(signoff, record['authority_sha256'])
    appr = signoff['approval']
    if record['authority_id'] != authority['authority_id'] or record['version'] != authority['version']:
        raise AuthorityError('publication record does not match the authority')
    sup = authority['source_lineage']['supersedes']
    decisions_sha = pinned_digest(REPLY_PUBLICATION_COMMIT, GOVERNANCE_DECISIONS)
    if decisions_sha != sup['governance_decisions_sha256']:
        raise AuthorityError('governance decisions differ from the superseded version, so no-decision-changed cannot be stated')
    record_commit = resolve_record_commit()
    if record_commit == record['publication_commit']:
        raise AuthorityError('record commit equals the publication commit')
    history_note = {'supersedes_authority_id': sup['authority_id'], 'supersedes_version': sup['version'], 'supersedes_commit': sup['commit'], 'purpose': 'Hardens the publication checks.', 'enforced_gates': list(ENFORCED_GATES), 'decisions_changed': False, 'governance_decisions_sha256': decisions_sha}
    return {
        'document_id': DOCUMENT_ID, 'request_id': REQUEST_ID, 'request_label': REQUEST_LABEL, 'reply_date': appr['date'],
        'from_authority': {'approver': appr['approver'], 'role': appr['role'], 'roles': list(APPROVER_ROLES)},
        'dual_role_statement': signoff['dual_role_statement'],
        'pin': {'publication_commit': record['publication_commit'], 'authority_id': record['authority_id'], 'version': record['version'], 'authority_sha256': record['authority_sha256'], 'manifest_sha256': record['manifest_sha256'], 'digest_normalisation': record['digest_normalisation'], 'publication_record_commit': record_commit},
        'published_shape': {
            'authority_path': rel(AUTHORITY), 'schema_path': rel(SCHEMA), 'generated_folder': rel(OUT),
            'manifest_path': f'{rel(OUT)}/{N_MANIFEST}', 'decision_traceability_path': f'{rel(OUT)}/{N_TRACE}',
            'decision_records_path': GOVERNANCE_DECISIONS_REL,
            'per_control_fields': list(PER_CONTROL_FIELDS),
            'decision_state_values': list(DECISION_STATES),
            'top_level_field': 'applicability_decision_ids', 'per_control_ids_field': 'decision_ids', 'per_control_ids_carry': list(DECISIONS),
            'semantics_block': 'not_applicable_semantics',
            'example_decided_row': example,
        },
        'controls': controls,
        'not_yet_decided': {'count': len(undecided), 'state': 'NOT_YET_DECIDED', 'date': None},
        'hayes_side_changes_needed': [
            'The target description must carry the eight classification facts.',
            'Hayes must read the published v2 shape.',
            f"Hayes must re-pin to {record['publication_commit']}.",
        ],
        'classification_prerequisites_gap_untouched': True,
        'live_resolved_count_stays_zero': True,
        'history_note': history_note,
        'send_condition': f"Do not send this reply until commit {record['publication_commit']} is on the remote branch {REMOTE_BRANCH}.",
    }


def render_markdown(reply: dict) -> str:
    pin, shape, hist = reply['pin'], reply['published_shape'], reply['history_note']
    by_id = {c['control_id']: c for c in reply['controls']}
    rules = {c['control_id']: c['rule'] for c in reply['controls'] if c['rule']}
    n_rule = sum(c['decision_state'] == 'RULE_PUBLISHED' for c in reply['controls'])
    n_none = len(reply['controls']) - n_rule
    L: list[str] = []
    L += [f"# Reply to {reply['request_id']} ({reply['request_label']})", '',
          f"This file is generated by {SCRIPT_REL} from the published authority and is read-only. Rebuild it with that script; do not edit it by hand.", '']
    L += ['## Opening', '',
          f"This is EMS's answer to request {reply['request_id']}, labelled {reply['request_label']}. The request asked, for each of 21 named controls, for either the not-applicable rule with its authority or a statement that no rule will be published. This reply gives one or the other for each of the 21 controls, so it is EMS's complete answer under the request's terms.", '',
          f"It is written as from {reply['from_authority']['approver']}, acting as the EMS governance authority, and dated {reply['reply_date']}. It stays unsigned in the repository until it is sent.", '',
          f"Dual role: {reply['dual_role_statement']}", '']
    L += ['## Decisions per control', '',
          f"{len(reply['controls'])} controls are decided: {n_rule} with a published rule and {n_none} with no rule. Each line gives the control, the decision state, the authority id, the rule, and the first sentence of the recorded reason. The full reason for each is in {shape['decision_records_path']}.", '']
    for c in reply['controls']:
        rule = rule_text(c['rule']) if c['rule'] else 'no rule'
        L += [f"- {c['control_id']}: {c['decision_state']}; authority {c['authority']}; rule: {rule}", f"  Reason: {c['reason']}"]
    L += ['']
    L += ['## What the rules mean', '']
    for cid, rule in sorted(rules.items()):
        conds = rule['conditions']
        words = ' and '.join(f"{c['field']} is {c['state']}" for c in conds)
        L.append(f"- {cid} is not applicable only when {words}. Machine form: {rule_text(rule)}.")
    L += ['',
          'If any field named by a rule is UNKNOWN, the result is APPLICABILITY_UNRESOLVED. UNKNOWN never resolves to not applicable. An explicit controlled rule is required for not applicable, unknown is not false, and absence of evidence is not not-applicable. A control with NO_RULE_WILL_BE_PUBLISHED is applicable whatever the facts.', '',
          "Hayes's resolver resolves no control until the target description carries the eight classification facts; under the EMS resolution table alone, a control with NO_RULE_WILL_BE_PUBLISHED is applicable whatever the facts.", '']
    L += ['## The pin', '',
          f"Cite this commit: {pin['publication_commit']}", '',
          f"- Authority id: {pin['authority_id']}",
          f"- Version: {pin['version']}",
          f"- Authority sha256: {pin['authority_sha256']}",
          f"- Publication manifest sha256: {pin['manifest_sha256']}",
          f"- Digest normalisation: {pin['digest_normalisation']} (both digests are computed over bytes with CRLF replaced by LF)", '',
          f"The commit {pin['publication_record_commit']} records the publication commit in a publication record, and this reply has its own commit. Neither changes the authority.", '']
    L += ['## The published shape', '',
          f"- Authority: {shape['authority_path']}",
          f"- Schema: {shape['schema_path']}",
          f"- Generated outputs: {shape['generated_folder']}/",
          f"- Manifest: {shape['manifest_path']}",
          f"- Decision traceability: {shape['decision_traceability_path']}",
          f"- Decision records: {shape['decision_records_path']}", '',
          f"Each control row carries {', '.join(shape['per_control_fields'])}. The decision state is one of {', '.join(shape['decision_state_values'])}. The top-level field {shape['top_level_field']} lists the cited authority ids. The field {shape['per_control_ids_field']} still carries the eight AA1-GOV ids ({shape['per_control_ids_carry'][0]} to {shape['per_control_ids_carry'][-1]}) on every row.", '',
          f"The full meaning of a rule is defined by the {shape['semantics_block']} block in the authority and by the schema.", '',
          f"One decided row from the authority ({shape['example_decided_row']['control_id']}):", '',
          '```json', jtext(shape['example_decided_row']).rstrip('\n'), '```', '']
    nyd = reply['not_yet_decided']
    L += ['## The other controls', '',
          f"The other {nyd['count']} controls stay {nyd['state']}. EMS gives no date for them. A rule for any of them would need a new governance decision and a new authority version.", '']
    L += ['## What publication does not change', '',
          'Three changes on the Hayes side are still needed before any control resolves:', '']
    for i, item in enumerate(reply['hayes_side_changes_needed'], 1):
        L.append(f"{i}. {item}")
    L += ['',
          'The classification-prerequisites gap is untouched by this publication. The live count of resolved controls stays at zero until those changes land.', '',
          'A Hayes test that expects all 21 controls to refuse is expected to fail after the re-pin.', '']
    L += ['## History', '',
          f"{pin['authority_id']} supersedes {hist['supersedes_authority_id']} (commit {hist['supersedes_commit'][:7]}). {hist['purpose']} The publisher now enforces these gates:", '']
    for gate in hist['enforced_gates']:
        L.append(f"- {gate}")
    L += ['',
          f"None of the 21 decisions changed. The governance decisions file has the same LF sha256 as at {hist['supersedes_version']}: {hist['governance_decisions_sha256']}.", '']
    L += ['## Sending', '', reply['send_condition'], '']
    text = '\n'.join(L)
    if '\r' in text:
        raise AuthorityError('rendered text contains a carriage return')
    return text


def frozen_schema() -> dict: return json.loads(git_show(REPLY_SCHEMA_COMMIT, REPLY_SCHEMA_REL).decode('utf-8'))


def validate_reply_object(reply: dict) -> None:
    jsonschema.Draft202012Validator(frozen_schema()).validate(reply)
    if contains_absolute(reply):
        raise AuthorityError('reply contains an absolute path')
    ids = [c['control_id'] for c in reply['controls']]
    if ids != sorted(REQUEST_CONTROL_IDS):
        raise AuthorityError('reply controls differ from the 21 requested controls')
    if reply['dual_role_statement'] != DUAL_ROLE_STATEMENT:
        raise AuthorityError('dual role statement differs from the published statement')


def check_inputs_bound(manifest: dict) -> None:
    man = {a['relative_path']: a['sha256'] for a in manifest['artifacts']}
    if man.get(rel(SIGNOFF)) != pinned_digest(REPLY_PUBLICATION_COMMIT, SIGNOFF):
        raise AuthorityError('sign-off differs from the published manifest')
    trace_path = OUT / N_TRACE
    trace = pinned_json(REPLY_PUBLICATION_COMMIT, trace_path)
    if man.get(rel(trace_path)) != pinned_digest(REPLY_PUBLICATION_COMMIT, trace_path):
        raise AuthorityError('decision traceability differs from the published manifest')
    doc_sha = pinned_digest(REPLY_PUBLICATION_COMMIT, GOVERNANCE_DECISIONS)
    if not trace['decision_records'] or any(r['decision_record_sha256'] != doc_sha for r in trace['decision_records']):
        raise AuthorityError('decision records differ from the published traceability')


def load_inputs() -> tuple:
    authority, signoff = pinned_json(REPLY_PUBLICATION_COMMIT, AUTHORITY), pinned_json(REPLY_PUBLICATION_COMMIT, SIGNOFF)
    decisions, manifest = pinned_json(REPLY_PUBLICATION_COMMIT, GOVERNANCE_DECISIONS), pinned_json(REPLY_PUBLICATION_COMMIT, OUT / N_MANIFEST)
    record = pinned_json(REPLY_RECORD_COMMIT, PUBLICATION_RECORD)
    if record.get('publication_commit') != REPLY_PUBLICATION_COMMIT:
        raise AuthorityError('REPLY_PUBLICATION_COMMIT differs from the publication_commit named by the frozen publication record')
    if record['manifest_sha256'] != pinned_digest(REPLY_PUBLICATION_COMMIT, OUT / N_MANIFEST):
        raise AuthorityError('publication record manifest digest differs from the published manifest')
    check_inputs_bound(manifest)
    return authority, record, signoff, decisions


def validate_reply() -> None:
    for p in (REPLY_JSON, REPLY_MD, REPLY_SCHEMA):
        if not p.exists():
            raise AuthorityError(f'{rel(p)}: not generated')
    authority, record, signoff, decisions = load_inputs()
    reply = build_reply(authority, record, signoff, decisions)
    if lf_bytes(REPLY_JSON.read_bytes()) != jtext(reply).encode('utf-8'):
        raise AuthorityError('reply JSON differs from a fresh build')
    if lf_bytes(REPLY_MD.read_bytes()) != render_markdown(reply).encode('utf-8'):
        raise AuthorityError('reply Markdown differs from a fresh build')
    if lf_bytes(REPLY_SCHEMA.read_bytes()) != lf_bytes(git_show(REPLY_SCHEMA_COMMIT, REPLY_SCHEMA_REL)):
        raise AuthorityError(f'reply schema differs from the frozen schema at {REPLY_SCHEMA_COMMIT}')
    validate_reply_object(load(REPLY_JSON))
    jsonschema.Draft202012Validator(load(REPLY_SCHEMA)).validate(load(REPLY_JSON))
    if record['authority_sha256'] != pinned_digest(REPLY_PUBLICATION_COMMIT, AUTHORITY) or record['manifest_sha256'] != pinned_digest(REPLY_PUBLICATION_COMMIT, OUT / N_MANIFEST):
        raise AuthorityError('publication record digests differ from the published files')
    print('PASS')


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(['git', *args], cwd=ROOT, capture_output=True, text=True)


def resolve_record_commit() -> str:
    try:
        s = git('rev-parse', '--is-shallow-repository')
    except OSError as e:
        raise AuthorityError(f'cannot check whether the clone is shallow: {e}') from e
    if s.returncode != 0 or s.stdout.strip() != 'false':
        raise AuthorityError('shallow clone or unreadable repository: cannot resolve the publication record commit; fetch full history')
    for sha in (REPLY_RECORD_COMMIT, REPLY_PUBLICATION_COMMIT, REPLY_SCHEMA_COMMIT):
        if not re.fullmatch(r'[0-9a-f]{40}', sha) or git('cat-file', '-e', f'{sha}^{{commit}}').returncode != 0:
            raise AuthorityError(f'the frozen commit {sha} is not in the repository history; fetch full history (git fetch --unshallow)')
        if git('merge-base', '--is-ancestor', sha, 'HEAD').returncode != 0:
            raise AuthorityError(f'the frozen commit {sha} is not an ancestor of HEAD')
    return REPLY_RECORD_COMMIT


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--validate', action='store_true')
    args = parser.parse_args()
    if args.validate: validate_reply()


if __name__ == '__main__': main()

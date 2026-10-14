from __future__ import annotations

import argparse
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location('aa_applicability_publisher_v2', ROOT / 'scripts' / 'publish_archive_assessment_applicability_authority_v2.py')
V2 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(V2)

REPLY_JSON = ROOT / 'registry' / 'archive_assessment_demo3_w1_req_001_reply.json'
REPLY_MD = ROOT / 'docs' / 'DEMO3_W1_REQ_001_REPLY.md'
REPLY_SCHEMA = ROOT / 'schemas' / 'archive_assessment_demo3_w1_req_001_reply.schema.json'
REPLY_DATE = '2026-10-14'
REQUEST_ID = 'DEMO3-W1-REQ-001'
REQUEST_LABEL = 'EMSREQ-APPLIC-RULES'
DOCUMENT_ID = 'EMS-DEMO3-W1-REQ-001-REPLY'
RECORD_COMMIT_ABBREV = '0ce89f2'
REVIEW_REL = '.planning/phases/04-certified-publication/04-REVIEW.md'
VERIFICATION_REL = '.planning/phases/04-certified-publication/04-VERIFICATION.md'
SCRIPT_REL = 'scripts/build_archive_assessment_demo3_w1_req_001_reply.py'
REMOTE_BRANCH = 'feature/ems-aa3-archive-applicability-authority'
DECIDED_STATES = ['RULE_PUBLISHED', 'NO_RULE_WILL_BE_PUBLISHED']
REPLY_KEYS = ['document_id', 'request_id', 'request_label', 'reply_date', 'from_authority', 'dual_role_statement', 'pin', 'published_shape', 'controls', 'not_yet_decided', 'hayes_side_changes_needed', 'classification_prerequisites_gap_untouched', 'live_resolved_count_stays_zero', 'disclosure', 'send_condition']
PIN_KEYS = ['publication_commit', 'authority_id', 'version', 'authority_sha256', 'manifest_sha256', 'digest_normalisation', 'publication_record_commit']
DIGEST_RE = r'^[0-9a-f]{64}$'
FORBIDDEN_WORDS = ('best', 'critical', 'important', 'recommended', 'highest')


def first_sentence(text: str) -> str:
    s = re.split(r'(?<=\.)\s+(?=[A-Z])', text, maxsplit=1)[0]
    if not s or '\n' in s or '\r' in s or not s.endswith('.') or re.search(r'\b(e\.g|i\.e|etc|vs)\.$', s):
        raise V2.AuthorityError('rationale first sentence cannot be cut deterministically')
    return s


def build_reply(authority: dict, record: dict, signoff: dict, decisions: dict, manifest: dict) -> dict:
    rows = {r['control_id']: r for r in authority['controls']}
    latest = {r['control_id']: r for r in V2.latest_records(decisions)}
    decided_rows = [r for r in authority['controls'] if r['not_applicable_decision_state'] != 'NOT_YET_DECIDED']
    if sorted(r['control_id'] for r in decided_rows) != sorted(V2.REQUEST_CONTROL_IDS):
        raise V2.AuthorityError('decided control set differs from the 21 requested controls')
    controls = []
    for row in sorted(decided_rows, key=lambda r: r['control_id']):
        cid = row['control_id']
        if row['not_applicable_decision_state'] not in DECIDED_STATES:
            raise V2.AuthorityError(f'{cid}: state is not a decided state')
        rec = latest.get(cid)
        if rec is None:
            raise V2.AuthorityError(f'{cid}: no decision record')
        if rec['decided_outcome'] != row['not_applicable_decision_state'] or rec['decision_id'] != row['not_applicable_authority'] or rec['decided']['rule'] != row['not_applicable_rule']:
            raise V2.AuthorityError(f'{cid}: decision record disagrees with the authority row')
        controls.append({'control_id': cid, 'decision_state': row['not_applicable_decision_state'], 'authority': row['not_applicable_authority'], 'rule': row['not_applicable_rule'], 'reason': first_sentence(rec['decided']['rationale'])})
    example = next(r for r in sorted(decided_rows, key=lambda r: r['control_id']) if r['not_applicable_decision_state'] == 'RULE_PUBLISHED')
    undecided = [r for r in authority['controls'] if r['not_applicable_decision_state'] == 'NOT_YET_DECIDED']
    if len(undecided) + len(controls) != len(rows):
        raise V2.AuthorityError('control counts do not add up')
    V2.validate_signoff(signoff, record['authority_sha256'])
    appr = signoff['approval']
    if record['authority_id'] != authority['authority_id'] or record['version'] != authority['version']:
        raise V2.AuthorityError('publication record does not match the authority')
    return {
        'document_id': DOCUMENT_ID, 'request_id': REQUEST_ID, 'request_label': REQUEST_LABEL, 'reply_date': REPLY_DATE,
        'from_authority': {'approver': appr['approver'], 'role': appr['role'], 'roles': list(V2.APPROVER_ROLES)},
        'dual_role_statement': signoff['dual_role_statement'],
        'pin': {'publication_commit': record['publication_commit'], 'authority_id': record['authority_id'], 'version': record['version'], 'authority_sha256': record['authority_sha256'], 'manifest_sha256': record['manifest_sha256'], 'digest_normalisation': record['digest_normalisation'], 'publication_record_commit': RECORD_COMMIT_ABBREV},
        'published_shape': {
            'authority_path': V2.rel(V2.AUTHORITY), 'schema_path': V2.rel(V2.SCHEMA), 'generated_folder': V2.rel(V2.OUT),
            'manifest_path': f'{V2.rel(V2.OUT)}/{V2.N_MANIFEST}', 'decision_traceability_path': f'{V2.rel(V2.OUT)}/{V2.N_TRACE}',
            'decision_records_path': V2.GOVERNANCE_DECISIONS_REL,
            'per_control_fields': ['not_applicable_decision_state', 'not_applicable_rule', 'not_applicable_authority'],
            'decision_state_values': list(V2.DECISION_STATES),
            'top_level_field': 'applicability_decision_ids', 'per_control_ids_field': 'decision_ids', 'per_control_ids_carry': list(V2.DECISIONS),
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
        'disclosure': {'review_path': REVIEW_REL, 'verification_path': VERIFICATION_REL, 'wr_01': 'WR-01: the semantic, negative-invariant and certification outputs record PASS and REJECTED_FAIL_CLOSED for checks the publisher does not run.', 'v2_0_1_possible': True, 'v2_0_1_date': None},
        'send_condition': f"Do not send this reply until commit {record['publication_commit']} is on the remote branch {REMOTE_BRANCH}.",
    }


def render_markdown(reply: dict) -> str:
    pin, shape, disc = reply['pin'], reply['published_shape'], reply['disclosure']
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
        rule = V2.rule_text(c['rule']) if c['rule'] else 'no rule'
        L += [f"- {c['control_id']}: {c['decision_state']}; authority {c['authority']}; rule: {rule}", f"  Reason: {c['reason']}"]
    L += ['']
    L += ['## What the rules mean', '']
    for cid, rule in sorted(rules.items()):
        conds = rule['conditions']
        words = ' and '.join(f"{c['field']} is {c['state']}" for c in conds)
        L.append(f"- {cid} is not applicable only when {words}. Machine form: {V2.rule_text(rule)}.")
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
          '```json', V2.jtext(shape['example_decided_row']).rstrip('\n'), '```', '']
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
    L += ['## Disclosure', '',
          f"The published data was checked independently and is correct; see {disc['verification_path']}. The checks that guard publication have known gaps, listed in {disc['review_path']}. None of them changes any of the 21 decisions. The list of findings is not repeated here.", '',
          f"{disc['wr_01']} Do not cite those fields as independent evidence.", '',
          'A hardening release, v2.0.1, may follow. EMS gives no date. It would need a new sign-off and a new pin, and it is not intended to change any of the 21 decisions.', '']
    L += ['## Sending', '', reply['send_condition'], '']
    text = '\n'.join(L)
    if '\r' in text:
        raise V2.AuthorityError('rendered text contains a carriage return')
    return text


def schema() -> dict:
    cond = {'type': 'object', 'additionalProperties': False, 'required': ['field', 'state'], 'properties': {'field': {'enum': list(V2.RULE_FIELDS)}, 'state': {'enum': list(V2.CONDITION_STATES)}}}
    rule = {'type': 'object', 'additionalProperties': False, 'required': ['combination', 'conditions'], 'properties': {'combination': {'const': V2.COMBINATION}, 'conditions': {'type': 'array', 'minItems': 1, 'maxItems': len(V2.RULE_FIELDS), 'items': cond}}}
    s = {'type': 'string', 'minLength': 1}
    sha = {'type': 'string', 'pattern': DIGEST_RE}
    def branch(state, rule_s):
        return {'if': {'properties': {'decision_state': {'const': state}}, 'required': ['decision_state']}, 'then': {'properties': {'rule': rule_s}}}
    control = {'type': 'object', 'additionalProperties': False, 'required': ['control_id', 'decision_state', 'authority', 'rule', 'reason'],
        'properties': {'control_id': {'type': 'string', 'pattern': '^EMS-CTRL-[0-9]{3}$'}, 'decision_state': {'enum': list(DECIDED_STATES)}, 'authority': {'type': 'string', 'pattern': V2.AUTHORITY_ID_RE}, 'rule': {'anyOf': [rule, {'type': 'null'}]}, 'reason': s},
        'allOf': [branch('RULE_PUBLISHED', rule), branch('NO_RULE_WILL_BE_PUBLISHED', {'type': 'null'})]}
    shape_keys = ['authority_path', 'schema_path', 'generated_folder', 'manifest_path', 'decision_traceability_path', 'decision_records_path', 'per_control_fields', 'decision_state_values', 'top_level_field', 'per_control_ids_field', 'per_control_ids_carry', 'semantics_block', 'example_decided_row']
    return {'$schema': 'https://json-schema.org/draft/2020-12/schema', 'title': 'EMS reply to Hayes Verify request DEMO3-W1-REQ-001', 'type': 'object', 'additionalProperties': False, 'required': list(REPLY_KEYS),
        'properties': {
            'document_id': {'const': DOCUMENT_ID}, 'request_id': {'const': REQUEST_ID}, 'request_label': {'const': REQUEST_LABEL}, 'reply_date': {'type': 'string', 'pattern': r'^[0-9]{4}-[0-9]{2}-[0-9]{2}$'},
            'from_authority': {'type': 'object', 'additionalProperties': False, 'required': ['approver', 'role', 'roles'], 'properties': {'approver': s, 'role': s, 'roles': {'type': 'array', 'items': s}}},
            'dual_role_statement': s,
            'pin': {'type': 'object', 'additionalProperties': False, 'required': list(PIN_KEYS), 'properties': {'publication_commit': {'type': 'string', 'pattern': '^[0-9a-f]{40}$'}, 'authority_id': s, 'version': s, 'authority_sha256': sha, 'manifest_sha256': sha, 'digest_normalisation': {'const': 'CRLF_TO_LF'}, 'publication_record_commit': {'type': 'string', 'pattern': '^[0-9a-f]{7,40}$'}}},
            'published_shape': {'type': 'object', 'additionalProperties': False, 'required': shape_keys, 'properties': {**{k: s for k in shape_keys if k not in ('per_control_fields', 'decision_state_values', 'per_control_ids_carry', 'example_decided_row')}, 'per_control_fields': {'type': 'array', 'items': s}, 'decision_state_values': {'type': 'array', 'items': s}, 'per_control_ids_carry': {'type': 'array', 'items': s}, 'example_decided_row': {'type': 'object'}}},
            'controls': {'type': 'array', 'minItems': 21, 'maxItems': 21, 'items': control},
            'not_yet_decided': {'type': 'object', 'additionalProperties': False, 'required': ['count', 'state', 'date'], 'properties': {'count': {'type': 'integer', 'minimum': 0}, 'state': {'const': 'NOT_YET_DECIDED'}, 'date': {'type': 'null'}}},
            'hayes_side_changes_needed': {'type': 'array', 'minItems': 3, 'maxItems': 3, 'items': s},
            'classification_prerequisites_gap_untouched': {'const': True}, 'live_resolved_count_stays_zero': {'const': True},
            'disclosure': {'type': 'object', 'additionalProperties': False, 'required': ['review_path', 'verification_path', 'wr_01', 'v2_0_1_possible', 'v2_0_1_date'], 'properties': {'review_path': s, 'verification_path': s, 'wr_01': s, 'v2_0_1_possible': {'const': True}, 'v2_0_1_date': {'type': 'null'}}},
            'send_condition': s}}


def validate_reply_object(reply: dict) -> None:
    jsonschema.Draft202012Validator(schema()).validate(reply)
    if V2.contains_absolute(reply):
        raise V2.AuthorityError('reply contains an absolute path')
    ids = [c['control_id'] for c in reply['controls']]
    if ids != sorted(V2.REQUEST_CONTROL_IDS):
        raise V2.AuthorityError('reply controls differ from the 21 requested controls')
    if reply['dual_role_statement'] != V2.DUAL_ROLE_STATEMENT:
        raise V2.AuthorityError('dual role statement differs from the published statement')


def check_inputs_bound(manifest: dict) -> None:
    man = {a['relative_path']: a['sha256'] for a in manifest['artifacts']}
    if man.get(V2.rel(V2.SIGNOFF)) != V2.lf_digest(V2.SIGNOFF):
        raise V2.AuthorityError('sign-off differs from the published manifest')
    trace = V2.load(V2.OUT / V2.N_TRACE)
    if man.get(f'{V2.rel(V2.OUT)}/{V2.N_TRACE}') != V2.lf_digest(V2.OUT / V2.N_TRACE):
        raise V2.AuthorityError('decision traceability differs from the published manifest')
    doc_sha = V2.lf_digest(V2.GOVERNANCE_DECISIONS)
    if not trace['decision_records'] or any(r['decision_record_sha256'] != doc_sha for r in trace['decision_records']):
        raise V2.AuthorityError('decision records differ from the published traceability')


def load_inputs() -> tuple:
    authority, record, signoff = V2.load(V2.AUTHORITY), V2.load(V2.PUBLICATION_RECORD), V2.load(V2.SIGNOFF)
    decisions, manifest = V2.load(V2.GOVERNANCE_DECISIONS), V2.load(V2.OUT / V2.N_MANIFEST)
    if record['manifest_sha256'] != V2.lf_digest(V2.OUT / V2.N_MANIFEST):
        raise V2.AuthorityError('publication record manifest digest differs from the published manifest')
    check_inputs_bound(manifest)
    return authority, record, signoff, decisions, manifest


def validate_reply() -> None:
    for p in (REPLY_JSON, REPLY_MD, REPLY_SCHEMA):
        if not p.exists():
            raise V2.AuthorityError(f'{V2.rel(p)}: not generated')
    authority, record, signoff, decisions, manifest = load_inputs()
    reply = build_reply(authority, record, signoff, decisions, manifest)
    if V2.lf_bytes(REPLY_JSON.read_bytes()) != V2.jtext(reply).encode('utf-8'):
        raise V2.AuthorityError('reply JSON differs from a fresh build')
    if V2.lf_bytes(REPLY_MD.read_bytes()) != render_markdown(reply).encode('utf-8'):
        raise V2.AuthorityError('reply Markdown differs from a fresh build')
    if V2.lf_bytes(REPLY_SCHEMA.read_bytes()) != V2.jtext(schema()).encode('utf-8'):
        raise V2.AuthorityError('reply schema differs from a fresh build')
    validate_reply_object(V2.load(REPLY_JSON))
    jsonschema.Draft202012Validator(V2.load(REPLY_SCHEMA)).validate(V2.load(REPLY_JSON))
    if record['authority_sha256'] != V2.lf_digest(V2.AUTHORITY) or record['manifest_sha256'] != V2.lf_digest(V2.OUT / V2.N_MANIFEST):
        raise V2.AuthorityError('publication record digests differ from the published files')
    print('PASS')


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(['git', *args], cwd=ROOT, capture_output=True, text=True)


PUSH_ON, PUSH_NOT_ON, PUSH_UNKNOWN = 0, 1, 2


def push_check() -> int:
    sha = V2.load(V2.PUBLICATION_RECORD)['publication_commit']
    ref = f'refs/heads/{REMOTE_BRANCH}'
    r = git('ls-remote', 'origin', ref)
    tip = r.stdout.split()[0] if r.returncode == 0 and r.stdout.strip() else None
    if tip is None:
        print(f'UNKNOWN: could not read the remote tip of {ref} (ls-remote exit {r.returncode}; branch may be absent on the remote)')
        status = PUSH_UNKNOWN
    elif git('cat-file', '-e', f'{tip}^{{commit}}').returncode != 0:
        print(f'UNKNOWN: remote tip {tip} is not present locally, so ancestry cannot be checked without a fetch')
        status = PUSH_UNKNOWN
    else:
        mb = git('merge-base', '--is-ancestor', sha, tip).returncode
        if mb == 0:
            print(f'Publication commit {sha} is on the remote branch (remote tip {tip})')
            status = PUSH_ON
        elif mb == 1:
            print(f'Publication commit {sha} is NOT on the remote branch (remote tip {tip})')
            status = PUSH_NOT_ON
        else:
            print(f'UNKNOWN: ancestry of {sha} against remote tip {tip} cannot be determined (merge-base exit {mb})')
            status = PUSH_UNKNOWN
    print(f'Push command: git push origin {REMOTE_BRANCH}')
    return status


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--build', action='store_true'); parser.add_argument('--validate', action='store_true'); parser.add_argument('--emit-schema', action='store_true'); parser.add_argument('--push-check', action='store_true')
    args = parser.parse_args()
    if args.emit_schema: V2.dump(REPLY_SCHEMA, schema())
    elif args.build:
        reply = build_reply(*load_inputs())
        validate_reply_object(reply)
        V2.dump(REPLY_JSON, reply); V2.write_text(REPLY_MD, render_markdown(reply))
    elif args.validate: validate_reply()
    elif args.push_check: sys.exit(push_check())
    else: parser.error('one of --build, --validate, --emit-schema or --push-check is required')


if __name__ == '__main__': main()

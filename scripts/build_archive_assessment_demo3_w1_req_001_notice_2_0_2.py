from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location('aa_applicability_publisher_v2', ROOT / 'scripts' / 'publish_archive_assessment_applicability_authority_v2.py')
V2 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(V2)

NOTICE_JSON = ROOT / 'registry' / 'archive_assessment_demo3_w1_req_001_notice_2_0_2.json'
NOTICE_MD = ROOT / 'docs' / 'DEMO3_W1_REQ_001_NOTICE_2_0_2.md'
NOTICE_SCHEMA = ROOT / 'schemas' / 'archive_assessment_demo3_w1_req_001_notice_2_0_2.schema.json'
NOTICE_PUBLICATION_COMMIT = 'ae15c7458e49c8f55cc58c61bab04bc716aa9892'
NOTICE_RECORD_COMMIT = 'a71257ed267410138a3c4daba412b00c116663d8'
SUPERSEDED_COMMIT = '31addfa95ffc5c2d6805c73fa1f34d6ccbe313eb'
NOTICE_AUTHORITY_ID = 'EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.2'
NOTICE_VERSION = '2.0.2'
SUPERSEDED_AUTHORITY_ID = 'EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.1'
SUPERSEDED_VERSION = '2.0.1'
REQUEST_ID = 'DEMO3-W1-REQ-001'
REQUEST_LABEL = 'EMSREQ-APPLIC-RULES'
DOCUMENT_ID = 'EMS-DEMO3-W1-REQ-001-NOTICE-2.0.2'
SCRIPT_REL = 'scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_2.py'
REMOTE_BRANCH = 'feature/ems-aa3-archive-applicability-authority'
NOTICE_DATE = '2026-11-12'
NOTICE_KEYS = ['document_id', 'request_id', 'request_label', 'notice_date', 'from_authority', 'dual_role_statement', 'pin', 'supersedes', 'what_changed', 'digest_scope_error', 'decisions', 'hayes_side_changes_needed', 'send_condition']
PIN_KEYS = ['publication_commit', 'authority_id', 'version', 'authority_sha256', 'manifest_sha256', 'digest_normalisation', 'publication_record_commit', 'published_on']
DIGEST_RE = r'^[0-9a-f]{64}$'
SHA_RE = r'^[0-9a-f]{40}$'
DATE_RE = r'^[0-9]{4}-[0-9]{2}-[0-9]{2}$'
NORMALISATIONS = ['RAW_BYTES', 'CRLF_TO_LF']
RAW_LINEAGE_KEYS = ('aa1_manifest', 'aa2_approval', 'aa2_closure')
DIGEST_SCOPE_PAIRS = (('aa1_manifest_sha256', 'aa1_manifest'), ('aa2_closure_sha256', 'aa2_closure'), ('aa2_approval_sha256', 'aa2_approval'))
FORBIDDEN_WORDS = ('best', 'critical', 'important', 'recommended', 'highest')
GATE_FIX_LINE = 'The publisher gates GATE-01 to GATE-05 were fixed, together with WR-02, WR-04, the catalog decoupling, WR-05 and the uniqueness check on norm_templated.'
EXPECTED_COUNTS = {'decided_count': 21, 'rule_count': 3, 'no_rule_count': 18, 'not_yet_decided_count': 59}


def pinned_bytes(commit: str, path: Path) -> bytes:
    return V2.git_show(commit, V2.rel(path))


def pinned_json(commit: str, path: Path) -> dict:
    return json.loads(pinned_bytes(commit, path).decode('utf-8'))


def pinned_digest(commit: str, path: Path) -> str:
    return hashlib.sha256(V2.lf_bytes(pinned_bytes(commit, path))).hexdigest()


def pinned_raw_digest(commit: str, path: Path | str) -> str:
    relative = V2.rel(path) if isinstance(path, Path) else path
    return hashlib.sha256(V2.git_show(commit, relative)).hexdigest()


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(['git', *args], cwd=ROOT, capture_output=True, text=True)


def resolve_record_commit() -> str:
    try:
        s = git('rev-parse', '--is-shallow-repository')
    except OSError as e:
        raise V2.AuthorityError(f'cannot check whether the clone is shallow: {e}') from e
    if s.returncode != 0 or s.stdout.strip() != 'false':
        raise V2.AuthorityError('shallow clone or unreadable repository: cannot resolve the frozen commits; fetch full history')
    for sha in (NOTICE_PUBLICATION_COMMIT, SUPERSEDED_COMMIT, NOTICE_RECORD_COMMIT):
        if not re.fullmatch(r'[0-9a-f]{40}', sha) or git('cat-file', '-e', f'{sha}^{{commit}}').returncode != 0:
            raise V2.AuthorityError(f'the frozen commit {sha[:7]} is not in the repository history')
        if git('merge-base', '--is-ancestor', sha, 'HEAD').returncode != 0:
            raise V2.AuthorityError(f'the frozen commit {sha[:7]} is not an ancestor of HEAD')
    if git('merge-base', '--is-ancestor', NOTICE_PUBLICATION_COMMIT, NOTICE_RECORD_COMMIT).returncode != 0:
        raise V2.AuthorityError('the publication commit is not an ancestor of the record commit')
    return NOTICE_RECORD_COMMIT


def check_inputs_bound(manifest: dict) -> None:
    man = {a['relative_path']: a['sha256'] for a in manifest['artifacts']}
    for path in (V2.SIGNOFF, V2.SCHEMA, V2.AUTHORITY, V2.OUT / V2.N_NEGATIVE, V2.OUT / V2.N_TRACE):
        if man.get(V2.rel(path)) != pinned_digest(NOTICE_PUBLICATION_COMMIT, path):
            raise V2.AuthorityError(f'{V2.rel(path)} differs from the published manifest')
    trace = pinned_json(NOTICE_PUBLICATION_COMMIT, V2.OUT / V2.N_TRACE)
    doc_sha = pinned_digest(NOTICE_PUBLICATION_COMMIT, V2.GOVERNANCE_DECISIONS)
    if not trace['decision_records'] or any(r['decision_record_sha256'] != doc_sha for r in trace['decision_records']):
        raise V2.AuthorityError('decision records differ from the published traceability')


def load_inputs() -> tuple:
    resolve_record_commit()
    authority = pinned_json(NOTICE_PUBLICATION_COMMIT, V2.AUTHORITY)
    previous = pinned_json(SUPERSEDED_COMMIT, V2.AUTHORITY)
    signoff = pinned_json(NOTICE_PUBLICATION_COMMIT, V2.SIGNOFF)
    decisions = pinned_json(NOTICE_PUBLICATION_COMMIT, V2.GOVERNANCE_DECISIONS)
    manifest = pinned_json(NOTICE_PUBLICATION_COMMIT, V2.OUT / V2.N_MANIFEST)
    frozen_schema = pinned_json(NOTICE_PUBLICATION_COMMIT, V2.SCHEMA)
    negative = pinned_json(NOTICE_PUBLICATION_COMMIT, V2.OUT / V2.N_NEGATIVE)
    record = pinned_json(NOTICE_RECORD_COMMIT, V2.PUBLICATION_RECORD)
    if record.get('publication_commit') != NOTICE_PUBLICATION_COMMIT:
        raise V2.AuthorityError('NOTICE_PUBLICATION_COMMIT differs from the publication_commit named by the frozen publication record')
    if record['manifest_sha256'] != pinned_digest(NOTICE_PUBLICATION_COMMIT, V2.OUT / V2.N_MANIFEST):
        raise V2.AuthorityError('publication record manifest digest differs from the published manifest')
    check_inputs_bound(manifest)
    return authority, previous, record, signoff, decisions, manifest, frozen_schema, negative


def lineage_entries(authority: dict) -> list:
    lin = authority['source_lineage']
    out = []
    for key in sorted(lin):
        e = lin[key]
        if not isinstance(e, dict) or e.get('normalisation') not in NORMALISATIONS:
            raise V2.AuthorityError(f'source_lineage {key} lacks a declared normalisation')
        out.append({'key': key, 'relative_path': e['relative_path'], 'normalisation': e['normalisation'], 'sha256': e['sha256']})
    for key in RAW_LINEAGE_KEYS:
        e = lin.get(key)
        if not isinstance(e, dict) or e.get('normalisation') != 'RAW_BYTES':
            raise V2.AuthorityError(f'source_lineage {key} must be declared RAW_BYTES')
        if pinned_raw_digest(NOTICE_PUBLICATION_COMMIT, e['relative_path']) != e['sha256']:
            raise V2.AuthorityError(f'source_lineage {key} digest differs from the raw bytes in git')
    return out


def rows_differing(authority: dict, previous: dict) -> tuple[int, int]:
    rows, prev_rows = {r['control_id']: r for r in authority['controls']}, {r['control_id']: r for r in previous['controls']}
    if set(rows) != set(prev_rows) or authority.get('applicability_decision_ids') != previous.get('applicability_decision_ids'):
        raise V2.AuthorityError('control set or cited decision ids differ from the superseded version')
    return sum(any(rows[c].get(k) != prev_rows[c].get(k) for k in V2.PREV_COMPARED_KEYS) for c in rows), len(rows)


def digest_scope_error(authority: dict, previous: dict) -> dict:
    old, new = previous['source_lineage'], authority['source_lineage']
    if old.get('digest_normalisation') != 'CRLF_TO_LF':
        raise V2.AuthorityError('the superseded version does not declare the global CRLF_TO_LF claim')
    if sorted(k for k, e in new.items() if isinstance(e, dict) and e.get('normalisation') == 'RAW_BYTES') != sorted(n for _, n in DIGEST_SCOPE_PAIRS):
        raise V2.AuthorityError('the RAW_BYTES digests of 2.0.2 differ from the digests 2.0.1 declared under the global claim')
    digests = []
    for old_key, new_key in DIGEST_SCOPE_PAIRS:
        e = new.get(new_key)
        if not isinstance(e, dict) or e.get('normalisation') != 'RAW_BYTES':
            raise V2.AuthorityError(f'{new_key} is not declared RAW_BYTES in 2.0.2')
        if old.get(old_key) != e.get('sha256'):
            raise V2.AuthorityError(f'{old_key} in 2.0.1 differs from {new_key} in 2.0.2')
        digests.append({'previous_key': old_key, 'key': new_key, 'sha256': e['sha256'], 'previous_declared_scope': old['digest_normalisation'], 'declared_scope': e['normalisation']})
    return {'previous_version': SUPERSEDED_VERSION, 'previous_commit': SUPERSEDED_COMMIT, 'previous_declared_normalisation': old['digest_normalisation'], 'digests': digests, 'digest_values_changed': False}


def build_notice(authority: dict, previous: dict, record: dict, signoff: dict, decisions: dict, manifest: dict, frozen_schema: dict, negative: dict) -> dict:
    if authority['authority_id'] != NOTICE_AUTHORITY_ID or authority['version'] != NOTICE_VERSION:
        raise V2.AuthorityError('frozen authority is not the 2.0.2 authority')
    if record['authority_id'] != authority['authority_id'] or record['version'] != authority['version']:
        raise V2.AuthorityError('publication record does not match the authority')
    if record['authority_sha256'] != pinned_digest(NOTICE_PUBLICATION_COMMIT, V2.AUTHORITY):
        raise V2.AuthorityError('publication record authority digest differs from the published authority')
    V2.validate_signoff(signoff, record['authority_sha256'], authority_id=record['authority_id'], version=record['version'])
    appr = signoff['approval']
    if signoff['dual_role_statement'] != V2.DUAL_ROLE_STATEMENT:
        raise V2.AuthorityError('dual role statement differs from the published statement')
    if manifest.get('published_on') != appr['date']:
        raise V2.AuthorityError('manifest publication date differs from the sign-off date')
    sup = authority['source_lineage']['supersedes']
    if (sup['authority_id'], sup['version'], sup['commit']) != (SUPERSEDED_AUTHORITY_ID, SUPERSEDED_VERSION, SUPERSEDED_COMMIT):
        raise V2.AuthorityError('2.0.2 does not supersede the frozen 2.0.1 commit')
    if previous['authority_id'] != sup['authority_id'] or previous['version'] != sup['version'] or pinned_digest(SUPERSEDED_COMMIT, V2.AUTHORITY) != sup['sha256']:
        raise V2.AuthorityError('the authority frozen at the superseded commit differs from the supersedes entry')
    decisions_sha = pinned_digest(NOTICE_PUBLICATION_COMMIT, V2.GOVERNANCE_DECISIONS)
    if len({decisions_sha, pinned_digest(SUPERSEDED_COMMIT, V2.GOVERNANCE_DECISIONS), sup['governance_decisions_sha256'], previous['source_lineage']['governance_decisions']['sha256'], authority['source_lineage']['governance_decisions']['sha256']}) != 1:
        raise V2.AuthorityError('governance decisions differ from the superseded version, so no-decision-changed cannot be stated')
    rows = authority['controls']
    decided = [r for r in rows if r['not_applicable_decision_state'] != 'NOT_YET_DECIDED']
    if sorted(r['control_id'] for r in decided) != sorted(V2.REQUEST_CONTROL_IDS):
        raise V2.AuthorityError('decided control set differs from the 21 requested controls')
    rule_rows = sorted((r for r in decided if r['not_applicable_decision_state'] == 'RULE_PUBLISHED'), key=lambda r: r['control_id'])
    counts = {'decided_count': len(decided), 'rule_count': len(rule_rows), 'no_rule_count': sum(r['not_applicable_decision_state'] == 'NO_RULE_WILL_BE_PUBLISHED' for r in decided), 'not_yet_decided_count': len(rows) - len(decided)}
    if counts != EXPECTED_COUNTS or any(r['not_applicable_rule'] is None for r in rule_rows):
        raise V2.AuthorityError('decision counts differ from 21 decided, 3 rules, 18 no-rule and 59 undecided')
    differing, total = rows_differing(authority, previous)
    if differing:
        raise V2.AuthorityError(f'{differing} of {total} control rows differ from the superseded version, so no-decision-changed cannot be stated')
    levels = V2.closed_schema_levels(frozen_schema)
    tests = negative['negative_invariant_tests']
    return {
        'document_id': DOCUMENT_ID, 'request_id': REQUEST_ID, 'request_label': REQUEST_LABEL, 'notice_date': NOTICE_DATE,
        'from_authority': {'approver': appr['approver'], 'role': appr['role'], 'roles': list(V2.APPROVER_ROLES)},
        'dual_role_statement': signoff['dual_role_statement'],
        'pin': {'publication_commit': record['publication_commit'], 'authority_id': record['authority_id'], 'version': record['version'], 'authority_sha256': record['authority_sha256'], 'manifest_sha256': record['manifest_sha256'], 'digest_normalisation': record['digest_normalisation'], 'publication_record_commit': NOTICE_RECORD_COMMIT, 'published_on': appr['date']},
        'supersedes': {'authority_id': sup['authority_id'], 'version': sup['version'], 'commit': sup['commit']},
        'what_changed': {'lineage': lineage_entries(authority), 'negative_mutation_count': len(tests), 'closed_schema_levels': {'count': len(levels), 'paths': levels}, 'row_comparison': {'rows_compared': total, 'rows_differing': differing, 'compared_keys': list(V2.PREV_COMPARED_KEYS)}, 'gate_fix_line': GATE_FIX_LINE},
        'digest_scope_error': digest_scope_error(authority, previous),
        'decisions': {**counts, 'rules': [{'control_id': r['control_id'], 'authority': r['not_applicable_authority'], 'rule': r['not_applicable_rule'], 'machine_form': V2.rule_text(r['not_applicable_rule'])} for r in rule_rows], 'governance_decisions_sha256': decisions_sha, 'decisions_changed': False},
        'hayes_side_changes_needed': [
            f"Re-pin to {record['publication_commit']}, replacing {sup['commit']}.",
            'The target description must carry the eight classification facts.',
            'Hayes must read the published v2 shape.',
        ],
        'send_condition': f'Do not send this notice until the commit that adds it is on the remote branch {REMOTE_BRANCH}.',
    }


def render_markdown(notice: dict) -> str:
    pin, sup, wc, ds, dec = notice['pin'], notice['supersedes'], notice['what_changed'], notice['digest_scope_error'], notice['decisions']
    rc, lv = wc['row_comparison'], wc['closed_schema_levels']
    L: list[str] = []
    L += [f"# Notice to Hayes Verify: authority {pin['version']} for {notice['request_id']} ({notice['request_label']})", '',
          f"This file is generated by {SCRIPT_REL} from the published authority and is read-only. Rebuild it with that script; do not edit it by hand.", '']
    L += ['## Opening', '',
          f"This notice tells Hayes Verify that EMS has published authority version {pin['version']}, which supersedes version {sup['version']}. It relates to request {notice['request_id']}, labelled {notice['request_label']}. It is written as from {notice['from_authority']['approver']}, acting as the EMS governance authority, and dated {notice['notice_date']}. It stays unsigned in the repository until it is sent.", '',
          f"Dual role: {notice['dual_role_statement']}", '']
    L += ['## What to do', '', 'Three changes on the Hayes side are needed:', '']
    for i, item in enumerate(notice['hayes_side_changes_needed'], 1):
        L.append(f"{i}. {item}")
    L += ['']
    L += ['## The pin', '',
          f"Cite this commit: {pin['publication_commit']}", '',
          f"- Authority id: {pin['authority_id']}",
          f"- Version: {pin['version']}",
          f"- Authority sha256: {pin['authority_sha256']}",
          f"- Publication manifest sha256: {pin['manifest_sha256']}",
          f"- Digest normalisation: {pin['digest_normalisation']} (both digests are computed over bytes with CRLF replaced by LF)",
          f"- Published on: {pin['published_on']}", '',
          f"The commit {pin['publication_record_commit']} records the publication commit in a publication record and changes no authority bytes. Do not cite it as the pin. This notice is dated {notice['notice_date']}; the publication date above is cited separately.", '']
    L += ['## What changed', '',
          f"Version {pin['version']} declares how each input is hashed, one entry per input in source_lineage:", '']
    for e in wc['lineage']:
        L.append(f"- {e['key']}: {e['relative_path']}; normalisation {e['normalisation']}; sha256 {e['sha256']}")
    L += ['',
          'The AA1 manifest is committed and hashed as RAW_BYTES, that is the exact bytes of the file with no CRLF replacement. The AA2 approval and AA2 closure files are hashed the same way.', '',
          f"- The negative-invariant validation records {wc['negative_mutation_count']} mutations, each rejected and failing closed.",
          f"- The authority schema closes {lv['count']} levels with additionalProperties false.",
          f"- {rc['rows_differing']} of {rc['rows_compared']} control rows differ from version {sup['version']} on {', '.join(rc['compared_keys'])}.",
          f"- {wc['gate_fix_line']}", '']
    L += ['## The 2.0.1 digest-scope error', '',
          f"Version {ds['previous_version']} at commit {ds['previous_commit']} declared one global digest scope, {ds['previous_declared_normalisation']}, for its source lineage. Version {pin['version']} declares the scope per digest. Three digests were declared under the wrong scope: {', '.join(d['previous_key'] for d in ds['digests'])}. Their files are hashed as RAW_BYTES.", '',
          'The digest values are the same in both versions. Only the declared scope changed.', '']
    for d in ds['digests']:
        L.append(f"- {d['previous_key']} is now {d['key']}: declared scope {d['previous_declared_scope']} became {d['declared_scope']}; sha256 {d['sha256']}")
    L += ['']
    L += ['## No decision changed', '',
          f"{dec['decided_count']} controls are decided: {dec['rule_count']} with a published rule and {dec['no_rule_count']} with no rule. The other {dec['not_yet_decided_count']} stay NOT_YET_DECIDED. The three rules, in machine form:", '']
    for r in dec['rules']:
        L.append(f"- {r['control_id']} ({r['authority']}): {r['machine_form']}")
    L += ['',
          'If any field named by a rule is UNKNOWN, the result is APPLICABILITY_UNRESOLVED. UNKNOWN never resolves to not applicable.', '',
          f"The governance decisions file has the same LF sha256 as at version {sup['version']}: {dec['governance_decisions_sha256']}.", '',
          'The reasons for the no-rule decisions are in docs/DEMO3_W1_REQ_001_REPLY.md and registry/archive_assessment_governance_decisions.json. They are not repeated here.', '']
    L += ['## Sending', '', notice['send_condition'], '']
    text = '\n'.join(L)
    if '\r' in text:
        raise V2.AuthorityError('rendered text contains a carriage return')
    return text


def schema() -> dict:
    cond = {'type': 'object', 'additionalProperties': False, 'required': ['field', 'state'], 'properties': {'field': {'enum': list(V2.RULE_FIELDS)}, 'state': {'enum': list(V2.CONDITION_STATES)}}}
    rule = {'type': 'object', 'additionalProperties': False, 'required': ['combination', 'conditions'], 'properties': {'combination': {'const': V2.COMBINATION}, 'conditions': {'type': 'array', 'minItems': 1, 'maxItems': len(V2.RULE_FIELDS), 'items': cond}}}
    s = {'type': 'string', 'minLength': 1}
    sha = {'type': 'string', 'pattern': DIGEST_RE}
    commit = {'type': 'string', 'pattern': SHA_RE}

    def obj(props: dict) -> dict:
        return {'type': 'object', 'additionalProperties': False, 'required': list(props), 'properties': props}

    lineage = obj({'key': s, 'relative_path': s, 'normalisation': {'enum': list(NORMALISATIONS)}, 'sha256': sha})
    digest = obj({'previous_key': {'enum': [p for p, _ in DIGEST_SCOPE_PAIRS]}, 'key': {'enum': [n for _, n in DIGEST_SCOPE_PAIRS]}, 'sha256': sha, 'previous_declared_scope': {'const': 'CRLF_TO_LF'}, 'declared_scope': {'const': 'RAW_BYTES'}})
    return {'$schema': 'https://json-schema.org/draft/2020-12/schema', 'title': 'EMS notice to Hayes Verify for request DEMO3-W1-REQ-001, authority 2.0.2', 'type': 'object', 'additionalProperties': False, 'required': list(NOTICE_KEYS),
        'properties': {
            'document_id': {'const': DOCUMENT_ID}, 'request_id': {'const': REQUEST_ID}, 'request_label': {'const': REQUEST_LABEL}, 'notice_date': {'type': 'string', 'pattern': DATE_RE},
            'from_authority': obj({'approver': s, 'role': {'enum': list(V2.APPROVER_ROLES)}, 'roles': {'type': 'array', 'items': {'enum': list(V2.APPROVER_ROLES)}}}),
            'dual_role_statement': s,
            'pin': obj({'publication_commit': {'const': NOTICE_PUBLICATION_COMMIT}, 'authority_id': {'const': NOTICE_AUTHORITY_ID}, 'version': {'const': NOTICE_VERSION}, 'authority_sha256': sha, 'manifest_sha256': sha, 'digest_normalisation': {'const': 'CRLF_TO_LF'}, 'publication_record_commit': commit, 'published_on': {'type': 'string', 'pattern': DATE_RE}}),
            'supersedes': obj({'authority_id': {'const': SUPERSEDED_AUTHORITY_ID}, 'version': {'const': SUPERSEDED_VERSION}, 'commit': {'const': SUPERSEDED_COMMIT}}),
            'what_changed': obj({'lineage': {'type': 'array', 'minItems': 7, 'maxItems': 7, 'items': lineage}, 'negative_mutation_count': {'const': 29}, 'closed_schema_levels': obj({'count': {'const': 16}, 'paths': {'type': 'array', 'minItems': 16, 'maxItems': 16, 'items': s}}), 'row_comparison': obj({'rows_compared': {'const': 80}, 'rows_differing': {'const': 0}, 'compared_keys': {'type': 'array', 'items': s}}), 'gate_fix_line': s}),
            'digest_scope_error': obj({'previous_version': {'const': SUPERSEDED_VERSION}, 'previous_commit': {'const': SUPERSEDED_COMMIT}, 'previous_declared_normalisation': {'const': 'CRLF_TO_LF'}, 'digests': {'type': 'array', 'minItems': 3, 'maxItems': 3, 'items': digest}, 'digest_values_changed': {'const': False}}),
            'decisions': obj({'decided_count': {'const': 21}, 'rule_count': {'const': 3}, 'no_rule_count': {'const': 18}, 'not_yet_decided_count': {'const': 59}, 'rules': {'type': 'array', 'minItems': 3, 'maxItems': 3, 'items': obj({'control_id': {'type': 'string', 'pattern': '^EMS-CTRL-[0-9]{3}$'}, 'authority': {'type': 'string', 'pattern': V2.AUTHORITY_ID_RE}, 'rule': rule, 'machine_form': s})}, 'governance_decisions_sha256': sha, 'decisions_changed': {'const': False}}),
            'hayes_side_changes_needed': {'type': 'array', 'minItems': 3, 'maxItems': 3, 'items': s},
            'send_condition': s}}


def validate_notice_object(notice: dict, inputs: tuple | None = None) -> None:
    jsonschema.Draft202012Validator(schema()).validate(notice)
    if V2.contains_absolute(notice):
        raise V2.AuthorityError('notice contains an absolute path')
    if notice['dual_role_statement'] != V2.DUAL_ROLE_STATEMENT:
        raise V2.AuthorityError('dual role statement differs from the published statement')
    text = render_markdown(notice) + V2.jtext(notice)
    for word in FORBIDDEN_WORDS:
        if re.search(rf'\b{word}\b', text, re.IGNORECASE):
            raise V2.AuthorityError(f'notice uses the word {word}')
    if build_notice(*(inputs or load_inputs())) != notice:
        raise V2.AuthorityError('notice differs from the values derived from the frozen inputs')


def validate_notice() -> None:
    for p in (NOTICE_JSON, NOTICE_MD, NOTICE_SCHEMA):
        if not p.exists():
            raise V2.AuthorityError(f'{V2.rel(p) if p.is_relative_to(V2.ROOT) else p.name}: not generated')
    inputs = load_inputs()
    notice = build_notice(*inputs)
    if V2.lf_bytes(NOTICE_JSON.read_bytes()) != V2.jtext(notice).encode('utf-8'):
        raise V2.AuthorityError('notice JSON differs from a fresh build')
    if V2.lf_bytes(NOTICE_MD.read_bytes()) != render_markdown(notice).encode('utf-8'):
        raise V2.AuthorityError('notice Markdown differs from a fresh build')
    if V2.lf_bytes(NOTICE_SCHEMA.read_bytes()) != V2.jtext(schema()).encode('utf-8'):
        raise V2.AuthorityError('notice schema differs from a fresh build')
    validate_notice_object(V2.load(NOTICE_JSON), inputs)
    jsonschema.Draft202012Validator(V2.load(NOTICE_SCHEMA)).validate(V2.load(NOTICE_JSON))
    print('PASS')


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--build', action='store_true'); group.add_argument('--validate', action='store_true'); group.add_argument('--emit-schema', action='store_true')
    args = parser.parse_args()
    if args.emit_schema: V2.dump(NOTICE_SCHEMA, schema())
    elif args.build:
        inputs = load_inputs()
        notice = build_notice(*inputs)
        validate_notice_object(notice, inputs)
        V2.dump(NOTICE_JSON, notice); V2.write_text(NOTICE_MD, render_markdown(notice))
    elif args.validate: validate_notice()


if __name__ == '__main__': main()

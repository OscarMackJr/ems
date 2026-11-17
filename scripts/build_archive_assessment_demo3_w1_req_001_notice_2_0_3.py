from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
import tempfile
from datetime import date
from pathlib import Path
from types import SimpleNamespace

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / 'registry'
SCHEMAS = ROOT / 'schemas'

# Frozen copies of the 2.0.3 publisher values at NOTICE_PUBLICATION_COMMIT (1544dc1); a test proves each one against that blob.
AUTHORITY = REGISTRY / 'archive_assessment_applicability_authority_v2.json'
SCHEMA = SCHEMAS / 'archive_assessment_applicability_authority_v2.schema.json'
GOVERNANCE_DECISIONS = REGISTRY / 'archive_assessment_governance_decisions.json'
REQUEST_CONTROL_IDS = [f'EMS-CTRL-{n:03d}' for n in (9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22, 30, 33, 39, 42, 52, 62, 75, 79)]
PREV_COMPARED_KEYS = ('not_applicable_decision_state', 'not_applicable_rule', 'not_applicable_authority', 'decision_ids')
RULE_FIELDS = ['production', 'internet_exposed', 'contains_customer_data', 'ai_enabled']
CONDITION_STATES = ['KNOWN_TRUE', 'KNOWN_FALSE']
COMBINATION = 'ALL_CONDITIONS_MUST_MATCH'
AUTHORITY_ID_RE = r'^AA4-GOV-[0-9]{3}$'
OUT = ROOT / 'generated' / 'archive-assessment' / 'ems-aa3-v2'
SIGNOFF = REGISTRY / 'archive_assessment_applicability_authority_v2_signoff.json'
PUBLICATION_RECORD = REGISTRY / 'archive_assessment_applicability_authority_v2_publication_record.json'
APPROVER = 'Oscar Mack'
APPROVER_ROLES = ['EMS_GOVERNANCE_AUTHORITY', 'HAYES_VERIFY_DEVELOPER']
SIGNOFF_ROLE = 'EMS_GOVERNANCE_AUTHORITY'
DUAL_ROLE_STATEMENT = 'Oscar Mack made this decision as the EMS governance authority and is also the developer of Hayes Verify, the assessor that will read it.'
N_NEGATIVE = 'archive_assessment_applicability_authority_v2_negative_invariant_validation.json'
N_TRACE = 'archive_assessment_applicability_authority_v2_decision_traceability.json'
N_MANIFEST = 'ems_aa3_v2_archive_applicability_authority_publication_manifest.json'

NOTICE_JSON = ROOT / 'registry' / 'archive_assessment_demo3_w1_req_001_notice_2_0_3.json'
NOTICE_MD = ROOT / 'docs' / 'DEMO3_W1_REQ_001_NOTICE_2_0_3.md'
NOTICE_SCHEMA = ROOT / 'schemas' / 'archive_assessment_demo3_w1_req_001_notice_2_0_3.schema.json'
NOTICE_PUBLICATION_COMMIT = '1544dc19ba235d732c832d1651895550ed5a265d'
NOTICE_RECORD_COMMIT = '87a46d147413bd99e931c71a1ab165eb0903f014'
PREVIOUS_2_0_2_COMMIT = 'ae15c7458e49c8f55cc58c61bab04bc716aa9892'
PREVIOUS_2_0_1_COMMIT = '31addfa95ffc5c2d6805c73fa1f34d6ccbe313eb'
CATALOG_COMMIT = '62a8955dc28d9458cd1167fad314926e057c31fc'
NOTICE_AUTHORITY_ID = 'EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.3'
NOTICE_VERSION = '2.0.3'
PREVIOUS_2_0_2_AUTHORITY_ID = 'EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.2'
PREVIOUS_2_0_2_VERSION = '2.0.2'
PREVIOUS_2_0_1_AUTHORITY_ID = 'EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.1'
PREVIOUS_2_0_1_VERSION = '2.0.1'
REQUEST_ID = 'DEMO3-W1-REQ-001'
REQUEST_LABEL = 'EMSREQ-APPLIC-RULES'
DOCUMENT_ID = 'EMS-DEMO3-W1-REQ-001-NOTICE-2.0.3'
SCRIPT_REL = 'scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py'
REMOTE_BRANCH = 'feature/ems-aa3-archive-applicability-authority'
REPOSITORY_URL = 'https://github.com/OscarMackJr/ems.git'
INSTALL_COMMAND = 'python -m pip install -r requirements.txt jsonschema==4.26.0'
NOTICE_DATE = '2026-11-17'
DIGEST_RE = r'^[0-9a-f]{64}$'
SHA_RE = r'^[0-9a-f]{40}$'
DATE_RE = r'^[0-9]{4}-[0-9]{2}-[0-9]{2}$'
NORMALISATIONS = ['RAW_BYTES', 'CRLF_TO_LF']
FORBIDDEN_WORDS = ('best', 'critical', 'important', 'recommended', 'highest')
EXPECTED_COUNTS = {'decided_count': 21, 'rule_count': 3, 'no_rule_count': 18, 'not_yet_decided_count': 59}
EXPECTED_MUTATION_RESULT = 'REJECTED_FAIL_CLOSED'
LINEAGE_NORMALISATION = {'aa1_manifest': 'RAW_BYTES', 'aa2_approval': 'RAW_BYTES', 'aa2_closure': 'RAW_BYTES', 'catalog_reference': 'CRLF_TO_LF', 'governance_decisions': 'CRLF_TO_LF', 'supersedes': 'CRLF_TO_LF', 'v1_baseline': 'CRLF_TO_LF'}
DIGEST_SCOPE_PAIRS = (('aa1_manifest_sha256', 'aa1_manifest'), ('aa2_approval_sha256', 'aa2_approval'), ('aa2_closure_sha256', 'aa2_closure'))
PINNED_CODE = ('scripts/publish_archive_assessment_applicability_authority_v2.py', 'scripts/build_archive_assessment_governance_decisions.py')
PINNED_DATA = ('registry/archive_assessment_governance_decisions.json', 'registry/archive_assessment_applicability_authority.json',
               'registry/archive_assessment_not_applicable_rule_proposals.json', 'registry/archive_assessment_rule_proposals_drafting_record.json',
               'registry/archive_assessment_governance_answers.json', 'registry/archive_assessment_governance_wording_approval.json',
               'schemas/archive_assessment_governance_decisions.schema.json')


class AuthorityError(ValueError): pass
class GitHistoryError(AuthorityError): pass

def lf_bytes(b: bytes) -> bytes: return b.replace(b'\r\n', b'\n')
def identity(b: bytes) -> bytes: return b
NORMALISERS = {'RAW_BYTES': identity, 'CRLF_TO_LF': lf_bytes}
def load(p: Path) -> dict: return json.loads(p.read_text(encoding='utf-8'))
def dump(p: Path, value: object) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, 'w', encoding='utf-8', newline='\n') as f: f.write(json.dumps(value, indent=2, sort_keys=True) + '\n')
def write_text(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, 'w', encoding='utf-8', newline='\n') as f: f.write(text)
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

def closed_schema_levels(node: object, path: str = '$') -> list:
    out = []
    if isinstance(node, dict):
        if node.get('additionalProperties') is False: out.append(path)
        for k, v in node.items(): out += closed_schema_levels(v, f'{path}.{k}')
    elif isinstance(node, list):
        for i, v in enumerate(node): out += closed_schema_levels(v, f'{path}[{i}]')
    return out

def is_date(value: object) -> bool:
    if not isinstance(value, str) or not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', value): return False
    try: date.fromisoformat(value)
    except ValueError: return False
    return True

def validate_signoff(record: object, authority_lf_digest: str, authority_id: str | None = None, version: str | None = None) -> None:
    errors = []
    want_id = NOTICE_AUTHORITY_ID if authority_id is None else authority_id; want_version = NOTICE_VERSION if version is None else version
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


def pinned_bytes(commit: str, path: Path) -> bytes:
    return git_show(commit, rel(path))


def pinned_json(commit: str, path: Path) -> dict:
    return json.loads(pinned_bytes(commit, path).decode('utf-8'))


def pinned_digest(commit: str, path: Path) -> str:
    return hashlib.sha256(lf_bytes(pinned_bytes(commit, path))).hexdigest()


def pinned_raw_digest(commit: str, path: Path | str) -> str:
    relative = rel(path) if isinstance(path, Path) else path
    return hashlib.sha256(git_show(commit, relative)).hexdigest()


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(['git', *args], cwd=ROOT, capture_output=True, text=True)


def resolve_record_commit() -> str:
    try:
        s = git('rev-parse', '--is-shallow-repository')
    except OSError as e:
        raise AuthorityError(f'cannot check whether the clone is shallow: {e}') from e
    if s.returncode != 0 or s.stdout.strip() != 'false':
        raise AuthorityError('shallow clone or unreadable repository: cannot resolve the frozen commits; fetch full history')
    for sha in (NOTICE_PUBLICATION_COMMIT, NOTICE_RECORD_COMMIT, PREVIOUS_2_0_2_COMMIT, PREVIOUS_2_0_1_COMMIT):
        if not re.fullmatch(r'[0-9a-f]{40}', sha) or git('cat-file', '-e', f'{sha}^{{commit}}').returncode != 0:
            raise AuthorityError(f'the frozen commit {sha} is not in the repository history; fetch full history (git fetch --unshallow)')
        if git('merge-base', '--is-ancestor', sha, 'HEAD').returncode != 0:
            raise AuthorityError(f'the frozen commit {sha} is not an ancestor of HEAD')
    if git('merge-base', '--is-ancestor', NOTICE_PUBLICATION_COMMIT, NOTICE_RECORD_COMMIT).returncode != 0:
        raise AuthorityError('the publication commit is not an ancestor of the record commit')
    return NOTICE_RECORD_COMMIT


def check_inputs_bound(manifest: dict) -> None:
    man = {a['relative_path']: a['sha256'] for a in manifest['artifacts']}
    for path in (SIGNOFF, SCHEMA, AUTHORITY, OUT / N_NEGATIVE, OUT / N_TRACE):
        if man.get(rel(path)) != pinned_digest(NOTICE_PUBLICATION_COMMIT, path):
            raise AuthorityError(f'{rel(path)} differs from the published manifest')
    trace = pinned_json(NOTICE_PUBLICATION_COMMIT, OUT / N_TRACE)
    doc_sha = pinned_digest(NOTICE_PUBLICATION_COMMIT, GOVERNANCE_DECISIONS)
    if not trace['decision_records'] or any(r['decision_record_sha256'] != doc_sha for r in trace['decision_records']):
        raise AuthorityError('decision records differ from the published traceability')


def check_rerun(rerun_outcomes: list, negative: dict) -> list:
    for o in rerun_outcomes:
        if not o.get('rejected_by') or o.get('result') != EXPECTED_MUTATION_RESULT:
            raise AuthorityError(f"mutation {o.get('id')} was not rejected by the rerun")
    if negative.get('result') != 'PASS':
        raise AuthorityError('the frozen negative-invariant result at the pin is not PASS')
    proj = lambda xs: [(x['id'], list(x['rejected_by']), x['result']) for x in xs]
    if proj(rerun_outcomes) != proj(negative['negative_invariant_tests']):
        raise AuthorityError('the mutation rerun differs from the frozen negative-invariant output')
    return [{'id': o['id'], 'rejected_by': list(o['rejected_by'])} for o in rerun_outcomes]


def lineage_entries(authority: dict) -> list:
    lin = authority['source_lineage']
    if sorted(lin) != sorted(LINEAGE_NORMALISATION):
        raise AuthorityError('source_lineage keys differ from the 7 declared inputs')
    out = []
    for key in sorted(lin):
        e = lin[key]
        norm = e.get('normalisation') if isinstance(e, dict) else None
        if norm != LINEAGE_NORMALISATION[key]:
            raise AuthorityError(f'source_lineage {key}: normalisation {norm!r} differs from {LINEAGE_NORMALISATION[key]}')
        at = e.get('commit', NOTICE_PUBLICATION_COMMIT)
        got = hashlib.sha256(NORMALISERS[norm](git_show(at, e['relative_path']))).hexdigest()
        if got != e['sha256']:
            raise AuthorityError(f'source_lineage {key}: recomputed sha256 at {at} differs from the recorded digest')
        out.append({'key': key, 'relative_path': e['relative_path'], 'normalisation': norm, 'sha256': got, 'recomputed_at': at})
    return out


def rows_differing(authority: dict, previous: dict) -> tuple[int, int]:
    rows, prev_rows = {r['control_id']: r for r in authority['controls']}, {r['control_id']: r for r in previous['controls']}
    if set(rows) != set(prev_rows) or authority.get('applicability_decision_ids') != previous.get('applicability_decision_ids'):
        raise AuthorityError('control set or cited decision ids differ from the superseded version')
    return sum(any(rows[c].get(k) != prev_rows[c].get(k) for k in PREV_COMPARED_KEYS) for c in rows), len(rows)


def digest_scope_error(authority: dict, previous_2_0_1: dict) -> dict:
    old, new = previous_2_0_1['source_lineage'], authority['source_lineage']
    if old.get('digest_normalisation') != 'CRLF_TO_LF':
        raise AuthorityError('the 2.0.1 authority does not declare the global CRLF_TO_LF claim')
    digests = []
    for previous_key, key in DIGEST_SCOPE_PAIRS:
        e = new.get(key)
        if not isinstance(e, dict):
            raise AuthorityError(f'{key} is missing from the 2.0.3 source_lineage')
        raw_bytes = git_show(NOTICE_PUBLICATION_COMMIT, e['relative_path'])
        raw, lf = hashlib.sha256(raw_bytes).hexdigest(), hashlib.sha256(lf_bytes(raw_bytes)).hexdigest()
        if raw == lf:
            raise AuthorityError(f'{key}: raw sha256 equals its LF sha256, so the wrong-scope statement cannot be made')
        if e.get('normalisation') != 'RAW_BYTES':
            raise AuthorityError(f'{key} is not declared RAW_BYTES in 2.0.3')
        if raw != e.get('sha256'):
            raise AuthorityError(f'{key}: raw sha256 differs from the 2.0.3 lineage digest')
        if raw != old.get(previous_key):
            raise AuthorityError(f'{previous_key} in 2.0.1 differs from the raw sha256 of {key}')
        digests.append({'key': key, 'previous_key': previous_key, 'relative_path': e['relative_path'], 'raw_sha256': raw, 'lf_sha256': lf, 'previous_declared_scope': 'CRLF_TO_LF', 'declared_scope': 'RAW_BYTES'})
    return {'previous_version': PREVIOUS_2_0_1_VERSION, 'previous_commit': PREVIOUS_2_0_1_COMMIT, 'previous_declared_normalisation': 'CRLF_TO_LF', 'computed_at': NOTICE_PUBLICATION_COMMIT, 'digests': digests, 'digest_values_changed': False}


def load_pinned_publisher(tmp: Path):
    for p in (*PINNED_CODE, *PINNED_DATA):
        if bad_rel(p): raise AuthorityError(f'{p}: path must be repo-relative without ..')
        dest = tmp / p
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(git_show(NOTICE_PUBLICATION_COMMIT, p))
    spec = importlib.util.spec_from_file_location('aa_pinned_publisher_2_0_3', tmp / PINNED_CODE[0])
    pub = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pub)
    b = pub.decisions_builder()
    # Pinned ROOT stays inside tmp, so no pinned ROOT read can reach a live file; only git processes run in the live repository.
    for name, module in (('ROOT', pub), ('builder ROOT', b), ('builder V2 ROOT', b.V2)):
        if not Path(module.ROOT).resolve().is_relative_to(tmp.resolve()):
            raise AuthorityError(f'pinned code resolved {name} outside the pinned materialisation')
    for module in (pub, b.V2):
        module.subprocess = live_git_subprocess()
    return pub


def live_git_subprocess() -> SimpleNamespace:
    def run(cmd, *args, **kwargs):
        if not isinstance(cmd, (list, tuple)) or not cmd or cmd[0] != 'git':
            raise AuthorityError(f'pinned code started a process that is not git: {cmd!r}')
        kwargs['cwd'] = ROOT
        return subprocess.run(cmd, *args, **kwargs)
    return SimpleNamespace(run=run, CompletedProcess=subprocess.CompletedProcess)


_WRAPPED = (ValueError, OSError, KeyError, TypeError, AttributeError, ImportError, jsonschema.ValidationError, jsonschema.SchemaError)


def pinned_mutation_run(authority: dict, signoff: dict, decisions: dict, manifest: dict) -> dict:
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        try:
            pub = load_pinned_publisher(tmp)
        except AuthorityError: raise
        except _WRAPPED as e:
            cls = GitHistoryError if type(e).__name__ == 'GitHistoryError' else AuthorityError
            raise cls(f'pinned mutation run failed: {type(e).__name__}: {e}') from e
        publisher_bytes = (tmp / PINNED_CODE[0]).read_bytes()
        if hashlib.sha256(lf_bytes(publisher_bytes)).hexdigest() != manifest['publisher_script']['sha256']:
            raise AuthorityError('pinned publisher differs from the certified publisher_script digest')
        if pub.VERSION != NOTICE_VERSION:
            raise AuthorityError('pinned publisher is not the 2.0.3 publisher')
        if 'run --validate --at-pin here' not in publisher_bytes.decode('utf-8'):
            raise AuthorityError('pinned publisher does not point plain --validate at the pin to --at-pin')
        if not str(pub.AT_PIN_DEFERRED).startswith('PUBLICATION_RECORD_BINDING: '):
            raise AuthorityError('pinned publisher AT_PIN_DEFERRED does not start with PUBLICATION_RECORD_BINDING')
        try:
            # non-vacuity: the unmutated inputs must pass every gate the mutations are judged by
            pub.validate_governance_decisions()
            pub.validate_publication(authority)
            jsonschema.Draft202012Validator(pub.schema()).validate(authority)
            pub.validate_signoff(signoff, pub.sha_text(pub.jtext(authority)))
        except AuthorityError: raise
        except _WRAPPED as e:
            if type(e).__name__ == 'GitHistoryError': raise GitHistoryError(str(e)) from e
            raise AuthorityError(f'pinned baseline rejected the unmutated inputs: {type(e).__name__}: {e}') from e
        try:
            outcomes = pub.run_mutations(authority, signoff, decisions)
        except AuthorityError: raise
        except _WRAPPED as e:
            cls = GitHistoryError if type(e).__name__ == 'GitHistoryError' else AuthorityError
            raise cls(f'pinned mutation run failed: {type(e).__name__}: {e}') from e
        b = pub._BUILDER
        names = {'ROOT': pub.ROOT, 'builder ROOT': b.ROOT, 'builder V2 ROOT': b.V2.ROOT, 'GOVERNANCE_DECISIONS': pub.GOVERNANCE_DECISIONS, 'V1_AUTHORITY': pub.V1_AUTHORITY, 'BUILDER_SCRIPT': pub.BUILDER_SCRIPT, 'builder __file__': b.__file__, 'builder V2 __file__': b.V2.__file__, 'PROPOSALS': b.PROPOSALS, 'DRAFTING_RECORD': b.DRAFTING_RECORD, 'ANSWERS': b.ANSWERS, 'WORDING_APPROVAL': b.WORDING_APPROVAL, 'DECISIONS_SCHEMA': b.DECISIONS_SCHEMA}
        for name, path in names.items():
            if not Path(path).resolve().is_relative_to(tmp.resolve()):
                raise AuthorityError(f'pinned code resolved {name} outside the pinned materialisation')
        return {'outcomes': [dict(o) for o in outcomes], 'at_pin_deferred': pub.AT_PIN_DEFERRED}


def load_inputs() -> tuple:
    resolve_record_commit()
    authority = pinned_json(NOTICE_PUBLICATION_COMMIT, AUTHORITY)
    previous_2_0_2 = pinned_json(PREVIOUS_2_0_2_COMMIT, AUTHORITY)
    previous_2_0_1 = pinned_json(PREVIOUS_2_0_1_COMMIT, AUTHORITY)
    signoff = pinned_json(NOTICE_PUBLICATION_COMMIT, SIGNOFF)
    decisions = pinned_json(NOTICE_PUBLICATION_COMMIT, GOVERNANCE_DECISIONS)
    manifest = pinned_json(NOTICE_PUBLICATION_COMMIT, OUT / N_MANIFEST)
    frozen_schema = pinned_json(NOTICE_PUBLICATION_COMMIT, SCHEMA)
    negative = pinned_json(NOTICE_PUBLICATION_COMMIT, OUT / N_NEGATIVE)
    record = pinned_json(NOTICE_RECORD_COMMIT, PUBLICATION_RECORD)
    if record.get('publication_commit') != NOTICE_PUBLICATION_COMMIT:
        raise AuthorityError('NOTICE_PUBLICATION_COMMIT differs from the publication_commit named by the frozen publication record')
    if record['manifest_sha256'] != pinned_digest(NOTICE_PUBLICATION_COMMIT, OUT / N_MANIFEST):
        raise AuthorityError('publication record manifest digest differs from the published manifest')
    check_inputs_bound(manifest)
    rerun = pinned_mutation_run(authority, signoff, decisions, manifest)
    return authority, previous_2_0_2, previous_2_0_1, record, signoff, decisions, manifest, frozen_schema, negative, rerun


NOTICE_KEYS = ['document_id', 'request_id', 'request_label', 'notice_date', 'from_authority', 'dual_role_statement', 'pin', 'supersedes', 'what_changed', 'mutations', 'lineage', 'digest_scope_error', 'decisions', 'verify', 'hayes_side_changes_needed', 'send_condition']
PIN_KEYS = ['publication_commit', 'authority_id', 'version', 'authority_sha256', 'manifest_sha256', 'digest_normalisation', 'publication_record_commit', 'published_on']
VERIFICATION_CHANGES_LINE = 'Verification changes in 2.0.3: the publisher adds --validate --at-pin, plain --validate checks that the publication files are byte-identical between the publication commit and HEAD, gates GATE-06 to GATE-10 were added, and the reply and 2.0.2 notice validators are frozen.'
PUBLISHER_CMD = 'python scripts/publish_archive_assessment_applicability_authority_v2.py'


def build_notice(authority: dict, previous_2_0_2: dict, previous_2_0_1: dict, record: dict, signoff: dict, decisions: dict, manifest: dict, frozen_schema: dict, negative: dict, rerun: dict) -> dict:
    if authority['authority_id'] != NOTICE_AUTHORITY_ID or authority['version'] != NOTICE_VERSION:
        raise AuthorityError('frozen authority is not the 2.0.3 authority')
    if record['authority_id'] != authority['authority_id'] or record['version'] != authority['version']:
        raise AuthorityError('publication record does not match the authority')
    if record['authority_sha256'] != pinned_digest(NOTICE_PUBLICATION_COMMIT, AUTHORITY):
        raise AuthorityError('publication record authority digest differs from the published authority')
    validate_signoff(signoff, record['authority_sha256'], authority_id=record['authority_id'], version=record['version'])
    appr = signoff['approval']
    if signoff['dual_role_statement'] != DUAL_ROLE_STATEMENT:
        raise AuthorityError('dual role statement differs from the published statement')
    if manifest.get('published_on') != appr['date']:
        raise AuthorityError('manifest publication date differs from the sign-off date')
    sup = authority['source_lineage']['supersedes']
    if (sup['authority_id'], sup['version'], sup['commit']) != (PREVIOUS_2_0_2_AUTHORITY_ID, PREVIOUS_2_0_2_VERSION, PREVIOUS_2_0_2_COMMIT):
        raise AuthorityError('2.0.3 does not supersede the frozen 2.0.2 commit')
    if previous_2_0_2['authority_id'] != sup['authority_id'] or previous_2_0_2['version'] != sup['version'] or pinned_digest(PREVIOUS_2_0_2_COMMIT, AUTHORITY) != sup['sha256']:
        raise AuthorityError('the authority frozen at the 2.0.2 commit differs from the supersedes entry')
    prev_sup = previous_2_0_2['source_lineage']['supersedes']
    if (prev_sup['authority_id'], prev_sup['version'], prev_sup['commit']) != (PREVIOUS_2_0_1_AUTHORITY_ID, PREVIOUS_2_0_1_VERSION, PREVIOUS_2_0_1_COMMIT):
        raise AuthorityError('2.0.2 does not supersede the frozen 2.0.1 commit')
    if previous_2_0_1['authority_id'] != PREVIOUS_2_0_1_AUTHORITY_ID or previous_2_0_1['version'] != PREVIOUS_2_0_1_VERSION:
        raise AuthorityError('the authority frozen at the 2.0.1 commit is not 2.0.1')
    decisions_sha = pinned_digest(NOTICE_PUBLICATION_COMMIT, GOVERNANCE_DECISIONS)
    superseded_decisions_sha = hashlib.sha256(lf_bytes(git_show(PREVIOUS_2_0_2_COMMIT, sup['governance_decisions_relative_path']))).hexdigest()
    if len({decisions_sha, superseded_decisions_sha, sup['governance_decisions_sha256'], previous_2_0_2['source_lineage']['governance_decisions']['sha256'], authority['source_lineage']['governance_decisions']['sha256']}) != 1:
        raise AuthorityError('governance decisions differ from the superseded version, so no-decision-changed cannot be stated')
    rows = authority['controls']
    decided = [r for r in rows if r['not_applicable_decision_state'] != 'NOT_YET_DECIDED']
    if sorted(r['control_id'] for r in decided) != sorted(REQUEST_CONTROL_IDS):
        raise AuthorityError('decided control set differs from the 21 requested controls')
    rule_rows = sorted((r for r in decided if r['not_applicable_decision_state'] == 'RULE_PUBLISHED'), key=lambda r: r['control_id'])
    counts = {'decided_count': len(decided), 'rule_count': len(rule_rows), 'no_rule_count': sum(r['not_applicable_decision_state'] == 'NO_RULE_WILL_BE_PUBLISHED' for r in decided), 'not_yet_decided_count': len(rows) - len(decided)}
    if counts != EXPECTED_COUNTS or any(r['not_applicable_rule'] is None for r in rule_rows):
        raise AuthorityError('decision counts differ from 21 decided, 3 rules, 18 no-rule and 59 undecided')
    differing, total = rows_differing(authority, previous_2_0_2)
    if differing:
        raise AuthorityError(f'{differing} of {total} control rows differ from the superseded version, so no-decision-changed cannot be stated')
    levels = closed_schema_levels(frozen_schema)
    mutations = check_rerun(rerun['outcomes'], negative)
    pub, p202, p201, rec = record['publication_commit'], PREVIOUS_2_0_2_COMMIT, PREVIOUS_2_0_1_COMMIT, NOTICE_RECORD_COMMIT
    deferred = rerun['at_pin_deferred']
    return {
        'document_id': DOCUMENT_ID, 'request_id': REQUEST_ID, 'request_label': REQUEST_LABEL, 'notice_date': NOTICE_DATE,
        'from_authority': {'approver': appr['approver'], 'role': appr['role'], 'roles': list(APPROVER_ROLES)},
        'dual_role_statement': signoff['dual_role_statement'],
        'pin': {'publication_commit': pub, 'authority_id': record['authority_id'], 'version': record['version'], 'authority_sha256': record['authority_sha256'], 'manifest_sha256': record['manifest_sha256'], 'digest_normalisation': record['digest_normalisation'], 'publication_record_commit': rec, 'published_on': appr['date']},
        'supersedes': {'authority_id': sup['authority_id'], 'version': sup['version'], 'commit': sup['commit'], 'previous': {'authority_id': prev_sup['authority_id'], 'version': prev_sup['version'], 'commit': prev_sup['commit']}},
        'what_changed': {
            'supersedes_moved': {'from_version': PREVIOUS_2_0_1_VERSION, 'from_commit': p201, 'to_version': PREVIOUS_2_0_2_VERSION, 'to_commit': p202},
            'row_comparison': {'rows_compared': total, 'rows_differing': differing, 'compared_with_version': PREVIOUS_2_0_2_VERSION, 'compared_keys': list(PREV_COMPARED_KEYS)},
            'decisions_digest': {'sha256': superseded_decisions_sha, 'recomputed_at': p202, 'unchanged': True},
            'negative_mutation_count': len(mutations),
            'closed_schema_levels': {'count': len(levels), 'paths': levels},
            'verification_changes_line': VERIFICATION_CHANGES_LINE},
        'mutations': mutations,
        'lineage': lineage_entries(authority),
        'digest_scope_error': digest_scope_error(authority, previous_2_0_1),
        'decisions': {**counts, 'rules': [{'control_id': r['control_id'], 'authority': r['not_applicable_authority'], 'rule': r['not_applicable_rule'], 'machine_form': rule_text(r['not_applicable_rule'])} for r in rule_rows], 'governance_decisions_sha256': decisions_sha, 'decisions_changed': False,
                      'no_rule_reasons_pointer': 'The reasons for the 18 no-rule decisions are in docs/DEMO3_W1_REQ_001_REPLY.md and registry/archive_assessment_governance_decisions.json.'},
        'verify': {
            'repository_url': REPOSITORY_URL,
            'prerequisites': ['Python 3.12', INSTALL_COMMAND, 'A full clone (not shallow); run git fetch --unshallow if needed', 'No local edits to the pinned paths'],
            'steps': [
                {'step': 1, 'checkout': pub, 'commands': ['git clone ' + REPOSITORY_URL, 'cd ems', 'git checkout ' + pub, INSTALL_COMMAND, PUBLISHER_CMD + ' --validate --at-pin'],
                 'pass_means': 'One JSON object with status PASS and mode AT_PIN, with exactly one deferred item. The pinned bytes are certified.'},
                {'step': 2, 'checkout': rec, 'commands': ['git checkout ' + rec, PUBLISHER_CMD + ' --validate'],
                 'pass_means': f'PASS means the publication record at this commit names {pub} and the publication files are byte-identical between the two commits. It also passes at any later commit on {REMOTE_BRANCH}.'},
                {'step': 3, 'checkout': REMOTE_BRANCH, 'commands': ['git checkout ' + REMOTE_BRANCH, 'python ' + SCRIPT_REL + ' --validate'],
                 'pass_means': f'Run this at or after the commit that adds this notice. PASS means the builder rebuilt the notice, reran the {len(mutations)} mutations from the pinned publisher and recomputed the digests, and all of them match the committed notice.'}],
            'outcomes': [
                {'case': 'Step 1 prints PASS with mode AT_PIN and one deferred item', 'meaning': 'The pinned bytes are certified. The deferred item is the publication record binding, which cannot exist inside the pinned commit.', 'action': 'Run step 2.'},
                {'case': f'Step 2 or step 3 prints PASS at {rec} or any later commit', 'meaning': 'The publication record binds the pin and the publication files are unchanged.', 'action': f'Re-pin to {pub}.'},
                {'case': 'Plain --validate at the pin fails', 'meaning': 'This failure is by design: the record that binds the pin is added after the pin. The message points to --validate --at-pin.', 'action': 'Run --validate --at-pin at the pin.'},
                {'case': 'Any other failure, including a shallow clone', 'meaning': 'The check did not complete as described.', 'action': 'Do not consume the authority. Report the output to EMS.'}],
            'at_pin_deferred': deferred},
        'hayes_side_changes_needed': [
            f'Re-pin to {pub}. It replaces {p202} (2.0.2) and {p201} (2.0.1); if Hayes pins either, move straight to {pub}.',
            'The target description must carry the eight classification facts.',
            'Hayes must read the published v2 shape.'],
        'send_condition': f'Do not send this notice until the commit that adds it is on the remote branch {REMOTE_BRANCH}.',
    }


def render_markdown(notice: dict) -> str:
    pin, sup, wc, ds, dec, ver = notice['pin'], notice['supersedes'], notice['what_changed'], notice['digest_scope_error'], notice['decisions'], notice['verify']
    rc, lv, mv, dd = wc['row_comparison'], wc['closed_schema_levels'], wc['supersedes_moved'], wc['decisions_digest']
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
    L += ['## How to verify', '', f"Repository: {ver['repository_url']}", '', 'Prerequisites:', '']
    for p in ver['prerequisites']:
        L.append(f"- {p}")
    L += ['']
    for s in ver['steps']:
        L += [f"{s['step']}. Check out {s['checkout']} and run:", '']
        for c in s['commands']:
            L.append(f"        {c}")
        L += ['', f"   {s['pass_means']}", '']
    L += ['| Result | Meaning | Action |', '| --- | --- | --- |']
    for o in ver['outcomes']:
        L.append(f"| {o['case']} | {o['meaning']} | {o['action']} |")
    L += ['', 'The deferred item printed at the pin reads:', '', f"> {ver['at_pin_deferred']}", '']
    L += ['## What changed in 2.0.3', '',
          f"- The supersedes entry moved from version {mv['from_version']} at {mv['from_commit']} to version {mv['to_version']} at {mv['to_commit']}.",
          f"- {rc['rows_differing']} of {rc['rows_compared']} control rows differ from version {rc['compared_with_version']} on {', '.join(rc['compared_keys'])}.",
          f"- The governance decisions digest is unchanged: {dd['sha256']}, recomputed at {dd['recomputed_at']}.",
          f"- {wc['negative_mutation_count']} negative mutations: each was run by this builder from the publisher at the pin and rejected; the list with the gate that rejected each is in registry/archive_assessment_demo3_w1_req_001_notice_2_0_3.json under mutations.",
          f"- The authority schema closes {lv['count']} levels with additionalProperties false.",
          f"- {wc['verification_changes_line']}", '']
    L += ['## Lineage digests recomputed from git', '']
    for e in notice['lineage']:
        L.append(f"- {e['key']}: {e['relative_path']}; normalisation {e['normalisation']}; sha256 {e['sha256']}; recomputed at {e['recomputed_at']}")
    L += ['']
    L += ['## The 2.0.1 digest-scope error', '',
          f"Version {ds['previous_version']} at commit {ds['previous_commit']} declared one global digest scope, {ds['previous_declared_normalisation']}, for its source lineage. Three files were hashed over their raw bytes instead. For each, the raw sha256 and the LF sha256 differ, so the digest recorded in {ds['previous_version']} (the raw one) was not a {ds['previous_declared_normalisation']} digest. Version {pin['version']} declares RAW_BYTES for each of the three. The digest values are unchanged.", '']
    for d in ds['digests']:
        L.append(f"- {d['key']} ({d['relative_path']}): raw sha256 {d['raw_sha256']}; LF sha256 {d['lf_sha256']}; declared scope {d['previous_declared_scope']} became {d['declared_scope']}")
    L += ['']
    L += ['## No decision changed', '',
          f"{dec['decided_count']} controls are decided: {dec['rule_count']} with a published rule and {dec['no_rule_count']} with no rule. The other {dec['not_yet_decided_count']} stay NOT_YET_DECIDED. The three rules, in machine form:", '']
    for r in dec['rules']:
        L.append(f"- {r['control_id']} ({r['authority']}): {r['machine_form']}")
    L += ['',
          'If any field named by a rule is UNKNOWN, the result is APPLICABILITY_UNRESOLVED. UNKNOWN never resolves to not applicable.', '',
          f"The governance decisions file has the same LF sha256 as at version {sup['version']}: {dec['governance_decisions_sha256']}.", '',
          dec['no_rule_reasons_pointer'], '']
    L += ['## Sending', '', notice['send_condition'], '']
    text = '\n'.join(L)
    if '\r' in text:
        raise AuthorityError('rendered text contains a carriage return')
    return text


def schema() -> dict:
    cond = {'type': 'object', 'additionalProperties': False, 'required': ['field', 'state'], 'properties': {'field': {'enum': list(RULE_FIELDS)}, 'state': {'enum': list(CONDITION_STATES)}}}
    rule = {'type': 'object', 'additionalProperties': False, 'required': ['combination', 'conditions'], 'properties': {'combination': {'const': COMBINATION}, 'conditions': {'type': 'array', 'minItems': 1, 'maxItems': len(RULE_FIELDS), 'items': cond}}}
    s = {'type': 'string', 'minLength': 1}
    sha = {'type': 'string', 'pattern': DIGEST_RE}
    commit = {'type': 'string', 'pattern': SHA_RE}

    def obj(props: dict) -> dict:
        return {'type': 'object', 'additionalProperties': False, 'required': list(props), 'properties': props}

    def strings(n: int | None = None) -> dict:
        a = {'type': 'array', 'items': s}
        if n is not None: a.update({'minItems': n, 'maxItems': n})
        return a

    mutation = obj({'id': s, 'rejected_by': {'type': 'array', 'minItems': 1, 'items': {'enum': ['PYTHON_VALIDATOR', 'SCHEMA']}}})
    lineage = obj({'key': {'enum': sorted(LINEAGE_NORMALISATION)}, 'relative_path': s, 'normalisation': {'enum': list(NORMALISATIONS)}, 'sha256': sha, 'recomputed_at': commit})
    digest = obj({'key': {'enum': [n for _, n in DIGEST_SCOPE_PAIRS]}, 'previous_key': {'enum': [p for p, _ in DIGEST_SCOPE_PAIRS]}, 'relative_path': s, 'raw_sha256': sha, 'lf_sha256': sha, 'previous_declared_scope': {'const': 'CRLF_TO_LF'}, 'declared_scope': {'const': 'RAW_BYTES'}})
    step = obj({'step': {'type': 'integer', 'minimum': 1, 'maximum': 3}, 'checkout': s, 'commands': {'type': 'array', 'minItems': 1, 'items': s}, 'pass_means': s})
    outcome = obj({'case': s, 'meaning': s, 'action': s})
    return {'$schema': 'https://json-schema.org/draft/2020-12/schema', 'title': 'EMS DEMO3-W1-REQ-001 notice to Hayes Verify, authority 2.0.3', 'type': 'object', 'additionalProperties': False, 'required': list(NOTICE_KEYS),
        'properties': {
            'document_id': {'const': DOCUMENT_ID}, 'request_id': {'const': REQUEST_ID}, 'request_label': {'const': REQUEST_LABEL}, 'notice_date': {'const': NOTICE_DATE},
            'from_authority': obj({'approver': s, 'role': {'enum': list(APPROVER_ROLES)}, 'roles': {'type': 'array', 'items': {'enum': list(APPROVER_ROLES)}}}),
            'dual_role_statement': s,
            'pin': obj({'publication_commit': {'const': NOTICE_PUBLICATION_COMMIT}, 'authority_id': {'const': NOTICE_AUTHORITY_ID}, 'version': {'const': NOTICE_VERSION}, 'authority_sha256': sha, 'manifest_sha256': sha, 'digest_normalisation': {'const': 'CRLF_TO_LF'}, 'publication_record_commit': {'const': NOTICE_RECORD_COMMIT}, 'published_on': {'type': 'string', 'pattern': DATE_RE}}),
            'supersedes': obj({'authority_id': {'const': PREVIOUS_2_0_2_AUTHORITY_ID}, 'version': {'const': PREVIOUS_2_0_2_VERSION}, 'commit': {'const': PREVIOUS_2_0_2_COMMIT},
                               'previous': obj({'authority_id': {'const': PREVIOUS_2_0_1_AUTHORITY_ID}, 'version': {'const': PREVIOUS_2_0_1_VERSION}, 'commit': {'const': PREVIOUS_2_0_1_COMMIT}})}),
            'what_changed': obj({
                'supersedes_moved': obj({'from_version': {'const': PREVIOUS_2_0_1_VERSION}, 'from_commit': {'const': PREVIOUS_2_0_1_COMMIT}, 'to_version': {'const': PREVIOUS_2_0_2_VERSION}, 'to_commit': {'const': PREVIOUS_2_0_2_COMMIT}}),
                'row_comparison': obj({'rows_compared': {'const': 80}, 'rows_differing': {'const': 0}, 'compared_with_version': {'const': PREVIOUS_2_0_2_VERSION}, 'compared_keys': strings()}),
                'decisions_digest': obj({'sha256': sha, 'recomputed_at': commit, 'unchanged': {'const': True}}),
                'negative_mutation_count': {'const': 29},
                'closed_schema_levels': obj({'count': {'const': 16}, 'paths': {'type': 'array', 'minItems': 16, 'maxItems': 16, 'items': s}}),
                'verification_changes_line': s}),
            'mutations': {'type': 'array', 'minItems': 29, 'maxItems': 29, 'items': mutation},
            'lineage': {'type': 'array', 'minItems': 7, 'maxItems': 7, 'items': lineage},
            'digest_scope_error': obj({'previous_version': {'const': PREVIOUS_2_0_1_VERSION}, 'previous_commit': commit, 'previous_declared_normalisation': {'const': 'CRLF_TO_LF'}, 'computed_at': commit, 'digests': {'type': 'array', 'minItems': 3, 'maxItems': 3, 'items': digest}, 'digest_values_changed': {'const': False}}),
            'decisions': obj({'decided_count': {'const': 21}, 'rule_count': {'const': 3}, 'no_rule_count': {'const': 18}, 'not_yet_decided_count': {'const': 59}, 'rules': {'type': 'array', 'minItems': 3, 'maxItems': 3, 'items': obj({'control_id': {'type': 'string', 'pattern': '^EMS-CTRL-[0-9]{3}$'}, 'authority': {'type': 'string', 'pattern': AUTHORITY_ID_RE}, 'rule': rule, 'machine_form': s})}, 'governance_decisions_sha256': sha, 'decisions_changed': {'const': False}, 'no_rule_reasons_pointer': s}),
            'verify': obj({'repository_url': {'const': REPOSITORY_URL}, 'prerequisites': strings(4), 'steps': {'type': 'array', 'minItems': 3, 'maxItems': 3, 'items': step}, 'outcomes': {'type': 'array', 'minItems': 4, 'maxItems': 4, 'items': outcome}, 'at_pin_deferred': {'type': 'string', 'pattern': '^PUBLICATION_RECORD_BINDING: '}}),
            'hayes_side_changes_needed': strings(3),
            'send_condition': s}}


def validate_notice_object(notice: dict, inputs: tuple | None = None) -> None:
    jsonschema.Draft202012Validator(schema()).validate(notice)
    if contains_absolute(notice):
        raise AuthorityError('notice contains an absolute path')
    if notice['dual_role_statement'] != DUAL_ROLE_STATEMENT:
        raise AuthorityError('dual role statement differs from the published statement')
    text = render_markdown(notice) + jtext(notice)
    for word in FORBIDDEN_WORDS:
        if re.search(rf'\b{word}\b', text, re.IGNORECASE):
            raise AuthorityError(f'notice uses the word {word}')
    if build_notice(*(inputs or load_inputs())) != notice:
        raise AuthorityError('notice differs from the values derived from the frozen inputs')


def validate_notice() -> None:
    for p in (NOTICE_JSON, NOTICE_MD, NOTICE_SCHEMA):
        if not p.exists():
            raise AuthorityError(f'{rel(p) if p.is_relative_to(ROOT) else p.name}: not generated')
    inputs = load_inputs()
    notice = build_notice(*inputs)
    if lf_bytes(NOTICE_JSON.read_bytes()) != jtext(notice).encode('utf-8'):
        raise AuthorityError('notice JSON differs from a fresh build')
    if lf_bytes(NOTICE_MD.read_bytes()) != render_markdown(notice).encode('utf-8'):
        raise AuthorityError('notice Markdown differs from a fresh build')
    if lf_bytes(NOTICE_SCHEMA.read_bytes()) != jtext(schema()).encode('utf-8'):
        raise AuthorityError('notice schema differs from a fresh build')
    validate_notice_object(load(NOTICE_JSON), inputs)
    jsonschema.Draft202012Validator(load(NOTICE_SCHEMA)).validate(load(NOTICE_JSON))
    print('PASS')


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--build', action='store_true'); group.add_argument('--validate', action='store_true'); group.add_argument('--emit-schema', action='store_true')
    args = parser.parse_args()
    if args.emit_schema: dump(NOTICE_SCHEMA, schema())
    elif args.build:
        inputs = load_inputs()
        notice = build_notice(*inputs)
        validate_notice_object(notice, inputs)
        json_text, md_text = jtext(notice), render_markdown(notice)
        write_text(NOTICE_JSON, json_text); write_text(NOTICE_MD, md_text)
        validate_notice()
    elif args.validate: validate_notice()


if __name__ == '__main__': main()

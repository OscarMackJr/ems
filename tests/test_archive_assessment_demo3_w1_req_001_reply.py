import copy
import hashlib
import importlib.util
import json
import re
import subprocess
import tempfile
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / 'scripts' / 'build_archive_assessment_demo3_w1_req_001_reply.py'
SPEC = importlib.util.spec_from_file_location('aa_reply_demo3', SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
V2 = MODULE.V2
AuthorityError = V2.AuthorityError
REJECTS = (AuthorityError, jsonschema.ValidationError)
F = 'KNOWN_FALSE'

REAL_JSON = MODULE.REPLY_JSON
REAL_MD = MODULE.REPLY_MD


def inputs():
    return V2.load(V2.AUTHORITY), V2.load(V2.PUBLICATION_RECORD), V2.load(V2.SIGNOFF), V2.load(V2.GOVERNANCE_DECISIONS), V2.load(V2.OUT / V2.N_MANIFEST)


def build():
    return MODULE.build_reply(*inputs())


def entry(reply, cid):
    return next(c for c in reply['controls'] if c['control_id'] == cid)


def rejected(reply):
    # Rejected by the object validator, or (for drift that stays schema-valid) different from a fresh build,
    # which validate_reply() turns into a failure by byte comparison.
    try:
        MODULE.validate_reply_object(reply)
    except REJECTS:
        return True
    return reply != build()


def test_built_reply_counts():
    r = build()
    assert [c['control_id'] for c in r['controls']] == sorted(MODULE.V2.REQUEST_CONTROL_IDS)
    assert len(r['controls']) == 21
    assert sum(c['decision_state'] == 'RULE_PUBLISHED' for c in r['controls']) == 3
    assert sum(c['decision_state'] == 'NO_RULE_WILL_BE_PUBLISHED' for c in r['controls']) == 18
    assert r['not_yet_decided']['count'] == 59
    MODULE.validate_reply_object(r)


def test_each_entry_matches_authority_and_decision_record():
    authority, _, _, decisions, _ = inputs()
    rows = {c['control_id']: c for c in authority['controls']}
    latest = {x['control_id']: x for x in V2.latest_records(decisions)}
    for c in build()['controls']:
        row, rec = rows[c['control_id']], latest[c['control_id']]
        assert c['decision_state'] == row['not_applicable_decision_state'] == rec['decided_outcome']
        assert c['authority'] == row['not_applicable_authority'] == rec['decision_id']
        assert re.fullmatch(r'AA4-GOV-\d{3}', c['authority'])
        assert c['rule'] == row['not_applicable_rule'] == rec['decided']['rule']


def test_the_three_rules():
    r = build()
    rules = {c['control_id']: c['rule']['conditions'] for c in r['controls'] if c['rule']}
    assert rules == {'EMS-CTRL-030': [{'field': 'production', 'state': F}], 'EMS-CTRL-039': [{'field': 'production', 'state': F}], 'EMS-CTRL-052': [{'field': 'ai_enabled', 'state': F}]}


def test_first_sentence_for_all_records():
    _, _, _, decisions, _ = inputs()
    latest = {x['control_id']: x for x in V2.latest_records(decisions)}
    r = build()
    for cid in V2.REQUEST_CONTROL_IDS:
        rationale = latest[cid]['decided']['rationale']
        s = MODULE.first_sentence(rationale)
        assert s and s.endswith('.') and rationale.startswith(s)
        assert entry(r, cid)['reason'] == s


def test_mutation_swapped_aa4_id():
    r = build()
    a, b = r['controls'][0], r['controls'][1]
    a['authority'], b['authority'] = b['authority'], a['authority']
    assert rejected(r)


def test_mutation_bad_aa4_format():
    r = build()
    r['controls'][0]['authority'] = 'AA4-GOV-1'
    with pytest.raises(REJECTS):
        MODULE.validate_reply_object(r)


def test_mutation_flipped_state():
    r = build()
    c = next(x for x in r['controls'] if x['decision_state'] == 'RULE_PUBLISHED')
    c['decision_state'] = 'NO_RULE_WILL_BE_PUBLISHED'
    with pytest.raises(REJECTS):
        MODULE.validate_reply_object(r)
    r = build()
    c = next(x for x in r['controls'] if x['decision_state'] == 'NO_RULE_WILL_BE_PUBLISHED')
    c['decision_state'] = 'RULE_PUBLISHED'
    with pytest.raises(REJECTS):
        MODULE.validate_reply_object(r)


def test_mutation_altered_rule():
    r = build()
    entry(r, 'EMS-CTRL-030')['rule']['conditions'][0]['state'] = 'KNOWN_TRUE'
    assert rejected(r)
    r = build()
    entry(r, 'EMS-CTRL-030')['rule']['conditions'][0]['state'] = 'UNKNOWN'
    with pytest.raises(REJECTS):
        MODULE.validate_reply_object(r)


def test_mutation_removed_and_extra_control():
    r = build()
    r['controls'].pop()
    with pytest.raises(REJECTS):
        MODULE.validate_reply_object(r)
    r = build()
    extra = copy.deepcopy(r['controls'][0])
    extra['control_id'] = 'EMS-CTRL-079'
    r['controls'].append(extra)
    with pytest.raises(REJECTS):
        MODULE.validate_reply_object(r)


def test_mutation_sha_and_digest():
    r = build()
    r['pin']['publication_commit'] = 'a' * 39
    with pytest.raises(REJECTS):
        MODULE.validate_reply_object(r)
    r = build()
    r['pin']['authority_sha256'] = '0' * 64
    assert rejected(r)
    r = build()
    r['pin']['manifest_sha256'] = 'xyz'
    with pytest.raises(REJECTS):
        MODULE.validate_reply_object(r)


def test_mutation_dual_role_text():
    r = build()
    r['dual_role_statement'] += ' Altered.'
    with pytest.raises(REJECTS):
        MODULE.validate_reply_object(r)


def test_mutation_absolute_path():
    r = build()
    r['published_shape']['authority_path'] = 'C:/temp/standars/ems/registry/x.json'
    with pytest.raises(REJECTS):
        MODULE.validate_reply_object(r)


def test_markdown_content():
    r = build()
    text = MODULE.render_markdown(r)
    assert '\r' not in text
    pin = r['pin']
    for needle in (pin['publication_commit'], pin['authority_id'], pin['version'], pin['authority_sha256'], pin['manifest_sha256'], r['dual_role_statement'], 'WR-01', '04-VERIFICATION', 'NOT_YET_DECIDED', 'v2.0.1'):
        assert needle in text
    reasons = {c['reason'] for c in r['controls']}
    prose = '\n'.join(line for line in text.split('\n') if not (line.startswith('  Reason: ') and line[len('  Reason: '):] in reasons))
    prose = prose.replace('service_criticality', '')
    for word in MODULE.FORBIDDEN_WORDS:
        assert not re.search(rf'\b{word}\b', prose, re.IGNORECASE), word


@pytest.mark.skipif(not REAL_JSON.exists(), reason='reply not generated yet')
def test_real_reply_files_validate():
    MODULE.validate_reply()
    for p in (REAL_JSON, REAL_MD, MODULE.REPLY_SCHEMA):
        assert b'\r' not in p.read_bytes()
    assert not V2.contains_absolute(V2.load(REAL_JSON))


def test_publisher_still_valid_and_digest_matches_manifest():
    V2.validate_published()
    manifest = V2.load(V2.OUT / V2.N_MANIFEST)
    rel = V2.rel(V2.SCRIPT)
    recorded = next(a['sha256'] for a in manifest['artifacts'] if a['relative_path'] == rel)
    assert V2.lf_digest(V2.SCRIPT) == recorded


def git(*args):
    r = subprocess.run(['git', *args], cwd=ROOT, capture_output=True)
    return subprocess.CompletedProcess(r.args, r.returncode, r.stdout, r.stderr.decode('utf-8', 'replace').strip())


def git_ready():
    try:
        r = git('rev-parse', '--is-shallow-repository')
    except OSError:
        return 'git is unavailable'
    if r.returncode != 0:
        return 'not a git repository'
    if r.stdout.decode().strip() == 'true':
        return 'shallow repository, history is incomplete'
    return None


def lf_sha(b): return hashlib.sha256(b.replace(b'\r\n', b'\n')).hexdigest()


def test_publication_sha_is_ancestor_and_holds_authority():
    reason = git_ready()
    if reason:
        pytest.skip(reason)
    rec = V2.load(V2.PUBLICATION_RECORD)
    sha = rec['publication_commit']
    assert git('merge-base', '--is-ancestor', sha, 'HEAD').returncode == 0
    auth_rel = V2.rel(V2.AUTHORITY)
    assert lf_sha(git('show', f'{sha}:{auth_rel}').stdout) == rec['authority_sha256']


def test_record_commit_added_the_publication_record():
    reason = git_ready()
    if reason:
        pytest.skip(reason)
    sha = V2.load(V2.PUBLICATION_RECORD)['publication_commit']
    rec_rel = V2.rel(V2.PUBLICATION_RECORD)
    added = git('log', '--diff-filter=A', '--format=%H', '--', rec_rel).stdout.decode().split()
    assert added and added[0].startswith(MODULE.RECORD_COMMIT_ABBREV)
    assert added[0] != sha
    assert git('merge-base', '--is-ancestor', sha, added[0]).returncode == 0

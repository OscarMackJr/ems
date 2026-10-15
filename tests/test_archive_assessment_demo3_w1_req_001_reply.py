import copy
import hashlib
import importlib.util
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

# tmp_path is not usable on this Windows machine; use one module-level temporary directory.
_TMP = tempfile.TemporaryDirectory()
TMP = Path(_TMP.name)


def inputs():
    return V2.load(V2.AUTHORITY), V2.load(V2.PUBLICATION_RECORD), V2.load(V2.SIGNOFF), V2.load(V2.GOVERNANCE_DECISIONS)


def build():
    return MODULE.build_reply(*inputs())


def entry(reply, cid):
    return next(c for c in reply['controls'] if c['control_id'] == cid)


def run_validate_reply(reply, monkeypatch):
    p = TMP / 'reply.json'
    V2.dump(p, reply)
    md = TMP / 'reply.md'
    V2.write_text(md, MODULE.render_markdown(build()))
    monkeypatch.setattr(MODULE, 'REPLY_JSON', p)
    monkeypatch.setattr(MODULE, 'REPLY_MD', md)
    MODULE.validate_reply()


def assert_validate_rejects(reply, monkeypatch):
    # Drift that stays schema-valid must be caught by the real file-comparison path in validate_reply().
    MODULE.validate_reply_object(reply)
    with pytest.raises(AuthorityError, match='reply JSON differs from a fresh build'):
        run_validate_reply(reply, monkeypatch)


def test_validate_reply_accepts_unmutated_reply_from_temp_file(monkeypatch):
    run_validate_reply(build(), monkeypatch)


def test_validate_reply_rejects_loosened_schema_file(monkeypatch):
    s = V2.load(MODULE.REPLY_SCHEMA)
    s['additionalProperties'] = True
    p = TMP / 'reply.schema.json'
    V2.dump(p, s)
    monkeypatch.setattr(MODULE, 'REPLY_SCHEMA', p)
    pj, md = TMP / 'reply_s.json', TMP / 'reply_s.md'
    V2.dump(pj, build())
    V2.write_text(md, MODULE.render_markdown(build()))
    monkeypatch.setattr(MODULE, 'REPLY_JSON', pj)
    monkeypatch.setattr(MODULE, 'REPLY_MD', md)
    with pytest.raises(AuthorityError, match='reply schema differs'):
        MODULE.validate_reply()


def test_validate_reply_rejects_edited_decision_rationale(monkeypatch):
    doc = V2.load(V2.GOVERNANCE_DECISIONS)
    rec = next(r for r in V2.latest_records(doc) if r['control_id'] == V2.REQUEST_CONTROL_IDS[0])
    rec['decided']['rationale'] = 'Edited reason. ' + rec['decided']['rationale']
    assert doc != V2.load(V2.GOVERNANCE_DECISIONS)
    p = TMP / 'decisions.json'
    V2.dump(p, doc)
    monkeypatch.setattr(V2, 'GOVERNANCE_DECISIONS', p)
    with pytest.raises(AuthorityError, match='decision records differ'):
        MODULE.validate_reply()


def test_validate_reply_rejects_edited_signoff(monkeypatch):
    signoff = V2.load(V2.SIGNOFF)
    signoff['approval']['role'] = next(r for r in V2.APPROVER_ROLES if r != signoff['approval']['role'])
    p = TMP / 'signoff.json'
    V2.dump(p, signoff)
    real_rel, orig_rel = V2.rel(V2.SIGNOFF), V2.rel
    monkeypatch.setattr(V2, 'rel', lambda q: real_rel if q == p else orig_rel(q))
    monkeypatch.setattr(V2, 'SIGNOFF', p)
    with pytest.raises(AuthorityError, match='sign-off differs'):
        MODULE.validate_reply()


def test_built_reply_counts():
    r = build()
    assert [c['control_id'] for c in r['controls']] == sorted(MODULE.V2.REQUEST_CONTROL_IDS)
    assert len(r['controls']) == 21
    assert sum(c['decision_state'] == 'RULE_PUBLISHED' for c in r['controls']) == 3
    assert sum(c['decision_state'] == 'NO_RULE_WILL_BE_PUBLISHED' for c in r['controls']) == 18
    assert r['not_yet_decided']['count'] == 59
    MODULE.validate_reply_object(r)


def test_each_entry_matches_authority_and_decision_record():
    authority, _, _, decisions = inputs()
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
    _, _, _, decisions = inputs()
    latest = {x['control_id']: x for x in V2.latest_records(decisions)}
    r = build()
    for cid in V2.REQUEST_CONTROL_IDS:
        rationale = latest[cid]['decided']['rationale']
        s = MODULE.first_sentence(rationale)
        assert s and s.endswith('.') and rationale.startswith(s)
        assert entry(r, cid)['reason'] == s


def test_first_sentence_cases():
    assert MODULE.first_sentence('One sentence. Two sentence.') == 'One sentence.'
    assert MODULE.first_sentence('Line one.\nLine two.') == 'Line one.'
    assert MODULE.first_sentence('Only one sentence.') == 'Only one sentence.'


@pytest.mark.parametrize('text', ['See e.g. Section 2. Next one.', 'Broken line\ncontinues here. Next.', 'No period at all', ''])
def test_first_sentence_fails_closed(text):
    with pytest.raises(AuthorityError, match='cannot be cut deterministically'):
        MODULE.first_sentence(text)


def test_mutation_swapped_aa4_id(monkeypatch):
    r = build()
    a, b = r['controls'][0], r['controls'][1]
    a['authority'], b['authority'] = b['authority'], a['authority']
    assert_validate_rejects(r, monkeypatch)


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


def test_mutation_altered_rule(monkeypatch):
    r = build()
    entry(r, 'EMS-CTRL-030')['rule']['conditions'][0]['state'] = 'KNOWN_TRUE'
    assert_validate_rejects(r, monkeypatch)
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


def test_mutation_sha_and_digest(monkeypatch):
    r = build()
    r['pin']['publication_commit'] = 'a' * 39
    with pytest.raises(REJECTS):
        MODULE.validate_reply_object(r)
    r = build()
    r['pin']['authority_sha256'] = '0' * 64
    assert_validate_rejects(r, monkeypatch)
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
    for needle in (pin['publication_commit'], pin['authority_id'], pin['version'], pin['authority_sha256'], pin['manifest_sha256'], r['dual_role_statement'], 'NOT_YET_DECIDED', '54a7fd0'):
        assert needle in text
    assert 'No control resolves until' not in text
    for gone in ('WR-01', '04-VERIFICATION', 'independent evidence'):
        assert gone not in text
    assert not re.search(r'rules? (use|uses|carry|carries) (the )?eight', text)
    assert "Hayes's resolver resolves no control until the target description carries the eight classification facts" in text
    reasons = {c['reason'] for c in r['controls']}
    prose = '\n'.join(line for line in text.split('\n') if not (line.startswith('  Reason: ') and line[len('  Reason: '):] in reasons))
    prose = prose.replace('service_criticality', '')
    for word in MODULE.FORBIDDEN_WORDS:
        assert not re.search(rf'\b{word}\b', prose, re.IGNORECASE), word


def test_real_reply_files_validate():
    MODULE.validate_reply()
    for p in (REAL_JSON, REAL_MD, MODULE.REPLY_SCHEMA):
        assert b'\r' not in p.read_bytes()
    assert not V2.contains_absolute(V2.load(REAL_JSON))


def test_publisher_still_valid_and_digest_matches_manifest():
    V2.validate_published()
    manifest = V2.load(V2.OUT / V2.N_MANIFEST)
    rel = V2.rel(V2.SCRIPT)
    assert manifest['publisher_script']['relative_path'] == rel
    assert V2.lf_digest(V2.SCRIPT) == manifest['publisher_script']['sha256']


def fake_git(ls_remote_rc=0, cat_file_rc=0, merge_base_rc=0):
    tip = 'b' * 40
    def run(*args):
        if args[0] == 'ls-remote':
            out = f'{tip}\trefs/heads/{MODULE.REMOTE_BRANCH}\n' if ls_remote_rc == 0 else ''
            return subprocess.CompletedProcess(args, ls_remote_rc, out, '')
        if args[0] == 'cat-file':
            return subprocess.CompletedProcess(args, cat_file_rc, '', '')
        if args[0] == 'merge-base':
            return subprocess.CompletedProcess(args, merge_base_rc, '', '')
        raise AssertionError(f'push-check ran an unexpected git command: {args}')
    return run


@pytest.mark.parametrize('kwargs, expected', [
    ({}, MODULE.PUSH_ON),
    ({'merge_base_rc': 1}, MODULE.PUSH_NOT_ON),
    ({'merge_base_rc': 128}, MODULE.PUSH_UNKNOWN),
    ({'cat_file_rc': 1}, MODULE.PUSH_UNKNOWN),
    ({'ls_remote_rc': 2}, MODULE.PUSH_UNKNOWN),
])
def test_push_check_status(monkeypatch, capsys, kwargs, expected):
    monkeypatch.setattr(MODULE, 'git', fake_git(**kwargs))
    assert MODULE.push_check() == expected
    assert MODULE.PUSH_ON == 0 and MODULE.PUSH_NOT_ON != 0 and MODULE.PUSH_UNKNOWN != 0


def test_push_check_cli_exit_code(monkeypatch):
    monkeypatch.setattr(MODULE, 'git', fake_git(merge_base_rc=1))
    monkeypatch.setattr('sys.argv', ['x', '--push-check'])
    with pytest.raises(SystemExit) as e:
        MODULE.main()
    assert e.value.code == MODULE.PUSH_NOT_ON


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


def test_record_commit_is_last_change_of_the_record():
    reason = git_ready()
    if reason:
        pytest.skip(reason)
    sha = V2.load(V2.PUBLICATION_RECORD)['publication_commit']
    rec_rel = V2.rel(V2.PUBLICATION_RECORD)
    last = git('log', '-n1', '--format=%H', '--', rec_rel).stdout.decode().strip()
    assert re.fullmatch(r'[0-9a-f]{40}', last)
    assert last != sha
    assert git('merge-base', '--is-ancestor', sha, last).returncode == 0
    changed = git('diff-tree', '--no-commit-id', '--name-only', '-r', last).stdout.decode().split()
    assert changed == [rec_rel]
    assert MODULE.resolve_record_commit() == last
    assert build()['pin']['publication_record_commit'] == last


def test_history_note_binds_to_supersedes_and_decisions():
    authority, _, _, _ = inputs()
    sup = authority['source_lineage']['supersedes']
    r = build()
    assert 'disclosure' not in r
    h = r['history_note']
    assert (h['supersedes_authority_id'], h['supersedes_version'], h['supersedes_commit']) == (sup['authority_id'], sup['version'], sup['commit'])
    assert sup['commit'] == '54a7fd09114704a97a7a48fce5f89aebeb48c90a'
    assert h['governance_decisions_sha256'] == sup['governance_decisions_sha256'] == V2.lf_digest(V2.GOVERNANCE_DECISIONS)
    assert h['decisions_changed'] is False and len(h['enforced_gates']) == 4
    for k in ('review_path', 'verification_path', 'wr_01', 'v2_0_1_possible', 'v2_0_1_date'):
        assert k not in h and k not in MODULE.schema()['properties']
    assert r['pin']['authority_id'].endswith('2.0.1') and r['pin']['version'] == '2.0.1'
    MODULE.validate_reply_object(r)


def test_history_note_fails_when_decisions_differ(monkeypatch):
    doc = V2.load(V2.GOVERNANCE_DECISIONS)
    doc['records'][0]['decided']['rationale'] += ' Edited.'
    p = TMP / 'decisions_hist.json'
    V2.dump(p, doc)
    monkeypatch.setattr(V2, 'GOVERNANCE_DECISIONS', p)
    with pytest.raises(AuthorityError, match='differ from the superseded'):
        MODULE.build_reply(*inputs())


def test_date_comes_from_signoff():
    _, _, signoff, _ = inputs()
    assert build()['reply_date'] == signoff['approval']['date']
    assert not hasattr(MODULE, 'REPLY_DATE')


def test_build_reply_takes_four_inputs():
    with pytest.raises(TypeError):
        MODULE.build_reply(*inputs(), {})


def test_no_rule_published_row_raises_authority_error():
    authority, record, signoff, decisions = inputs()
    for row in authority['controls']:
        if row['not_applicable_decision_state'] == 'RULE_PUBLISHED':
            row['not_applicable_decision_state'] = 'NO_RULE_WILL_BE_PUBLISHED'
            row['not_applicable_rule'] = None
    with pytest.raises(AuthorityError):
        MODULE.build_reply(authority, record, signoff, decisions)


@pytest.mark.parametrize('mutate', [
    lambda a: a.pop('applicability_decision_ids'),
    lambda a: a.pop('not_applicable_semantics'),
    lambda a: a['controls'][0].pop('not_applicable_rule'),
    lambda a: a['controls'][0].pop('not_applicable_authority'),
    lambda a: a['controls'][5].__setitem__('decision_ids', a['controls'][5]['decision_ids'][:-1]),
])
def test_shape_names_validated_against_authority(mutate):
    authority, record, signoff, decisions = inputs()
    mutate(authority)
    with pytest.raises(AuthorityError):
        MODULE.build_reply(authority, record, signoff, decisions)


def test_record_commit_format_checked_by_schema_only():
    r = build()
    assert re.fullmatch(r'[0-9a-f]{40}', r['pin']['publication_record_commit'])
    r['pin']['publication_record_commit'] = '0ce89f2'
    with pytest.raises(REJECTS):
        MODULE.validate_reply_object(r)


def test_hayes_side_list_and_send_condition_name_publication_sha():
    reason = git_ready()
    if reason:
        pytest.skip(reason)
    r = build()
    sha = r['pin']['publication_commit']
    assert any(sha in item for item in r['hayes_side_changes_needed'])
    assert sha in r['send_condition'] and MODULE.REMOTE_BRANCH in r['send_condition']
    assert git('merge-base', '--is-ancestor', sha, 'HEAD').returncode == 0


@pytest.mark.parametrize('argv', [[], ['--build', '--validate'], ['--emit-schema', '--push-check']])
def test_cli_flags_mutually_exclusive(monkeypatch, argv):
    monkeypatch.setattr('sys.argv', ['x', *argv])
    with pytest.raises(SystemExit) as e:
        MODULE.main()
    assert e.value.code != 0

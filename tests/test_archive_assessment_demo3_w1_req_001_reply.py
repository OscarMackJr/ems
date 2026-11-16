import ast
import copy
import hashlib
import importlib.abc
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import types
from pathlib import Path

import jsonschema
import pytest

from aa_history import require_history

ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / 'scripts' / 'build_archive_assessment_demo3_w1_req_001_reply.py'
SPEC = importlib.util.spec_from_file_location('aa_reply_demo3', SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
AuthorityError = MODULE.AuthorityError


def assert_schema_rejects(reply, validator, path):
    # The frozen schema is the guard named by the test: assert the keyword and the instance path it failed on.
    with pytest.raises(jsonschema.ValidationError) as e:
        MODULE.validate_reply_object(reply)
    assert e.value.validator == validator, e.value.message
    assert list(e.value.absolute_path) == path, e.value.message
F = 'KNOWN_FALSE'

REAL_JSON = MODULE.REPLY_JSON
REAL_MD = MODULE.REPLY_MD

# tmp_path is not usable on this Windows machine; use one module-level temporary directory.
_TMP = tempfile.TemporaryDirectory()
TMP = Path(_TMP.name)


def dump(p, value):
    p.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n', encoding='utf-8', newline='\n')


def write_text(p, text):
    p.write_text(text, encoding='utf-8', newline='\n')


def inputs():
    return MODULE.load_inputs()


def serve_edited(monkeypatch, path, obj):
    rel_path, real = MODULE.rel(path), MODULE.git_show
    data = MODULE.jtext(obj).encode('utf-8')
    monkeypatch.setattr(MODULE, 'git_show', lambda commit, relative_path: data if relative_path == rel_path else real(commit, relative_path))


def build():
    return MODULE.build_reply(*inputs())


def entry(reply, cid):
    return next(c for c in reply['controls'] if c['control_id'] == cid)


def run_validate_reply(reply, monkeypatch):
    p = TMP / 'reply.json'
    dump(p, reply)
    md = TMP / 'reply.md'
    write_text(md, MODULE.render_markdown(build()))
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
    s = MODULE.load(MODULE.REPLY_SCHEMA)
    s['additionalProperties'] = True
    p = TMP / 'reply.schema.json'
    dump(p, s)
    monkeypatch.setattr(MODULE, 'REPLY_SCHEMA', p)
    pj, md = TMP / 'reply_s.json', TMP / 'reply_s.md'
    dump(pj, build())
    write_text(md, MODULE.render_markdown(build()))
    monkeypatch.setattr(MODULE, 'REPLY_JSON', pj)
    monkeypatch.setattr(MODULE, 'REPLY_MD', md)
    with pytest.raises(AuthorityError, match='reply schema differs'):
        MODULE.validate_reply()


def test_validate_reply_rejects_edited_decision_rationale(monkeypatch):
    doc = inputs()[3]
    rec = next(r for r in MODULE.latest_records(doc) if r['control_id'] == MODULE.REQUEST_CONTROL_IDS[0])
    rec['decided']['rationale'] = 'Edited reason. ' + rec['decided']['rationale']
    assert doc != inputs()[3]
    serve_edited(monkeypatch, MODULE.GOVERNANCE_DECISIONS, doc)
    with pytest.raises(AuthorityError, match='decision records differ'):
        MODULE.validate_reply()


def test_validate_reply_rejects_edited_signoff(monkeypatch):
    signoff = inputs()[2]
    signoff['approval']['role'] = next(r for r in MODULE.APPROVER_ROLES if r != signoff['approval']['role'])
    serve_edited(monkeypatch, MODULE.SIGNOFF, signoff)
    with pytest.raises(AuthorityError, match='sign-off differs'):
        MODULE.validate_reply()


def test_built_reply_counts():
    r = build()
    assert [c['control_id'] for c in r['controls']] == sorted(MODULE.REQUEST_CONTROL_IDS)
    assert len(r['controls']) == 21
    assert sum(c['decision_state'] == 'RULE_PUBLISHED' for c in r['controls']) == 3
    assert sum(c['decision_state'] == 'NO_RULE_WILL_BE_PUBLISHED' for c in r['controls']) == 18
    assert r['not_yet_decided']['count'] == 59
    MODULE.validate_reply_object(r)


def test_each_entry_matches_authority_and_decision_record():
    authority, _, _, decisions = inputs()
    rows = {c['control_id']: c for c in authority['controls']}
    latest = {x['control_id']: x for x in MODULE.latest_records(decisions)}
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
    latest = {x['control_id']: x for x in MODULE.latest_records(decisions)}
    r = build()
    for cid in MODULE.REQUEST_CONTROL_IDS:
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
    assert_schema_rejects(r, 'pattern', ['controls', 0, 'authority'])


def test_mutation_flipped_state():
    r = build()
    i, c = next((i, x) for i, x in enumerate(r['controls']) if x['decision_state'] == 'RULE_PUBLISHED')
    c['decision_state'] = 'NO_RULE_WILL_BE_PUBLISHED'
    assert_schema_rejects(r, 'type', ['controls', i, 'rule'])
    r = build()
    i, c = next((i, x) for i, x in enumerate(r['controls']) if x['decision_state'] == 'NO_RULE_WILL_BE_PUBLISHED')
    c['decision_state'] = 'RULE_PUBLISHED'
    assert_schema_rejects(r, 'type', ['controls', i, 'rule'])


def test_mutation_altered_rule(monkeypatch):
    r = build()
    entry(r, 'EMS-CTRL-030')['rule']['conditions'][0]['state'] = 'KNOWN_TRUE'
    assert_validate_rejects(r, monkeypatch)
    r = build()
    i = next(i for i, c in enumerate(r['controls']) if c['control_id'] == 'EMS-CTRL-030')
    r['controls'][i]['rule']['conditions'][0]['state'] = 'UNKNOWN'
    assert_schema_rejects(r, 'enum', ['controls', i, 'rule', 'conditions', 0, 'state'])


def test_mutation_removed_and_extra_control():
    r = build()
    r['controls'].pop()
    assert_schema_rejects(r, 'minItems', ['controls'])
    r = build()
    extra = copy.deepcopy(r['controls'][0])
    extra['control_id'] = 'EMS-CTRL-079'
    r['controls'].append(extra)
    assert_schema_rejects(r, 'maxItems', ['controls'])


@pytest.mark.parametrize('mutate', [
    lambda r: r['controls'][0].__setitem__('control_id', 'EMS-CTRL-001'),
    lambda r: r['controls'].reverse(),
])
def test_mutation_swapped_control_id_with_21_controls(mutate):
    # 21 schema-valid controls whose ids are not the requested ids in order: only the id-set guard rejects this.
    r = build()
    mutate(r)
    assert len(r['controls']) == 21
    jsonschema.Draft202012Validator(MODULE.frozen_schema()).validate(r)
    with pytest.raises(AuthorityError, match='reply controls differ from the 21 requested controls'):
        MODULE.validate_reply_object(r)


def test_mutation_sha_and_digest(monkeypatch):
    r = build()
    r['pin']['publication_commit'] = 'a' * 39
    assert_schema_rejects(r, 'pattern', ['pin', 'publication_commit'])
    r = build()
    r['pin']['manifest_sha256'] = 'xyz'
    assert_schema_rejects(r, 'pattern', ['pin', 'manifest_sha256'])


@pytest.mark.parametrize('key', ['authority_sha256', 'manifest_sha256'])
def test_mutation_zeroed_digest_reaches_the_fresh_build_comparison(monkeypatch, key):
    # A well-formed but wrong digest passes the schema and validate_reply_object; the reply has no separate
    # derived-values check, so the fresh-build comparison in validate_reply() is the guard that rejects it.
    r = build()
    r['pin'][key] = '0' * 64
    assert_validate_rejects(r, monkeypatch)


def test_mutation_dual_role_text():
    r = build()
    r['dual_role_statement'] += ' Altered.'
    # dual_role_statement is only minLength 1 in the schema, so the dual role guard must be the one that fires.
    jsonschema.Draft202012Validator(MODULE.frozen_schema()).validate(r)
    with pytest.raises(AuthorityError, match='dual role statement differs from the published statement'):
        MODULE.validate_reply_object(r)


@pytest.mark.parametrize('path', ['C:/temp/standars/ems/registry/x.json', 'C:\\temp\\x.json', '/temp/x.json'])
def test_mutation_absolute_path(path):
    r = build()
    r['published_shape']['authority_path'] = path
    # authority_path is any string in the schema, so contains_absolute must be the guard that fires.
    jsonschema.Draft202012Validator(MODULE.frozen_schema()).validate(r)
    with pytest.raises(AuthorityError, match='reply contains an absolute path'):
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


def test_real_reply_files_validate(capsys):
    # D-13 / FROZEN-04: the committed bytes themselves, with no monkeypatching.
    require_history(ROOT, commits=FROZEN_COMMITS)
    capsys.readouterr()
    MODULE.validate_reply()
    assert capsys.readouterr().out.strip() == 'PASS'
    for p in (REAL_JSON, REAL_MD, MODULE.REPLY_SCHEMA):
        assert b'\r' not in p.read_bytes()
    assert not MODULE.contains_absolute(MODULE.load(REAL_JSON))


def git(*args):
    r = subprocess.run(['git', *args], cwd=ROOT, capture_output=True)
    return subprocess.CompletedProcess(r.args, r.returncode, r.stdout, r.stderr.decode('utf-8', 'replace').strip())


FROZEN_COMMITS = (MODULE.REPLY_PUBLICATION_COMMIT, MODULE.REPLY_RECORD_COMMIT, MODULE.REPLY_SCHEMA_COMMIT)


def lf_sha(b): return hashlib.sha256(b.replace(b'\r\n', b'\n')).hexdigest()


def test_publication_sha_is_ancestor_and_holds_authority():
    require_history(ROOT, commits=FROZEN_COMMITS)
    rec = inputs()[1]
    sha = MODULE.REPLY_PUBLICATION_COMMIT
    assert rec['publication_commit'] == sha
    assert git('merge-base', '--is-ancestor', sha, 'HEAD').returncode == 0
    auth_rel = MODULE.rel(MODULE.AUTHORITY)
    assert lf_sha(git('show', f'{sha}:{auth_rel}').stdout) == rec['authority_sha256']


def test_frozen_constants_match_git():
    require_history(ROOT, commits=FROZEN_COMMITS)
    assert git('rev-parse', '31addfa').stdout.decode().strip() == MODULE.REPLY_PUBLICATION_COMMIT
    assert git('rev-parse', '4d9b7c1').stdout.decode().strip() == MODULE.REPLY_RECORD_COMMIT
    rec_rel = MODULE.rel(MODULE.PUBLICATION_RECORD)
    changed = git('diff-tree', '--no-commit-id', '--name-only', '-r', MODULE.REPLY_RECORD_COMMIT).stdout.decode().split()
    assert changed == [rec_rel]
    assert git('merge-base', '--is-ancestor', MODULE.REPLY_PUBLICATION_COMMIT, MODULE.REPLY_RECORD_COMMIT).returncode == 0
    assert MODULE.resolve_record_commit() == MODULE.REPLY_RECORD_COMMIT
    assert build()['pin']['publication_record_commit'] == MODULE.REPLY_RECORD_COMMIT
    assert re.fullmatch(r'[0-9a-f]{40}', MODULE.REPLY_SCHEMA_COMMIT)
    assert git('cat-file', '-e', f'{MODULE.REPLY_SCHEMA_COMMIT}^{{commit}}').returncode == 0
    assert git('merge-base', '--is-ancestor', MODULE.REPLY_SCHEMA_COMMIT, 'HEAD').returncode == 0
    assert MODULE.REPLY_SCHEMA_REL == MODULE.rel(MODULE.REPLY_SCHEMA)
    shown = git('show', f'{MODULE.REPLY_SCHEMA_COMMIT}:{MODULE.REPLY_SCHEMA_REL}')
    assert shown.returncode == 0
    assert shown.stdout.replace(b'\r\n', b'\n') == MODULE.REPLY_SCHEMA.read_bytes().replace(b'\r\n', b'\n')
    assert MODULE.frozen_schema() == json.loads(shown.stdout.decode('utf-8'))


def fake_shallow_git(rc, out, exc=None, cat_rc=0, mb_rc=0, cat_exc=None, mb_exc=None):
    seen = []
    def run(*args):
        seen.append(args)
        if args[0] == 'rev-parse' and args[1] == '--is-shallow-repository':
            if exc:
                raise exc
            return subprocess.CompletedProcess(args, rc, out, '')
        if args[0] == 'cat-file':
            if cat_exc:
                raise cat_exc
            return subprocess.CompletedProcess(args, cat_rc, '', '')
        if args[0] == 'merge-base':
            if mb_exc:
                raise mb_exc
            return subprocess.CompletedProcess(args, mb_rc, '', '')
        raise AssertionError(f'unexpected git command: {args}')
    run.seen = seen
    return run


@pytest.mark.parametrize('rc, out, exc', [
    (0, 'true\n', None),
    (128, '', None),
    (0, 'maybe\n', None),
    (0, '', OSError('git missing')),
])
def test_resolve_record_commit_fails_when_shallow_or_unknown(monkeypatch, rc, out, exc):
    fake = fake_shallow_git(rc, out, exc)
    monkeypatch.setattr(MODULE, 'git', fake)
    with pytest.raises(MODULE.AuthorityError, match='shallow'):
        MODULE.resolve_record_commit()


def test_resolve_record_commit_full_clone_passes_through(monkeypatch):
    fake = fake_shallow_git(0, 'false\n')
    monkeypatch.setattr(MODULE, 'git', fake)
    assert MODULE.resolve_record_commit() == MODULE.REPLY_RECORD_COMMIT


@pytest.mark.parametrize('kwargs, match', [
    ({'cat_rc': 128}, f'the frozen commit {MODULE.REPLY_RECORD_COMMIT} is not in the repository history'),
    ({'mb_rc': 1}, f'the frozen commit {MODULE.REPLY_RECORD_COMMIT} is not an ancestor of HEAD'),
    ({'mb_rc': 128}, 'cannot check ancestry.*git merge-base exit 128'),
    ({'cat_exc': OSError('git gone')}, 'in the repository history'),
    ({'mb_exc': OSError('git gone')}, 'cannot check ancestry'),
])
def test_resolve_record_commit_fails_when_commit_missing_or_not_ancestor(monkeypatch, kwargs, match):
    monkeypatch.setattr(MODULE, 'git', fake_shallow_git(0, 'false\n', **kwargs))
    with pytest.raises(AuthorityError, match=match):
        MODULE.resolve_record_commit()


def test_validate_fails_closed_without_history_shallow(monkeypatch):
    monkeypatch.setattr(MODULE, 'git', fake_shallow_git(0, 'true\n'))
    with pytest.raises(AuthorityError, match='shallow'):
        MODULE.validate_reply()


def test_validate_fails_closed_without_history_git_show(monkeypatch):
    def no_history(commit, relative_path):
        raise MODULE.GitHistoryError(f'{relative_path}@{commit[:7]}: git show failed')
    monkeypatch.setattr(MODULE, 'git_show', no_history)
    with pytest.raises(MODULE.GitHistoryError, match='git show failed'):
        MODULE.validate_reply()
    with pytest.raises(MODULE.GitHistoryError, match='git show failed'):
        MODULE.load_inputs()


@pytest.mark.parametrize('which', ['json', 'md'])
def test_validate_rejects_tampered_reply_bytes(monkeypatch, which):
    pj, md = TMP / f'tamper_{which}.json', TMP / f'tamper_{which}.md'
    pj.write_bytes(REAL_JSON.read_bytes() + (b' ' if which == 'json' else b''))
    md.write_bytes(REAL_MD.read_bytes() + (b' ' if which == 'md' else b''))
    monkeypatch.setattr(MODULE, 'REPLY_JSON', pj)
    monkeypatch.setattr(MODULE, 'REPLY_MD', md)
    with pytest.raises(AuthorityError, match='differs from a fresh build'):
        MODULE.validate_reply()


REPLY_RECORD_BINDING = 'REPLY_PUBLICATION_COMMIT differs from the publication_commit named by the frozen publication record'


@pytest.mark.parametrize('name, value, error, match', [
    # an unknown commit: resolve_record_commit is called via build_reply, after the pinned reads in load_inputs, so the first pinned read fails
    ('REPLY_PUBLICATION_COMMIT', 'd' * 40, MODULE.GitHistoryError, 'registry/archive_assessment_applicability_authority_v2.json@d{40}: git show failed'),
    ('REPLY_PUBLICATION_COMMIT', '54a7fd09114704a97a7a48fce5f89aebeb48c90a', AuthorityError, REPLY_RECORD_BINDING),
    # valid commits holding the same 2.0.1 bytes or reachable history: only the record binding rejects these (WR-01)
    ('REPLY_PUBLICATION_COMMIT', '4d9b7c1f41df5fa7575d4653a7d54ff9cf0a192b', AuthorityError, REPLY_RECORD_BINDING),
    ('REPLY_PUBLICATION_COMMIT', 'b3c041146a5360e582b0161183414ec70059919d', AuthorityError, REPLY_RECORD_BINDING),
    ('REPLY_RECORD_COMMIT', 'd' * 40, MODULE.GitHistoryError, 'registry/archive_assessment_applicability_authority_v2_publication_record.json@d{40}: git show failed'),
    # the record read at that commit does not name the 2.0.1 publication commit, so the binding rejects it
    ('REPLY_RECORD_COMMIT', '31addfa95ffc5c2d6805c73fa1f34d6ccbe313eb', AuthorityError, REPLY_RECORD_BINDING),
])
def test_validate_rejects_tampered_constant(monkeypatch, name, value, error, match):
    require_history(ROOT, commits=FROZEN_COMMITS)
    monkeypatch.setattr(MODULE, name, value)
    with pytest.raises(error, match=match):
        MODULE.validate_reply()


def test_history_note_binds_to_supersedes_and_decisions():
    authority, _, _, _ = inputs()
    sup = authority['source_lineage']['supersedes']
    r = build()
    assert 'disclosure' not in r
    h = r['history_note']
    assert (h['supersedes_authority_id'], h['supersedes_version'], h['supersedes_commit']) == (sup['authority_id'], sup['version'], sup['commit'])
    assert sup['commit'] == '54a7fd09114704a97a7a48fce5f89aebeb48c90a'
    assert h['governance_decisions_sha256'] == sup['governance_decisions_sha256'] == MODULE.pinned_digest(MODULE.REPLY_PUBLICATION_COMMIT, MODULE.GOVERNANCE_DECISIONS)
    assert h['decisions_changed'] is False and len(h['enforced_gates']) == 4
    for k in ('review_path', 'verification_path', 'wr_01', 'v2_0_1_possible', 'v2_0_1_date'):
        assert k not in h and k not in MODULE.frozen_schema()['properties']
    assert r['pin']['authority_id'].endswith('2.0.1') and r['pin']['version'] == '2.0.1'
    MODULE.validate_reply_object(r)


def test_history_note_fails_when_decisions_differ(monkeypatch):
    args = inputs()
    doc = copy.deepcopy(args[3])
    doc['records'][0]['decided']['rationale'] += ' Edited.'
    serve_edited(monkeypatch, MODULE.GOVERNANCE_DECISIONS, doc)
    with pytest.raises(AuthorityError, match='differ from the superseded'):
        MODULE.build_reply(*args)


def test_date_comes_from_signoff():
    _, _, signoff, _ = inputs()
    assert build()['reply_date'] == signoff['approval']['date']
    assert not hasattr(MODULE, 'REPLY_DATE')


def test_build_reply_takes_four_inputs():
    with pytest.raises(TypeError):
        MODULE.build_reply(*inputs(), {})


def test_no_rule_published_row_raises_authority_error():
    authority, record, signoff, decisions = inputs()
    latest = {r['control_id']: r for r in MODULE.latest_records(decisions)}
    for row in authority['controls']:
        if row['not_applicable_decision_state'] == 'RULE_PUBLISHED':
            row['not_applicable_decision_state'] = 'NO_RULE_WILL_BE_PUBLISHED'
            row['not_applicable_rule'] = None
            # keep the decision record in step with the row, so the record-agreement guard does not mask this one
            latest[row['control_id']]['decided_outcome'] = 'NO_RULE_WILL_BE_PUBLISHED'
            latest[row['control_id']]['decided']['rule'] = None
    with pytest.raises(AuthorityError, match='no RULE_PUBLISHED row for the example'):
        MODULE.build_reply(authority, record, signoff, decisions)


def test_decision_record_disagreeing_with_row_raises_authority_error():
    authority, record, signoff, decisions = inputs()
    row = next(r for r in authority['controls'] if r['not_applicable_decision_state'] == 'RULE_PUBLISHED')
    row['not_applicable_decision_state'] = 'NO_RULE_WILL_BE_PUBLISHED'
    row['not_applicable_rule'] = None
    with pytest.raises(AuthorityError, match=f"{row['control_id']}: decision record disagrees with the authority row"):
        MODULE.build_reply(authority, record, signoff, decisions)


@pytest.mark.parametrize('mutate, match', [
    (lambda a: a.pop('applicability_decision_ids'), 'authority lacks the top_level_field applicability_decision_ids'),
    (lambda a: a.pop('not_applicable_semantics'), 'authority lacks the semantics_block not_applicable_semantics'),
    (lambda a: a['controls'][0].pop('not_applicable_rule'), 'authority rows lack the field not_applicable_rule'),
    (lambda a: a['controls'][0].pop('not_applicable_authority'), 'authority rows lack the field not_applicable_authority'),
    (lambda a: a['controls'][5].__setitem__('decision_ids', a['controls'][5]['decision_ids'][:-1]), 'authority rows do not carry the eight AA1-GOV ids'),
])
def test_shape_names_validated_against_authority(mutate, match):
    authority, record, signoff, decisions = inputs()
    mutate(authority)
    with pytest.raises(AuthorityError, match=match):
        MODULE.build_reply(authority, record, signoff, decisions)


def test_record_commit_format_checked_by_schema_only():
    r = build()
    assert re.fullmatch(r'[0-9a-f]{40}', r['pin']['publication_record_commit'])
    r['pin']['publication_record_commit'] = '0ce89f2'
    assert_schema_rejects(r, 'pattern', ['pin', 'publication_record_commit'])


def test_hayes_side_list_and_send_condition_name_publication_sha():
    require_history(ROOT, commits=FROZEN_COMMITS)
    r = build()
    sha = r['pin']['publication_commit']
    assert any(sha in item for item in r['hayes_side_changes_needed'])
    assert sha in r['send_condition'] and MODULE.REMOTE_BRANCH in r['send_condition']
    assert git('merge-base', '--is-ancestor', sha, 'HEAD').returncode == 0


FROZEN_PATHS = [MODULE.REPLY_JSON, MODULE.REPLY_MD, MODULE.REPLY_SCHEMA, MODULE.SIGNOFF, MODULE.PUBLICATION_RECORD]


def frozen_bytes():
    return {p: p.read_bytes() for p in FROZEN_PATHS}


@pytest.mark.parametrize('argv', [[], ['--build'], ['--emit-schema'], ['--push-check'], ['--build', '--validate'], ['--emit-schema', '--validate'], ['--push-check', '--validate']])
def test_cli_rejects_removed_and_missing_modes(monkeypatch, capsys, argv):
    before = frozen_bytes()
    monkeypatch.setattr('sys.argv', ['x', *argv])
    with pytest.raises(SystemExit) as e:
        MODULE.main()
    assert e.value.code == 2
    err = capsys.readouterr().err
    # Alone, a removed flag leaves the required group empty; next to --validate it is reported as unrecognised.
    assert ('unrecognized arguments: ' + argv[0]) in err if '--validate' in argv else 'one of the arguments --validate is required' in err
    assert frozen_bytes() == before


def test_cli_validate_is_the_only_mode(monkeypatch, capsys):
    before = frozen_bytes()
    monkeypatch.setattr('sys.argv', ['x', '--validate'])
    MODULE.main()
    assert capsys.readouterr().out.strip() == 'PASS'
    assert frozen_bytes() == before
    for name in ('push_check', 'schema', 'dump', 'write_text', 'PUSH_ON', 'V2'):
        assert not hasattr(MODULE, name), name


# ---- 11-01: frozen on 2.0.1 at REPLY_PUBLICATION_COMMIT (D-02, D-11) ----

PUBLISHER_REL = 'scripts/publish_archive_assessment_applicability_authority_v2.py'
PUBLISHER_PATH = ROOT / 'scripts' / 'publish_archive_assessment_applicability_authority_v2.py'
_FROZEN = {}


def frozen_publisher(commit):
    if commit in _FROZEN:
        return _FROZEN[commit]
    r = subprocess.run(['git', 'show', f'{commit}:{PUBLISHER_REL}'], cwd=ROOT, capture_output=True)
    if r.returncode != 0:
        pytest.fail(f'cannot read {PUBLISHER_REL} at {commit}: {r.stderr.decode("utf-8", "replace").strip()}; fetch full history (git fetch --unshallow)')
    name = f'aa_frozen_publisher_{commit[:7]}'
    m = types.ModuleType(name)
    m.__file__ = str(PUBLISHER_PATH)
    sys.modules[name] = m
    try:
        exec(compile(r.stdout.decode('utf-8'), f'publisher@{commit}', 'exec'), m.__dict__)
    finally:
        sys.modules.pop(name, None)
    _FROZEN[commit] = m
    return m


def blob():
    return frozen_publisher(MODULE.REPLY_PUBLICATION_COMMIT)


def frozen_value(m, name):
    v = getattr(m, name)
    return v.relative_to(m.ROOT).as_posix() if isinstance(v, Path) else v


FROZEN_CONSTANTS = ['REGISTRY', 'SCHEMAS', 'AUTHORITY', 'SCHEMA', 'GOVERNANCE_DECISIONS', 'GOVERNANCE_DECISIONS_REL', 'REQUEST_CONTROL_IDS', 'DECISIONS', 'DECISION_STATES', 'VERSION', 'AUTHORITY_ID', 'OUT', 'SIGNOFF', 'PUBLICATION_RECORD', 'APPROVER', 'APPROVER_ROLES', 'SIGNOFF_ROLE', 'DUAL_ROLE_STATEMENT', 'N_TRACE', 'N_MANIFEST']


def test_frozen_publisher_blob_is_the_2_0_1_publisher():
    m = blob()
    assert m.VERSION == '2.0.1' and m.AUTHORITY_ID == 'EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.1'
    assert m.ROOT == MODULE.ROOT
    assert not hasattr(m, 'PREV_COMPARED_KEYS')


@pytest.mark.parametrize('name', FROZEN_CONSTANTS)
def test_frozen_constant_equals_publisher_blob(name):
    assert frozen_value(MODULE, name) == frozen_value(blob(), name)


def test_path_constants_resolve_under_the_builder_root():
    for name in FROZEN_CONSTANTS:
        v = getattr(MODULE, name)
        if isinstance(v, Path):
            assert v.is_relative_to(MODULE.ROOT)
            assert MODULE.rel(v) == blob().rel(getattr(blob(), name))


def outcome(fn, *args):
    try:
        return ('PASS', fn(*args))
    except Exception as e:
        return (type(e).__name__, str(e))


SYNTHETIC_RULE = {'combination': 'ALL_CONDITIONS_MUST_MATCH', 'conditions': [{'field': 'production', 'state': 'KNOWN_FALSE'}, {'field': 'ai_enabled', 'state': 'KNOWN_TRUE'}]}


def real_rules():
    authority = inputs()[0]
    rules = [c['not_applicable_rule'] for c in authority['controls'] if c['not_applicable_rule']]
    assert len(rules) == 3
    return rules


def test_rule_text_equals_publisher_blob():
    for rule in [*real_rules(), SYNTHETIC_RULE]:
        assert MODULE.rule_text(rule) == blob().rule_text(rule)


def latest_records_cases():
    decisions = inputs()[3]
    base = [{'decision_id': 'A', 'control_id': 'X'}, {'decision_id': 'B', 'control_id': 'X'}, {'decision_id': 'C', 'control_id': 'Y'}, {'decision_id': 'D', 'control_id': 'Z'}]
    as_str = copy.deepcopy(base)
    as_str[1]['supersedes'] = 'A'
    as_list = copy.deepcopy(base)
    as_list[3]['supersedes'] = ['B', 'C', 7]
    return [decisions, {'records': as_str}, {'records': as_list}, {}]


def test_latest_records_equals_publisher_blob():
    cases = latest_records_cases()
    assert len(MODULE.latest_records(cases[0])) == 21
    for doc in cases:
        assert MODULE.latest_records(doc) == blob().latest_records(doc)


def signoff_cases():
    _, record, signoff, _ = inputs()
    d = record['authority_sha256']
    def mut(fn):
        s = copy.deepcopy(signoff)
        fn(s)
        return (s, d)
    return [
        (signoff, d),
        mut(lambda s: s['approval'].__setitem__('approver', 'Someone Else')),
        mut(lambda s: s['approval'].__setitem__('role', 'HAYES_VERIFY_DEVELOPER')),
        mut(lambda s: s['approval'].__setitem__('date', '2026-02-30')),
        mut(lambda s: s['approval'].__setitem__('date', '14 November 2026')),
        mut(lambda s: s['approval'].__setitem__('scope', '  ')),
        mut(lambda s: s['approval'].pop('scope')),
        mut(lambda s: s.__setitem__('approval', 'approved')),
        mut(lambda s: s.__setitem__('status', 'DRAFT')),
        mut(lambda s: s.__setitem__('dual_role_statement', s['dual_role_statement'] + ' Altered.')),
        mut(lambda s: s.__setitem__('authority_id', 'EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.2')),
        mut(lambda s: s.__setitem__('version', '2.0.2')),
        mut(lambda s: s.__setitem__('authority_sha256_normalisation', 'RAW_BYTES')),
        mut(lambda s: s.__setitem__('extra', True)),
        (signoff, '0' * 64),
        ([], d),
        ('signoff', d),
    ]


def test_validate_signoff_equals_publisher_blob():
    cases = signoff_cases()
    results = [outcome(MODULE.validate_signoff, s, d) for s, d in cases]
    assert results[0] == ('PASS', None)
    assert all(r[0] == 'AuthorityError' for r in results[1:])
    for (s, d), mine in zip(cases, results):
        assert mine == outcome(blob().validate_signoff, s, d)


@pytest.mark.parametrize('value', ['/x', '\\\\x', 'C:\\x', 'C:/x', 'x/y', 'C:', ['a', ['/b']], {'a': {'b': 'C:/c'}}, {'a': ['b', 'c']}, 7, None])
def test_contains_absolute_equals_publisher_blob(value):
    assert MODULE.contains_absolute(value) == blob().contains_absolute(value)


def test_jtext_lf_bytes_and_rel_equal_publisher_blob():
    value = {'b': [1, {'z': None, 'a': 'x'}], 'a': {'c': True}}
    assert MODULE.jtext(value) == blob().jtext(value)
    assert MODULE.lf_bytes(b'a\r\nb\nc\r\n') == blob().lf_bytes(b'a\r\nb\nc\r\n')
    assert MODULE.rel(MODULE.SIGNOFF) == blob().rel(blob().SIGNOFF)
    assert issubclass(MODULE.GitHistoryError, MODULE.AuthorityError) and issubclass(MODULE.AuthorityError, ValueError)


FORBIDDEN_CALLS = {'import_module', '__import__', 'spec_from_file_location', 'SourceFileLoader', 'exec', 'eval'}


def publisher_refs(source):
    found = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            found += [f'import {a.name}' for a in node.names if 'publish_archive_assessment_applicability_authority' in a.name or a.name.startswith('importlib')]
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ''
            if 'publish_archive_assessment_applicability_authority' in mod or mod.startswith('importlib') or any('publish_archive_assessment_applicability_authority' in a.name for a in node.names):
                found.append(f'from {mod} import')
        elif isinstance(node, ast.Constant) and isinstance(node.value, str) and 'publish_archive_assessment_applicability_authority_v2' in node.value:
            found.append(f'string {node.value!r}')
        elif isinstance(node, ast.Name) and node.id == 'V2':
            found.append('name V2')
        elif isinstance(node, ast.Attribute) and node.attr == 'V2':
            found.append('attribute V2')
        if isinstance(node, ast.Call):
            f = node.func
            called = f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else None
            if called in FORBIDDEN_CALLS:
                found.append(f'call {called}')
    return found


OLD_LOADER = """import importlib.util
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location('aa_applicability_publisher_v2', ROOT / 'scripts' / 'publish_archive_assessment_applicability_authority_v2.py')
V2 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(V2)
"""


def test_builder_has_no_publisher_reference():
    assert publisher_refs(SCRIPT.read_text(encoding='utf-8')) == []


def test_publisher_ref_scanner_flags_the_old_loader():
    found = publisher_refs(OLD_LOADER)
    assert 'import importlib.util' in found and 'call spec_from_file_location' in found and 'name V2' in found
    assert any(f.startswith('string ') for f in found)
    assert publisher_refs('import publish_archive_assessment_applicability_authority_v2 as P') != []
    assert publisher_refs('from importlib import import_module\nimport_module("x")') != []
    assert publisher_refs('exec("x")') != []


def mutated_live_publisher():
    m = types.ModuleType('aa_mutated_publisher')
    m.__file__ = str(PUBLISHER_PATH)
    sys.modules['aa_mutated_publisher'] = m
    try:
        exec(compile(PUBLISHER_PATH.read_text(encoding='utf-8'), str(PUBLISHER_PATH), 'exec'), m.__dict__)
    finally:
        sys.modules.pop('aa_mutated_publisher', None)
    def raises(*a, **k):
        raise m.AuthorityError('mutated live publisher was called')
    m.PREV_COMPARED_KEYS = ('mutated',)
    m.DUAL_ROLE_STATEMENT = 'Mutated dual role statement.'
    m.rule_text = lambda rule: 'MUTATED RULE TEXT'
    m.validate_signoff = raises
    m.git_show = raises
    m.latest_records = raises
    m.REQUEST_CONTROL_IDS = ['EMS-CTRL-001']
    return m


class _Installed(importlib.abc.Loader):
    def __init__(self, module):
        self.module = module
    def create_module(self, spec):
        return self.module
    def exec_module(self, module):
        pass


def test_validate_reply_passes_with_a_mutated_live_publisher(monkeypatch, capsys):
    monkeypatch.delitem(sys.modules, 'aa_applicability_publisher_v2', raising=False)
    monkeypatch.delitem(sys.modules, 'publish_archive_assessment_applicability_authority_v2', raising=False)
    mutated = mutated_live_publisher()
    monkeypatch.setitem(sys.modules, 'aa_applicability_publisher_v2', mutated)
    monkeypatch.setitem(sys.modules, 'publish_archive_assessment_applicability_authority_v2', mutated)
    real_spec = importlib.util.spec_from_file_location
    def spec_for(name, location=None, *a, **k):
        if location is not None and Path(location).resolve() == PUBLISHER_PATH.resolve():
            return importlib.util.spec_from_loader(name, _Installed(mutated))
        return real_spec(name, location, *a, **k)
    monkeypatch.setattr(importlib.util, 'spec_from_file_location', spec_for)
    # Non-vacuity: the old loader line would now load the mutated publisher.
    old_spec = importlib.util.spec_from_file_location('aa_applicability_publisher_v2', PUBLISHER_PATH)
    old = importlib.util.module_from_spec(old_spec)
    old_spec.loader.exec_module(old)
    assert old.DUAL_ROLE_STATEMENT == 'Mutated dual role statement.' and old.rule_text({}) == 'MUTATED RULE TEXT'
    with pytest.raises(old.AuthorityError, match='mutated live publisher'):
        old.validate_signoff({}, '0' * 64)
    spec = importlib.util.spec_from_file_location('aa_reply_demo3_fresh', SCRIPT)
    fresh = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fresh)
    assert fresh is not MODULE and not hasattr(fresh, 'V2')
    capsys.readouterr()
    fresh.validate_reply()
    assert capsys.readouterr().out.strip() == 'PASS'
    assert fresh.DUAL_ROLE_STATEMENT != mutated.DUAL_ROLE_STATEMENT

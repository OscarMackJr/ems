import copy
import importlib.util
import re
import subprocess
import tempfile
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / 'scripts' / 'build_archive_assessment_demo3_w1_req_001_notice_2_0_2.py'
SPEC = importlib.util.spec_from_file_location('aa_notice_demo3', SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
V2 = MODULE.V2
AuthorityError = V2.AuthorityError
REJECTS = (AuthorityError, jsonschema.ValidationError)
F = 'KNOWN_FALSE'
PUB = MODULE.NOTICE_PUBLICATION_COMMIT
REC = MODULE.NOTICE_RECORD_COMMIT
SUP = MODULE.SUPERSEDED_COMMIT

# tmp_path is not usable on this Windows machine; use one module-level temporary directory.
_TMP = tempfile.TemporaryDirectory()
TMP = Path(_TMP.name)


def inputs():
    return MODULE.load_inputs()


def build():
    return MODULE.build_notice(*inputs())


def serve_edited(monkeypatch, commit, path, obj):
    # 2.0.1 and 2.0.2 share one relative path, so the edit is keyed on commit and path.
    rel_path, real = V2.rel(path), V2.git_show
    data = V2.jtext(obj).encode('utf-8')
    monkeypatch.setattr(V2, 'git_show', lambda c, relative_path: data if (c == commit and relative_path == rel_path) else real(c, relative_path))


def write_set(monkeypatch, notice=None, md_text=None, schema_obj=None):
    base = build()
    pj, md, ps = TMP / 'notice.json', TMP / 'notice.md', TMP / 'notice.schema.json'
    V2.dump(pj, base if notice is None else notice)
    V2.write_text(md, MODULE.render_markdown(base) if md_text is None else md_text)
    V2.dump(ps, MODULE.schema() if schema_obj is None else schema_obj)
    monkeypatch.setattr(MODULE, 'NOTICE_JSON', pj)
    monkeypatch.setattr(MODULE, 'NOTICE_MD', md)
    monkeypatch.setattr(MODULE, 'NOTICE_SCHEMA', ps)


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


def test_validate_notice_accepts_unmutated_notice_from_temp_files(monkeypatch):
    write_set(monkeypatch)
    MODULE.validate_notice()


def test_validate_notice_rejects_loosened_schema_file(monkeypatch):
    s = MODULE.schema()
    s['additionalProperties'] = True
    write_set(monkeypatch, schema_obj=s)
    with pytest.raises(AuthorityError, match='notice schema differs from a fresh build'):
        MODULE.validate_notice()


@pytest.mark.parametrize('key, value', [
    ('authority_id', 'EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.1'),
    ('version', '2.0.1'),
    ('publication_commit', SUP),
    ('publication_commit', REC),
    ('authority_sha256', '0' * 64),
    ('manifest_sha256', '0' * 64),
])
def test_validate_rejects_tampered_cited_value(monkeypatch, key, value):
    notice = build()
    notice['pin'][key] = value
    with pytest.raises(REJECTS):
        MODULE.validate_notice_object(notice)
    write_set(monkeypatch, notice=notice)
    with pytest.raises(AuthorityError, match='notice JSON differs from a fresh build'):
        MODULE.validate_notice()


@pytest.mark.parametrize('which', ['json', 'md'])
def test_validate_rejects_tampered_notice_bytes(monkeypatch, which):
    write_set(monkeypatch)
    target = MODULE.NOTICE_JSON if which == 'json' else MODULE.NOTICE_MD
    target.write_bytes(target.read_bytes() + b' ')
    with pytest.raises(AuthorityError, match='differs from a fresh build'):
        MODULE.validate_notice()


def test_validate_reports_ungenerated_files(monkeypatch):
    monkeypatch.setattr(MODULE, 'NOTICE_JSON', TMP / 'absent.json')
    with pytest.raises(AuthorityError, match='not generated'):
        MODULE.validate_notice()


@pytest.mark.parametrize('name, value', [
    ('NOTICE_PUBLICATION_COMMIT', 'd' * 40),
    ('NOTICE_PUBLICATION_COMMIT', SUP),
    # valid commits reachable in history: only the record binding or the schema constants reject these (WR-01)
    ('NOTICE_PUBLICATION_COMMIT', '4d9b7c1f41df5fa7575d4653a7d54ff9cf0a192b'),
    ('NOTICE_PUBLICATION_COMMIT', 'b3c041146a5360e582b0161183414ec70059919d'),
    ('NOTICE_RECORD_COMMIT', 'd' * 40),
    ('NOTICE_RECORD_COMMIT', 'ae15c7458e49c8f55cc58c61bab04bc716aa9892'),
])
def test_validate_rejects_tampered_constant(monkeypatch, name, value):
    reason = git_ready()
    if reason:
        pytest.skip(reason)
    write_set(monkeypatch)
    monkeypatch.setattr(MODULE, name, value)
    with pytest.raises(REJECTS):
        MODULE.validate_notice()


def test_frozen_constants_match_git():
    reason = git_ready()
    if reason:
        pytest.skip(reason)
    assert git('rev-parse', 'ae15c74').stdout.decode().strip() == PUB
    assert git('rev-parse', 'a71257e').stdout.decode().strip() == REC
    assert git('rev-parse', '31addfa').stdout.decode().strip() == SUP
    changed = [p for p in git('diff', '--name-only', PUB, REC).stdout.decode().split() if not p.startswith('.planning/')]
    assert changed == [V2.rel(V2.PUBLICATION_RECORD)]
    assert git('merge-base', '--is-ancestor', PUB, REC).returncode == 0
    assert MODULE.resolve_record_commit() == REC
    assert build()['pin']['publication_record_commit'] == REC


def fake_shallow_git(rc, out, exc=None, cat_rc=0, mb_rc=0):
    seen = []

    def run(*args):
        seen.append(args)
        if args[0] == 'rev-parse' and args[1] == '--is-shallow-repository':
            if exc:
                raise exc
            return subprocess.CompletedProcess(args, rc, out, '')
        if args[0] == 'cat-file':
            return subprocess.CompletedProcess(args, cat_rc, '', '')
        if args[0] == 'merge-base':
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
    with pytest.raises(AuthorityError, match='shallow'):
        MODULE.resolve_record_commit()
    assert not any(a[0] in ('cat-file', 'merge-base') for a in fake.seen)


def test_resolve_record_commit_full_clone_passes_through(monkeypatch):
    fake = fake_shallow_git(0, 'false\n')
    monkeypatch.setattr(MODULE, 'git', fake)
    assert MODULE.resolve_record_commit() == REC
    checked = {a[-1] for a in fake.seen if a[0] == 'merge-base'}
    assert {'HEAD', REC} <= checked
    assert {a[2] for a in fake.seen if a[0] == 'merge-base' and a[-1] == 'HEAD'} == {PUB, SUP, REC}


@pytest.mark.parametrize('kwargs', [{'cat_rc': 128}, {'mb_rc': 1}])
def test_resolve_record_commit_fails_when_commit_missing_or_not_ancestor(monkeypatch, kwargs):
    monkeypatch.setattr(MODULE, 'git', fake_shallow_git(0, 'false\n', **kwargs))
    with pytest.raises(AuthorityError):
        MODULE.resolve_record_commit()


def test_validate_fails_closed_without_history_shallow(monkeypatch):
    write_set(monkeypatch)
    monkeypatch.setattr(MODULE, 'git', fake_shallow_git(0, 'true\n'))
    with pytest.raises(AuthorityError, match='shallow'):
        MODULE.validate_notice()


def test_validate_fails_closed_without_history_git_show(monkeypatch):
    write_set(monkeypatch)

    def no_history(commit, relative_path):
        raise V2.GitHistoryError(f'{relative_path}@{commit[:7]}: git show failed')
    monkeypatch.setattr(V2, 'git_show', no_history)
    with pytest.raises(V2.GitHistoryError):
        MODULE.validate_notice()
    with pytest.raises(AuthorityError):
        MODULE.load_inputs()


def test_validate_independent_of_live_version(monkeypatch):
    write_set(monkeypatch)

    def boom(*a, **k):
        raise AssertionError('validator read a live file digest')
    monkeypatch.setattr(V2, 'lf_digest', boom)
    monkeypatch.setattr(V2, 'VERSION', '9.9.9')
    monkeypatch.setattr(V2, 'AUTHORITY_ID', 'EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-9.9.9')
    MODULE.validate_notice()


def test_record_binding_rejects_a_record_naming_another_commit(monkeypatch):
    record = copy.deepcopy(inputs()[2])
    record['publication_commit'] = SUP
    serve_edited(monkeypatch, REC, V2.PUBLICATION_RECORD, record)
    with pytest.raises(AuthorityError, match='publication_commit'):
        MODULE.load_inputs()


def test_built_notice_counts_and_rules():
    n = build()
    d = n['decisions']
    assert (d['decided_count'], d['rule_count'], d['no_rule_count'], d['not_yet_decided_count']) == (21, 3, 18, 59)
    rules = {r['control_id']: r['rule']['conditions'] for r in d['rules']}
    assert rules == {'EMS-CTRL-030': [{'field': 'production', 'state': F}], 'EMS-CTRL-039': [{'field': 'production', 'state': F}], 'EMS-CTRL-052': [{'field': 'ai_enabled', 'state': F}]}
    assert all(r['machine_form'] == V2.rule_text(r['rule']) for r in d['rules'])
    assert d['governance_decisions_sha256'].startswith('4e746d1f') and d['decisions_changed'] is False
    MODULE.validate_notice_object(n)


def test_pin_matches_record_and_frozen_digests():
    n = build()
    pin = n['pin']
    assert pin['publication_commit'] == PUB and pin['version'] == '2.0.2'
    assert pin['authority_sha256'].startswith('a44eea1f') and pin['manifest_sha256'].startswith('9991228a')
    assert pin['authority_sha256'] == MODULE.pinned_digest(PUB, V2.AUTHORITY)
    assert pin['manifest_sha256'] == MODULE.pinned_digest(PUB, V2.OUT / V2.N_MANIFEST)
    assert pin['published_on'] == inputs()[3]['approval']['date']
    assert n['notice_date'] == MODULE.NOTICE_DATE


def test_digest_scope_names_exactly_the_three_digests():
    n = build()
    assert {d['previous_key'] for d in n['digest_scope_error']['digests']} == {'aa1_manifest_sha256', 'aa2_closure_sha256', 'aa2_approval_sha256'}
    authority, previous = inputs()[:2]
    for d in n['digest_scope_error']['digests']:
        assert authority['source_lineage'][d['key']]['normalisation'] == 'RAW_BYTES'
        assert previous['source_lineage'][d['previous_key']] == d['sha256'] == authority['source_lineage'][d['key']]['sha256']
    assert previous['source_lineage']['digest_normalisation'] == 'CRLF_TO_LF'
    text = MODULE.render_markdown(n)
    assert 'aa2_approval_sha256' in text and 'RAW_BYTES' in text and 'declared scope' in text


@pytest.mark.parametrize('mutate', [
    lambda p: p['source_lineage'].__setitem__('digest_normalisation', 'RAW_BYTES'),
    lambda p: p['source_lineage'].__setitem__('aa2_closure_sha256', '0' * 64),
    lambda p: p['source_lineage'].pop('aa1_manifest_sha256'),
])
def test_digest_scope_error_fails_when_previous_authority_edited(monkeypatch, mutate):
    authority, previous = inputs()[:2]
    edited = copy.deepcopy(previous)
    mutate(edited)
    with pytest.raises(AuthorityError):
        MODULE.digest_scope_error(authority, edited)
    serve_edited(monkeypatch, SUP, V2.AUTHORITY, edited)
    with pytest.raises(AuthorityError):
        MODULE.build_notice(*inputs())


def test_mutation_count_and_closed_levels_come_from_frozen_bytes(monkeypatch):
    n = build()
    frozen = MODULE.pinned_json(PUB, V2.OUT / V2.N_NEGATIVE)
    assert n['what_changed']['negative_mutation_count'] == len(frozen['negative_invariant_tests']) == 29
    assert n['what_changed']['closed_schema_levels']['count'] == len(V2.closed_schema_levels(MODULE.pinned_json(PUB, V2.SCHEMA))) == 16
    assert n['what_changed']['row_comparison'] == {'rows_compared': 80, 'rows_differing': 0, 'compared_keys': list(V2.PREV_COMPARED_KEYS)}
    edited = copy.deepcopy(frozen)
    edited['negative_invariant_tests'].append(edited['negative_invariant_tests'][0])
    serve_edited(monkeypatch, PUB, V2.OUT / V2.N_NEGATIVE, edited)
    with pytest.raises(AuthorityError, match='differs from the published manifest'):
        MODULE.load_inputs()


def test_lineage_lists_every_input_with_its_normalisation():
    authority = inputs()[0]
    lin = {e['key']: e for e in build()['what_changed']['lineage']}
    assert sorted(lin) == sorted(authority['source_lineage'])
    assert all(lin[k]['normalisation'] == 'RAW_BYTES' for k in ('aa1_manifest', 'aa2_approval', 'aa2_closure'))
    assert all(lin[k]['normalisation'] == 'CRLF_TO_LF' for k in lin if k not in ('aa1_manifest', 'aa2_approval', 'aa2_closure'))


def test_changed_row_blocks_no_decision_changed(monkeypatch):
    authority, previous = inputs()[:2]
    edited = copy.deepcopy(previous)
    edited['controls'][0]['not_applicable_decision_state'] = 'NO_RULE_WILL_BE_PUBLISHED' if edited['controls'][0]['not_applicable_decision_state'] != 'NO_RULE_WILL_BE_PUBLISHED' else 'NOT_YET_DECIDED'
    assert MODULE.rows_differing(authority, edited)[0] == 1


def test_dual_role_statement_must_match_published_statement():
    n = build()
    assert n['dual_role_statement'] == V2.DUAL_ROLE_STATEMENT
    n['dual_role_statement'] = n['dual_role_statement'] + ' Edited.'
    with pytest.raises(AuthorityError, match='dual role'):
        MODULE.validate_notice_object(n)


def test_no_forbidden_words_in_rendered_text():
    text = MODULE.render_markdown(build()) + V2.jtext(build())
    for word in MODULE.FORBIDDEN_WORDS:
        assert not re.search(rf'\b{word}\b', text, re.IGNORECASE)
    assert '\r' not in text


def test_forbidden_word_is_rejected():
    n = build()
    n['what_changed']['gate_fix_line'] = 'This is the best fix.'
    with pytest.raises(AuthorityError, match='best'):
        MODULE.validate_notice_object(n)


def test_absolute_path_is_rejected():
    n = build()
    n['what_changed']['lineage'][0]['relative_path'] = 'C:\\temp\\x.json'
    with pytest.raises(REJECTS):
        MODULE.validate_notice_object(n)


def test_markdown_content():
    n = build()
    text = MODULE.render_markdown(n)
    assert PUB in text and SUP in text and REC in text
    assert V2.DUAL_ROLE_STATEMENT in text
    assert 'Published on: 2026-11-12' in text and f"dated {MODULE.NOTICE_DATE}" in text
    assert MODULE.GATE_FIX_LINE in text and MODULE.REMOTE_BRANCH in text
    assert 'changes no authority bytes' in text
    assert text.startswith('# ') and 'This file is generated by' in text.split('\n')[2]


def test_schema_closes_every_object_level():
    s = MODULE.schema()
    assert s['additionalProperties'] is False and s['required'] == MODULE.NOTICE_KEYS
    assert s['properties']['pin']['properties']['publication_commit'] == {'const': PUB}
    assert s['properties']['pin']['properties']['version'] == {'const': '2.0.2'}
    assert len(V2.closed_schema_levels(s)) >= 8


@pytest.mark.parametrize('argv', [[], ['--build', '--validate'], ['--emit-schema', '--validate'], ['--push-check']])
def test_cli_flags_mutually_exclusive(monkeypatch, argv):
    monkeypatch.setattr('sys.argv', ['x', *argv])
    with pytest.raises(SystemExit) as e:
        MODULE.main()
    assert e.value.code != 0

import ast
import copy
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

ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / 'scripts' / 'build_archive_assessment_demo3_w1_req_001_notice_2_0_2.py'
SPEC = importlib.util.spec_from_file_location('aa_notice_demo3', SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
AuthorityError = MODULE.AuthorityError
REJECTS = (AuthorityError, jsonschema.ValidationError)
F = 'KNOWN_FALSE'
PUB = MODULE.NOTICE_PUBLICATION_COMMIT
REC = MODULE.NOTICE_RECORD_COMMIT
SUP = MODULE.SUPERSEDED_COMMIT
SCH = MODULE.NOTICE_SCHEMA_COMMIT

# tmp_path is not usable on this Windows machine; use one module-level temporary directory.
_TMP = tempfile.TemporaryDirectory()
TMP = Path(_TMP.name)


def dump(p, value):
    p.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n', encoding='utf-8', newline='\n')


def write_text(p, text):
    p.write_text(text, encoding='utf-8', newline='\n')


def inputs():
    return MODULE.load_inputs()


def build():
    return MODULE.build_notice(*inputs())


def serve_edited(monkeypatch, commit, path, obj):
    # 2.0.1 and 2.0.2 share one relative path, so the edit is keyed on commit and path.
    rel_path, real = MODULE.rel(path), MODULE.git_show
    data = MODULE.jtext(obj).encode('utf-8')
    monkeypatch.setattr(MODULE, 'git_show', lambda c, relative_path: data if (c == commit and relative_path == rel_path) else real(c, relative_path))


def write_set(monkeypatch, notice=None, md_text=None, schema_obj=None):
    base = build()
    pj, md, ps = TMP / 'notice.json', TMP / 'notice.md', TMP / 'notice.schema.json'
    dump(pj, base if notice is None else notice)
    write_text(md, MODULE.render_markdown(base) if md_text is None else md_text)
    dump(ps, MODULE.frozen_notice_schema() if schema_obj is None else schema_obj)
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
    s = MODULE.frozen_notice_schema()
    s['additionalProperties'] = True
    write_set(monkeypatch, schema_obj=s)
    with pytest.raises(AuthorityError, match='notice schema differs from the frozen schema at ' + SCH):
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
    ('NOTICE_SCHEMA_COMMIT', 'd' * 40),
    # a real commit before the notice schema existed: the schema read itself fails
    ('NOTICE_SCHEMA_COMMIT', 'ae15c7458e49c8f55cc58c61bab04bc716aa9892'),
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
    assert changed == [MODULE.rel(MODULE.PUBLICATION_RECORD)]
    assert git('merge-base', '--is-ancestor', PUB, REC).returncode == 0
    assert MODULE.resolve_record_commit() == REC
    assert build()['pin']['publication_record_commit'] == REC


def test_notice_schema_commit_holds_the_committed_schema():
    reason = git_ready()
    if reason:
        pytest.skip(reason)
    assert SCH == '052f0f13f4c882a7b80667d4835bc802002e0f80'
    assert git('rev-parse', '052f0f1').stdout.decode().strip() == SCH
    assert git('cat-file', '-e', f'{SCH}^{{commit}}').returncode == 0
    assert git('merge-base', '--is-ancestor', SCH, 'HEAD').returncode == 0
    # The schema commit post-dates the publication; it must never be used as the publication-vs-record ancestor.
    assert git('merge-base', '--is-ancestor', SCH, PUB).returncode != 0
    assert MODULE.NOTICE_SCHEMA_REL == MODULE.rel(MODULE.NOTICE_SCHEMA)
    shown = git('show', f'{SCH}:{MODULE.NOTICE_SCHEMA_REL}')
    assert shown.returncode == 0
    assert shown.stdout.replace(b'\r\n', b'\n') == MODULE.NOTICE_SCHEMA.read_bytes().replace(b'\r\n', b'\n')
    assert MODULE.frozen_notice_schema() == json.loads(shown.stdout.decode('utf-8'))
    assert MODULE.jtext(MODULE.frozen_notice_schema()).encode('utf-8') == shown.stdout.replace(b'\r\n', b'\n')


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
    assert {a[2] for a in fake.seen if a[0] == 'merge-base' and a[-1] == 'HEAD'} == {PUB, SUP, REC, SCH}
    assert {a[2] for a in fake.seen if a[0] == 'cat-file'} == {f'{c}^{{commit}}' for c in (PUB, SUP, REC, SCH)}
    # The schema commit post-dates the publication, so it is never in the publication-vs-record check.
    assert [a[2:] for a in fake.seen if a[0] == 'merge-base' and a[-1] != 'HEAD'] == [(PUB, REC)]


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
        raise MODULE.GitHistoryError(f'{relative_path}@{commit}: git show failed')
    monkeypatch.setattr(MODULE, 'git_show', no_history)
    with pytest.raises(MODULE.GitHistoryError):
        MODULE.validate_notice()
    with pytest.raises(AuthorityError):
        MODULE.load_inputs()


def test_record_binding_rejects_a_record_naming_another_commit(monkeypatch):
    record = copy.deepcopy(inputs()[2])
    record['publication_commit'] = SUP
    serve_edited(monkeypatch, REC, MODULE.PUBLICATION_RECORD, record)
    with pytest.raises(AuthorityError, match='publication_commit'):
        MODULE.load_inputs()


def test_built_notice_counts_and_rules():
    n = build()
    d = n['decisions']
    assert (d['decided_count'], d['rule_count'], d['no_rule_count'], d['not_yet_decided_count']) == (21, 3, 18, 59)
    rules = {r['control_id']: r['rule']['conditions'] for r in d['rules']}
    assert rules == {'EMS-CTRL-030': [{'field': 'production', 'state': F}], 'EMS-CTRL-039': [{'field': 'production', 'state': F}], 'EMS-CTRL-052': [{'field': 'ai_enabled', 'state': F}]}
    assert all(r['machine_form'] == MODULE.rule_text(r['rule']) for r in d['rules'])
    assert d['governance_decisions_sha256'].startswith('4e746d1f') and d['decisions_changed'] is False
    MODULE.validate_notice_object(n)


def test_pin_matches_record_and_frozen_digests():
    n = build()
    pin = n['pin']
    assert pin['publication_commit'] == PUB and pin['version'] == '2.0.2'
    assert pin['authority_sha256'].startswith('a44eea1f') and pin['manifest_sha256'].startswith('9991228a')
    assert pin['authority_sha256'] == MODULE.pinned_digest(PUB, MODULE.AUTHORITY)
    assert pin['manifest_sha256'] == MODULE.pinned_digest(PUB, MODULE.OUT / MODULE.N_MANIFEST)
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
    serve_edited(monkeypatch, SUP, MODULE.AUTHORITY, edited)
    with pytest.raises(AuthorityError):
        MODULE.build_notice(*inputs())


def test_mutation_count_and_closed_levels_come_from_frozen_bytes(monkeypatch):
    n = build()
    frozen = MODULE.pinned_json(PUB, MODULE.OUT / MODULE.N_NEGATIVE)
    assert n['what_changed']['negative_mutation_count'] == len(frozen['negative_invariant_tests']) == 29
    assert n['what_changed']['closed_schema_levels']['count'] == len(MODULE.closed_schema_levels(MODULE.pinned_json(PUB, MODULE.SCHEMA))) == 16
    assert n['what_changed']['row_comparison'] == {'rows_compared': 80, 'rows_differing': 0, 'compared_keys': list(MODULE.PREV_COMPARED_KEYS)}
    edited = copy.deepcopy(frozen)
    edited['negative_invariant_tests'].append(edited['negative_invariant_tests'][0])
    serve_edited(monkeypatch, PUB, MODULE.OUT / MODULE.N_NEGATIVE, edited)
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
    assert n['dual_role_statement'] == MODULE.DUAL_ROLE_STATEMENT
    n['dual_role_statement'] = n['dual_role_statement'] + ' Edited.'
    with pytest.raises(AuthorityError, match='dual role'):
        MODULE.validate_notice_object(n)


def test_no_forbidden_words_in_rendered_text():
    text = MODULE.render_markdown(build()) + MODULE.jtext(build())
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
    assert MODULE.DUAL_ROLE_STATEMENT in text
    assert 'Published on: 2026-11-12' in text and f"dated {MODULE.NOTICE_DATE}" in text
    assert MODULE.GATE_FIX_LINE in text and MODULE.REMOTE_BRANCH in text
    assert 'changes no authority bytes' in text
    assert text.startswith('# ') and 'This file is generated by' in text.split('\n')[2]


def test_schema_closes_every_object_level():
    s = MODULE.frozen_notice_schema()
    assert s['additionalProperties'] is False and s['required'] == MODULE.NOTICE_KEYS
    assert s['properties']['pin']['properties']['publication_commit'] == {'const': PUB}
    assert s['properties']['pin']['properties']['version'] == {'const': '2.0.2'}
    assert len(MODULE.closed_schema_levels(s)) >= 8


FROZEN_PATHS = [MODULE.NOTICE_JSON, MODULE.NOTICE_MD, MODULE.NOTICE_SCHEMA, MODULE.SIGNOFF, MODULE.PUBLICATION_RECORD]


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
    for name in ('schema', 'dump', 'write_text', 'V2'):
        assert not hasattr(MODULE, name), name


# ---- 11-02: frozen on 2.0.2 at NOTICE_PUBLICATION_COMMIT (D-02, D-11) ----

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
    return frozen_publisher(PUB)


def frozen_value(m, name):
    v = getattr(m, name)
    return v.relative_to(m.ROOT).as_posix() if isinstance(v, Path) else v


FROZEN_CONSTANTS = ['REGISTRY', 'SCHEMAS', 'AUTHORITY', 'SCHEMA', 'GOVERNANCE_DECISIONS', 'REQUEST_CONTROL_IDS', 'VERSION', 'AUTHORITY_ID', 'PREV_COMPARED_KEYS', 'OUT', 'SIGNOFF', 'PUBLICATION_RECORD', 'APPROVER', 'APPROVER_ROLES', 'SIGNOFF_ROLE', 'DUAL_ROLE_STATEMENT', 'N_NEGATIVE', 'N_TRACE', 'N_MANIFEST']


def test_frozen_publisher_blob_is_the_2_0_2_publisher():
    m = blob()
    assert PUB == 'ae15c7458e49c8f55cc58c61bab04bc716aa9892'
    assert m.VERSION == '2.0.2' and m.AUTHORITY_ID == 'EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.2'
    assert m.ROOT == MODULE.ROOT


@pytest.mark.parametrize('name', FROZEN_CONSTANTS)
def test_frozen_constant_equals_publisher_blob(name):
    assert frozen_value(MODULE, name) == frozen_value(blob(), name)


def test_notice_identity_constants_equal_the_frozen_publisher():
    assert MODULE.NOTICE_VERSION == MODULE.VERSION == blob().VERSION
    assert MODULE.NOTICE_AUTHORITY_ID == MODULE.AUTHORITY_ID == blob().AUTHORITY_ID


def test_path_constants_resolve_under_the_builder_root():
    for name in FROZEN_CONSTANTS:
        v = getattr(MODULE, name)
        if isinstance(v, Path):
            assert v.is_relative_to(MODULE.ROOT)
            assert MODULE.rel(v) == blob().rel(getattr(blob(), name))


def outcome(fn, *args, **kwargs):
    try:
        return ('PASS', fn(*args, **kwargs))
    except Exception as e:
        return (type(e).__name__, str(e))


SYNTHETIC_RULE = {'combination': 'ALL_CONDITIONS_MUST_MATCH', 'conditions': [{'field': 'production', 'state': 'KNOWN_FALSE'}, {'field': 'ai_enabled', 'state': 'KNOWN_TRUE'}]}
SYNTHETIC_SCHEMA = {'type': 'object', 'additionalProperties': False, 'properties': {
    'a': {'type': 'object', 'additionalProperties': False, 'properties': {'b': {'additionalProperties': True}}},
    'list': [{'additionalProperties': False}, {'x': {'additionalProperties': False}}, 3, None],
    'open': {'additionalProperties': {'type': 'string'}}}}


def test_rule_text_equals_publisher_blob():
    rules = [c['not_applicable_rule'] for c in inputs()[0]['controls'] if c['not_applicable_rule']]
    assert len(rules) == 3
    for rule in [*rules, SYNTHETIC_RULE]:
        assert MODULE.rule_text(rule) == blob().rule_text(rule)


def test_closed_schema_levels_equals_publisher_blob():
    real = MODULE.pinned_json(PUB, MODULE.SCHEMA)
    assert len(MODULE.closed_schema_levels(real)) == 16
    assert MODULE.closed_schema_levels(real) == blob().closed_schema_levels(real)
    assert MODULE.closed_schema_levels(SYNTHETIC_SCHEMA) == blob().closed_schema_levels(SYNTHETIC_SCHEMA)
    assert MODULE.closed_schema_levels(SYNTHETIC_SCHEMA) == ['$', '$.properties.a', '$.properties.list[0]', '$.properties.list[1].x']
    assert MODULE.closed_schema_levels(SYNTHETIC_SCHEMA, '#') == blob().closed_schema_levels(SYNTHETIC_SCHEMA, '#')


def signoff_cases():
    record, signoff = inputs()[2:4]
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
        mut(lambda s: s.__setitem__('authority_id', 'EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.1')),
        mut(lambda s: s.__setitem__('version', '2.0.1')),
        mut(lambda s: s.__setitem__('authority_sha256_normalisation', 'RAW_BYTES')),
        mut(lambda s: s.__setitem__('extra', True)),
        mut(lambda s: s.pop('version')),
        (signoff, '0' * 64),
        ([], d),
        ('signoff', d),
    ]


SIGNOFF_KWARGS = [
    {},
    {'authority_id': 'EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.2', 'version': '2.0.2'},
    {'authority_id': 'EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.1', 'version': '2.0.1'},
    {'authority_id': 'EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.2', 'version': None},
]


@pytest.mark.parametrize('kwargs', SIGNOFF_KWARGS)
def test_validate_signoff_equals_publisher_blob(kwargs):
    cases = signoff_cases()
    results = [outcome(MODULE.validate_signoff, s, d, **kwargs) for s, d in cases]
    if kwargs.get('version') != '2.0.1':
        assert results[0] == ('PASS', None)
    assert all(r[0] == 'AuthorityError' for r in results[1:])
    for (s, d), mine in zip(cases, results):
        assert mine == outcome(blob().validate_signoff, s, d, **kwargs)


def test_validate_signoff_is_the_four_argument_form():
    import inspect
    params = inspect.signature(MODULE.validate_signoff).parameters
    assert list(params) == ['record', 'authority_lf_digest', 'authority_id', 'version']
    assert params['authority_id'].default is None and params['version'].default is None
    assert list(params) == list(inspect.signature(blob().validate_signoff).parameters)


@pytest.mark.parametrize('value', ['/x', '\\\\x', 'C:\\x', 'C:/x', 'x/y', 'C:', ['a', ['/b']], {'a': {'b': 'C:/c'}}, {'a': ['b', 'c']}, 7, None])
def test_contains_absolute_equals_publisher_blob(value):
    assert MODULE.contains_absolute(value) == blob().contains_absolute(value)


@pytest.mark.parametrize('value', ['registry/x.json', '', '../x', 'a/../b', '\\x', 'C:x', 'C:/x', '/x', 'a\\..\\b', 7, None])
def test_bad_rel_equals_publisher_blob(value):
    assert MODULE.bad_rel(value) == blob().bad_rel(value)


@pytest.mark.parametrize('value', ['2026-11-12', '2026-02-30', '2026-1-12', '12 November 2026', '', None, 20261112])
def test_is_date_equals_publisher_blob(value):
    assert MODULE.is_date(value) == blob().is_date(value)


def test_jtext_lf_bytes_load_and_rel_equal_publisher_blob():
    value = {'b': [1, {'z': None, 'a': 'x'}], 'a': {'c': True}}
    assert MODULE.jtext(value) == blob().jtext(value)
    assert MODULE.lf_bytes(b'a\r\nb\nc\r\n') == blob().lf_bytes(b'a\r\nb\nc\r\n')
    assert MODULE.load(MODULE.NOTICE_JSON) == blob().load(MODULE.NOTICE_JSON)
    assert MODULE.rel(MODULE.SIGNOFF) == blob().rel(blob().SIGNOFF)
    assert issubclass(MODULE.GitHistoryError, MODULE.AuthorityError) and issubclass(MODULE.AuthorityError, ValueError)


def test_git_show_error_names_full_sha_and_fetch_hint():
    missing = 'e' * 40
    with pytest.raises(MODULE.GitHistoryError) as e:
        MODULE.git_show(missing, MODULE.NOTICE_SCHEMA_REL)
    assert 'git show failed' in str(e.value) and missing in str(e.value) and 'fetch full history (git fetch --unshallow)' in str(e.value)
    with pytest.raises(AuthorityError, match='40-character'):
        MODULE.git_show('ae15c74', MODULE.NOTICE_SCHEMA_REL)
    with pytest.raises(AuthorityError, match='repo-relative'):
        MODULE.git_show(PUB, '../x')


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
V2=importlib.util.module_from_spec(_spec)
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
    m.closed_schema_levels = lambda *a, **k: ['$mutated']
    m.git_show = raises
    m.REQUEST_CONTROL_IDS = ['EMS-CTRL-001']
    m.APPROVER_ROLES = ['MUTATED_ROLE']
    return m


class _Installed(importlib.abc.Loader):
    def __init__(self, module):
        self.module = module
    def create_module(self, spec):
        return self.module
    def exec_module(self, module):
        pass


def test_validate_notice_passes_with_a_mutated_live_publisher(monkeypatch, capsys):
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
    assert old.PREV_COMPARED_KEYS == ('mutated',)
    with pytest.raises(old.AuthorityError, match='mutated live publisher'):
        old.validate_signoff({}, '0' * 64, authority_id=None, version=None)
    spec = importlib.util.spec_from_file_location('aa_notice_demo3_fresh', SCRIPT)
    fresh = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fresh)
    assert fresh is not MODULE and not hasattr(fresh, 'V2')
    capsys.readouterr()
    fresh.validate_notice()
    assert capsys.readouterr().out.strip() == 'PASS'
    assert fresh.DUAL_ROLE_STATEMENT != mutated.DUAL_ROLE_STATEMENT
    assert fresh.PREV_COMPARED_KEYS != mutated.PREV_COMPARED_KEYS

import copy
import importlib.util
import json
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

import jsonschema
import pytest

from aa_history import require_history

ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / 'scripts' / 'build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py'
SPEC = importlib.util.spec_from_file_location('aa_notice_demo3_2_0_3', SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
AuthorityError = MODULE.AuthorityError
GitHistoryError = MODULE.GitHistoryError
F = 'KNOWN_FALSE'
PUB = MODULE.NOTICE_PUBLICATION_COMMIT
REC = MODULE.NOTICE_RECORD_COMMIT
P202 = MODULE.PREVIOUS_2_0_2_COMMIT
P201 = MODULE.PREVIOUS_2_0_1_COMMIT
FROZEN_COMMITS = (PUB, REC, P202, P201)
PUBLISHER_REL = 'scripts/publish_archive_assessment_applicability_authority_v2.py'
DECISIONS_BUILDER_REL = 'scripts/build_archive_assessment_governance_decisions.py'

# tmp_path is not usable on this Windows machine; use one module-level temporary directory.
_TMP = tempfile.TemporaryDirectory()
TMP = Path(_TMP.name)

_CACHE = {}


def inputs():
    # Runs the real load_inputs (including the real pinned 29-mutation rerun) once per module.
    require_history(ROOT, commits=FROZEN_COMMITS)
    if 'inputs' not in _CACHE:
        _CACHE['inputs'] = MODULE.load_inputs()
    return _CACHE['inputs']


def args():
    return copy.deepcopy(inputs())


def authority():
    return args()[0]


def previous_2_0_1():
    return args()[2]


def negative():
    return args()[8]


def rerun_outcomes():
    return args()[9]['outcomes']


def build():
    return MODULE.build_notice(*args())


def cached_pinned_run(monkeypatch):
    # Prime the cache from the real pinned run FIRST, then patch the rerun out for the rest of the test.
    cached = inputs()[9]
    monkeypatch.setattr(MODULE, 'pinned_mutation_run', lambda *a, **k: copy.deepcopy(cached))


def dump(p, value):
    p.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n', encoding='utf-8', newline='\n')


def write_text(p, text):
    p.write_text(text, encoding='utf-8', newline='\n')


def serve_edited(monkeypatch, commit, path, obj):
    rel_path, real = MODULE.rel(path), MODULE.git_show
    data = MODULE.jtext(obj).encode('utf-8')
    monkeypatch.setattr(MODULE, 'git_show', lambda c, relative_path: data if (c == commit and relative_path == rel_path) else real(c, relative_path))


def write_set(monkeypatch, notice=None, md_text=None, schema_obj=None):
    cached_pinned_run(monkeypatch)
    base = build()
    pj, md, ps = TMP / 'notice.json', TMP / 'notice.md', TMP / 'notice.schema.json'
    dump(pj, base if notice is None else notice)
    write_text(md, MODULE.render_markdown(base) if md_text is None else md_text)
    dump(ps, MODULE.schema() if schema_obj is None else schema_obj)
    monkeypatch.setattr(MODULE, 'NOTICE_JSON', pj)
    monkeypatch.setattr(MODULE, 'NOTICE_MD', md)
    monkeypatch.setattr(MODULE, 'NOTICE_SCHEMA', ps)


def git(*a, cwd=ROOT):
    r = subprocess.run(['git', *a], cwd=cwd, capture_output=True)
    return subprocess.CompletedProcess(r.args, r.returncode, r.stdout, r.stderr.decode('utf-8', 'replace').strip())


# ---- CLAIM-01: the mutation rerun ----

def test_check_rerun_fails_when_a_mutation_was_not_rejected():
    outcomes = rerun_outcomes()
    outcomes[3]['rejected_by'] = []
    with pytest.raises(AuthorityError, match=f"mutation {outcomes[3]['id']} was not rejected by the rerun"):
        MODULE.check_rerun(outcomes, negative())


def test_check_rerun_fails_when_frozen_negative_result_is_not_pass():
    neg = negative()
    neg['result'] = 'FAIL'
    with pytest.raises(AuthorityError, match='the frozen negative-invariant result at the pin is not PASS'):
        MODULE.check_rerun(rerun_outcomes(), neg)


def test_check_rerun_fails_when_rerun_differs_from_recorded():
    neg = negative()
    neg['negative_invariant_tests'][5]['rejected_by'] = ['PYTHON_VALIDATOR', 'SCHEMA', 'EXTRA']
    with pytest.raises(AuthorityError, match='the mutation rerun differs from the frozen negative-invariant output'):
        MODULE.check_rerun(rerun_outcomes(), neg)
    swapped = negative()
    tests = swapped['negative_invariant_tests']
    tests[0], tests[1] = tests[1], tests[0]
    with pytest.raises(AuthorityError, match='the mutation rerun differs from the frozen negative-invariant output'):
        MODULE.check_rerun(rerun_outcomes(), swapped)


def test_check_rerun_returns_29_rejected_mutations():
    got = MODULE.check_rerun(rerun_outcomes(), negative())
    assert len(got) == 29
    assert all(m['rejected_by'] for m in got)


def test_pinned_run_fails_when_pinned_code_accepts_a_mutation(monkeypatch):
    a = args()
    real = MODULE.load_pinned_publisher

    def wrapper(tmp):
        pub = real(tmp)
        pub.NEGATIVE_MUTATIONS.append(pub.Mutation('noop', 'No change.', 'AUTHORITY', lambda doc: None))
        return pub
    monkeypatch.setattr(MODULE, 'load_pinned_publisher', wrapper)
    with pytest.raises(AuthorityError, match='pinned mutation run failed: AuthorityError: mutation noop was accepted'):
        MODULE.pinned_mutation_run(a[0], a[4], a[5], a[6])


def test_pinned_run_fails_when_a_materialised_data_file_is_missing(monkeypatch):
    a = args()
    real = MODULE.load_pinned_publisher

    def wrapper(tmp):
        pub = real(tmp)
        (tmp / 'registry' / 'archive_assessment_governance_answers.json').unlink()
        return pub
    monkeypatch.setattr(MODULE, 'load_pinned_publisher', wrapper)
    with pytest.raises(AuthorityError, match='pinned baseline rejected the unmutated inputs'):
        MODULE.pinned_mutation_run(a[0], a[4], a[5], a[6])


def test_pinned_run_paths_stay_in_temp_materialisation(monkeypatch):
    a = args()
    real = MODULE.load_pinned_publisher
    seen = []

    def wrapper(tmp):
        pub = real(tmp)
        seen.append((tmp, pub))
        return pub
    monkeypatch.setattr(MODULE, 'load_pinned_publisher', wrapper)
    out = MODULE.pinned_mutation_run(a[0], a[4], a[5], a[6])
    assert len(out['outcomes']) == 29
    assert out['at_pin_deferred'].startswith('PUBLICATION_RECORD_BINDING: ')
    assert len(seen) == 1 and not seen[0][0].resolve().is_relative_to(ROOT.resolve())
    tmp, pub = seen[0]
    b = pub._BUILDER
    for module in (pub, b, b.V2):
        assert Path(module.ROOT).resolve().is_relative_to(tmp.resolve()), module.__name__
    for module in (pub, b.V2):
        top = module.git_run('rev-parse', '--show-toplevel')
        assert top.returncode == 0 and Path(top.stdout.decode('utf-8').strip()).resolve() == ROOT.resolve(), module.__name__
        with pytest.raises(AuthorityError, match='not git'):
            module.subprocess.run(['python', '--version'])


def test_pinned_run_rejects_publisher_digest_mismatch():
    a = args()
    manifest = a[6]
    manifest['publisher_script']['sha256'] = '0' * 64
    with pytest.raises(AuthorityError, match='pinned publisher differs from the certified publisher_script digest'):
        MODULE.pinned_mutation_run(a[0], a[4], a[5], manifest)


# ---- CLAIM-02: lineage recomputed from git ----

@pytest.mark.parametrize('key', sorted(MODULE.LINEAGE_NORMALISATION))
def test_lineage_entries_fails_on_wrong_digest(key):
    a = authority()
    a['source_lineage'][key]['sha256'] = '0' * 64
    with pytest.raises(AuthorityError, match=f'source_lineage {key}: recomputed sha256 at [0-9a-f]{{40}} differs'):
        MODULE.lineage_entries(a)


def test_lineage_entries_recomputes_all_seven():
    entries = MODULE.lineage_entries(authority())
    assert len(entries) == 7
    want = {'catalog_reference': MODULE.CATALOG_COMMIT, 'v1_baseline': MODULE.CATALOG_COMMIT, 'supersedes': P202}
    for e in entries:
        assert e['recomputed_at'] == want.get(e['key'], PUB), e['key']
        assert e['normalisation'] == MODULE.LINEAGE_NORMALISATION[e['key']]


# ---- CLAIM-03: the 2.0.1 digest-scope error ----

@pytest.mark.parametrize('key', ['aa1_manifest', 'aa2_approval', 'aa2_closure'])
def test_digest_scope_error_fails_when_raw_equals_lf(monkeypatch, key):
    a, p = authority(), previous_2_0_1()
    path = a['source_lineage'][key]['relative_path']
    real = MODULE.git_show
    monkeypatch.setattr(MODULE, 'git_show', lambda c, rp: real(c, rp).replace(b'\r\n', b'\n') if (c, rp) == (PUB, path) else real(c, rp))
    with pytest.raises(AuthorityError, match=f'{key}: raw sha256 equals its LF sha256'):
        MODULE.digest_scope_error(a, p)


def test_digest_scope_error_shows_raw_and_lf():
    got = MODULE.digest_scope_error(authority(), previous_2_0_1())
    digests = got['digests']
    assert len(digests) == 3
    assert all(d['raw_sha256'] != d['lf_sha256'] for d in digests)
    assert [d['raw_sha256'][:8] for d in digests] == ['f0da8e2e', 'de170ebc', 'ed589d76']
    assert [d['lf_sha256'][:8] for d in digests] == ['06e39f7b', '248b6e38', '66662df3']
    assert got['digest_values_changed'] is False and got['computed_at'] == PUB and got['previous_commit'] == P201


def test_digest_scope_error_fails_without_2_0_1_global_claim():
    p = previous_2_0_1()
    p['source_lineage']['digest_normalisation'] = 'RAW_BYTES'
    with pytest.raises(AuthorityError, match='the 2.0.1 authority does not declare the global CRLF_TO_LF claim'):
        MODULE.digest_scope_error(authority(), p)


# ---- fail-closed history (never skipped, never reach require_history) ----

def fake_shallow_git(rc, out, exc=None, cat_rc=0, mb_rc=0):
    seen = []

    def run(*a):
        seen.append(a)
        if a[0] == 'rev-parse' and a[1] == '--is-shallow-repository':
            if exc:
                raise exc
            return subprocess.CompletedProcess(a, rc, out, '')
        if a[0] == 'cat-file':
            return subprocess.CompletedProcess(a, cat_rc, '', '')
        if a[0] == 'merge-base':
            return subprocess.CompletedProcess(a, mb_rc, '', '')
        raise AssertionError(f'unexpected git command: {a}')
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
    assert {a[2] for a in fake.seen if a[0] == 'merge-base' and a[-1] == 'HEAD'} == set(FROZEN_COMMITS)
    assert {a[2] for a in fake.seen if a[0] == 'cat-file'} == {f'{c}^{{commit}}' for c in FROZEN_COMMITS}
    assert [a[2:] for a in fake.seen if a[0] == 'merge-base' and a[-1] != 'HEAD'] == [(PUB, REC)]


@pytest.mark.parametrize('kwargs, match', [
    ({'cat_rc': 128}, f'the frozen commit {PUB} is not in the repository history'),
    ({'mb_rc': 1}, f'the frozen commit {PUB} is not an ancestor of HEAD'),
])
def test_resolve_record_commit_fails_when_commit_missing_or_not_ancestor(monkeypatch, kwargs, match):
    monkeypatch.setattr(MODULE, 'git', fake_shallow_git(0, 'false\n', **kwargs))
    with pytest.raises(AuthorityError, match=match):
        MODULE.resolve_record_commit()


def test_resolve_record_commit_fails_when_publication_not_before_record(monkeypatch):
    fake = fake_shallow_git(0, 'false\n')

    def run(*a):
        if a[0] == 'merge-base' and a[2] == PUB and a[-1] == REC:
            return subprocess.CompletedProcess(a, 1, '', '')
        return fake(*a)
    monkeypatch.setattr(MODULE, 'git', run)
    with pytest.raises(AuthorityError, match='the publication commit is not an ancestor of the record commit'):
        MODULE.resolve_record_commit()


def dummy_notice_files(monkeypatch):
    pj, md, ps = TMP / 'no-history-notice.json', TMP / 'no-history-notice.md', TMP / 'no-history-notice.schema.json'
    write_text(pj, '{}\n')
    write_text(md, 'dummy\n')
    write_text(ps, '{}\n')
    monkeypatch.setattr(MODULE, 'NOTICE_JSON', pj)
    monkeypatch.setattr(MODULE, 'NOTICE_MD', md)
    monkeypatch.setattr(MODULE, 'NOTICE_SCHEMA', ps)


def test_validate_fails_closed_without_history_git_show(monkeypatch):
    dummy_notice_files(monkeypatch)
    monkeypatch.setattr(MODULE, 'resolve_record_commit', lambda: REC)

    def no_history(commit, relative_path):
        raise GitHistoryError('history unavailable')
    monkeypatch.setattr(MODULE, 'git_show', no_history)
    with pytest.raises(GitHistoryError, match='history unavailable'):
        MODULE.load_inputs()
    with pytest.raises(GitHistoryError, match='history unavailable'):
        MODULE.validate_notice()


def test_validate_fails_closed_without_history_shallow(monkeypatch):
    dummy_notice_files(monkeypatch)
    monkeypatch.setattr(MODULE, 'git', fake_shallow_git(0, 'true\n'))
    with pytest.raises(AuthorityError, match='shallow'):
        MODULE.validate_notice()


def test_git_show_error_names_full_sha_and_fetch_hint():
    missing = 'e' * 40
    with pytest.raises(GitHistoryError, match='git show failed') as e:
        MODULE.git_show(missing, 'registry/archive_assessment_applicability_authority_v2.json')
    assert missing in str(e.value) and 'fetch full history (git fetch --unshallow)' in str(e.value)
    with pytest.raises(AuthorityError, match='40-character'):
        MODULE.git_show('1544dc1', 'registry/x.json')
    with pytest.raises(AuthorityError, match='repo-relative'):
        MODULE.git_show(PUB, '../x')


# ---- committed files, tamper and bytes (D-15) ----

def test_validate_notice_accepts_unmutated_notice_from_temp_files(monkeypatch, capsys):
    write_set(monkeypatch)
    capsys.readouterr()
    MODULE.validate_notice()
    assert capsys.readouterr().out.strip() == 'PASS'


def test_committed_notice_files_validate(capsys):
    require_history(ROOT, commits=FROZEN_COMMITS)
    capsys.readouterr()
    MODULE.validate_notice()
    assert capsys.readouterr().out.strip() == 'PASS'
    for p in (MODULE.NOTICE_JSON, MODULE.NOTICE_MD, MODULE.NOTICE_SCHEMA):
        assert b'\r' not in p.read_bytes(), p
    assert MODULE.contains_absolute(MODULE.load(MODULE.NOTICE_JSON)) is False


def tamper(notice, path, new=None):
    parent = notice
    for k in path[:-1]:
        parent = parent[k]
    old = parent[path[-1]]
    if new is None:
        new = 'd' * 40 if str(path[-1]).endswith('commit') else 'X' + str(old)
    parent[path[-1]] = new
    return old, new


CONST_PATHS = [
    ('pin', 'authority_id'), ('pin', 'version'), ('pin', 'publication_commit'), ('pin', 'publication_record_commit'),
    ('supersedes', 'authority_id'), ('supersedes', 'version'), ('supersedes', 'commit'),
    ('supersedes', 'previous', 'authority_id'), ('supersedes', 'previous', 'version'), ('supersedes', 'previous', 'commit'),
    ('what_changed', 'supersedes_moved', 'from_version'), ('what_changed', 'supersedes_moved', 'from_commit'),
    ('what_changed', 'supersedes_moved', 'to_version'), ('what_changed', 'supersedes_moved', 'to_commit'),
    ('digest_scope_error', 'previous_version'), ('verify', 'repository_url'),
]


@pytest.mark.parametrize('path', CONST_PATHS)
def test_validate_rejects_tampered_cited_constant_by_schema(monkeypatch, path):
    cached_pinned_run(monkeypatch)
    notice = build()
    tamper(notice, path)
    with pytest.raises(jsonschema.ValidationError) as e:
        MODULE.validate_notice_object(notice, inputs=args())
    assert e.value.validator == 'const' and list(e.value.path) == list(path)
    write_set(monkeypatch, notice=notice)
    with pytest.raises(AuthorityError, match='notice JSON differs from a fresh build'):
        MODULE.validate_notice()


@pytest.mark.parametrize('key', ['authority_sha256', 'manifest_sha256'])
def test_validate_rejects_tampered_cited_digest_by_derivation(monkeypatch, key):
    cached_pinned_run(monkeypatch)
    notice = build()
    notice['pin'][key] = '0' * 64
    jsonschema.Draft202012Validator(MODULE.schema()).validate(notice)
    with pytest.raises(AuthorityError, match='notice differs from the values derived from the frozen inputs'):
        MODULE.validate_notice_object(notice, inputs=args())
    write_set(monkeypatch, notice=notice)
    with pytest.raises(AuthorityError, match='notice JSON differs from a fresh build'):
        MODULE.validate_notice()


DERIVATION_PATHS = [
    ('verify', 'steps', 0, 'checkout'), ('verify', 'steps', 1, 'checkout'),
    ('verify', 'steps', 0, 'commands', 2), ('verify', 'steps', 1, 'commands', 0),
    ('hayes_side_changes_needed', 0),
    ('digest_scope_error', 'previous_commit'), ('digest_scope_error', 'computed_at'),
    ('what_changed', 'decisions_digest', 'recomputed_at'),
    *[('lineage', i, 'recomputed_at') for i in range(7)],
]


@pytest.mark.parametrize('path', DERIVATION_PATHS)
def test_validate_rejects_tampered_cited_commit_by_derivation(path):
    notice = MODULE.build_notice(*args())
    parent = notice
    for k in path[:-1]:
        parent = parent[k]
    old = parent[path[-1]]
    new = re.sub(r'[0-9a-f]{40}', 'd' * 40, old)
    assert new != old
    parent[path[-1]] = new
    jsonschema.Draft202012Validator(MODULE.schema()).validate(notice)
    with pytest.raises(AuthorityError, match='notice differs from the values derived from the frozen inputs'):
        MODULE.validate_notice_object(notice, inputs=args())


def test_const_and_derivation_paths_match_the_schema():
    def leaf(path):
        n = MODULE.schema()
        for k in path:
            n = n['items'] if isinstance(k, int) else n['properties'][k]
        return n
    for path in CONST_PATHS:
        assert 'const' in leaf(path), path
    for path in DERIVATION_PATHS:
        assert 'const' not in leaf(path) and 'enum' not in leaf(path), path


def test_validate_rejects_tampered_markdown_bytes(monkeypatch):
    cached_pinned_run(monkeypatch)
    write_set(monkeypatch, md_text=MODULE.render_markdown(build()) + ' ')
    with pytest.raises(AuthorityError, match='notice Markdown differs from a fresh build'):
        MODULE.validate_notice()


def test_validate_rejects_tampered_schema_bytes(monkeypatch):
    loosened = MODULE.schema()
    loosened['additionalProperties'] = True
    write_set(monkeypatch, schema_obj=loosened)
    with pytest.raises(AuthorityError, match='notice schema differs from a fresh build'):
        MODULE.validate_notice()


def test_validate_rejects_tampered_notice_json_bytes(monkeypatch):
    write_set(monkeypatch)
    MODULE.NOTICE_JSON.write_bytes(MODULE.NOTICE_JSON.read_bytes() + b' ')
    with pytest.raises(AuthorityError, match='notice JSON differs from a fresh build'):
        MODULE.validate_notice()


def test_validate_reports_ungenerated_files(monkeypatch):
    monkeypatch.setattr(MODULE, 'NOTICE_JSON', TMP / 'absent.json')
    with pytest.raises(AuthorityError, match='not generated'):
        MODULE.validate_notice()


NOT_IN_HISTORY = 'the frozen commit ' + 'd' * 40 + ' is not in the repository history'
RECORD_BINDING = 'NOTICE_PUBLICATION_COMMIT differs from the publication_commit named by the frozen publication record'


@pytest.mark.parametrize('name, value, match', [
    ('NOTICE_PUBLICATION_COMMIT', 'd' * 40, NOT_IN_HISTORY),
    ('NOTICE_RECORD_COMMIT', 'd' * 40, NOT_IN_HISTORY),
    ('NOTICE_PUBLICATION_COMMIT', P202, RECORD_BINDING),
    ('NOTICE_RECORD_COMMIT', P202, 'the publication commit is not an ancestor of the record commit'),
])
def test_validate_rejects_tampered_frozen_constant(monkeypatch, name, value, match):
    require_history(ROOT, commits=FROZEN_COMMITS)
    monkeypatch.setattr(MODULE, name, value)
    with pytest.raises(AuthorityError, match=match):
        MODULE.load_inputs()


def test_record_binding_rejects_a_record_naming_another_commit(monkeypatch):
    record = args()[3]
    record['publication_commit'] = P202
    serve_edited(monkeypatch, REC, MODULE.PUBLICATION_RECORD, record)
    with pytest.raises(AuthorityError, match=RECORD_BINDING):
        MODULE.load_inputs()


def test_frozen_constants_match_git():
    require_history(ROOT, commits=FROZEN_COMMITS)
    for short, full in (('1544dc1', PUB), ('87a46d1', REC), ('ae15c74', P202), ('31addfa', P201)):
        assert git('rev-parse', short).stdout.decode().strip() == full
    changed = [p for p in git('diff', '--name-only', PUB, REC).stdout.decode().split() if not p.startswith('.planning/')]
    assert changed == ['registry/archive_assessment_applicability_authority_v2_publication_record.json']
    assert git('rev-parse', REC + '^').stdout.decode().strip() == PUB
    assert git('merge-base', '--is-ancestor', PUB, REC).returncode == 0
    assert MODULE.resolve_record_commit() == REC


# ---- content ----

def test_built_notice_counts_and_rules():
    d = build()['decisions']
    assert (d['decided_count'], d['rule_count'], d['no_rule_count'], d['not_yet_decided_count']) == (21, 3, 18, 59)
    rules = {r['control_id']: r['rule']['conditions'] for r in d['rules']}
    assert rules == {'EMS-CTRL-030': [{'field': 'production', 'state': F}], 'EMS-CTRL-039': [{'field': 'production', 'state': F}], 'EMS-CTRL-052': [{'field': 'ai_enabled', 'state': F}]}
    assert all(r['machine_form'] == MODULE.rule_text(r['rule']) for r in d['rules'])
    assert d['governance_decisions_sha256'].startswith('4e746d1f') and d['decisions_changed'] is False


def test_built_notice_what_changed():
    n = build()
    wc = n['what_changed']
    assert wc['negative_mutation_count'] == 29
    assert [m['id'] for m in n['mutations']] == [t['id'] for t in negative()['negative_invariant_tests']]
    assert wc['closed_schema_levels']['count'] == 16 == len(wc['closed_schema_levels']['paths'])
    assert (wc['row_comparison']['rows_differing'], wc['row_comparison']['rows_compared']) == (0, 80)
    assert wc['supersedes_moved'] == {'from_version': '2.0.1', 'from_commit': P201, 'to_version': '2.0.2', 'to_commit': P202}
    assert wc['decisions_digest']['recomputed_at'] == P202
    first = n['hayes_side_changes_needed'][0]
    assert PUB in first and P202 in first and P201 in first
    assert n['pin']['publication_commit'] == PUB and n['pin']['publication_record_commit'] == REC and n['pin']['version'] == '2.0.3'


def at_pin_deferred_literal():
    src = git('show', f'{PUB}:{PUBLISHER_REL}').stdout.decode('utf-8')
    m = re.search(r"^AT_PIN_DEFERRED = '([^']*)'", src, re.MULTILINE)
    assert m
    return m.group(1)


def test_verify_section():
    v = build()['verify']
    assert v['repository_url'] == 'https://github.com/OscarMackJr/ems.git'
    assert 'python -m pip install -r requirements.txt jsonschema==4.26.0' in v['prerequisites']
    s1, s2, s3 = v['steps']
    assert 'git checkout ' + PUB in s1['commands'] and any('--validate --at-pin' in c for c in s1['commands'])
    assert 'git checkout ' + REC in s2['commands'] and any(c.endswith('--validate') for c in s2['commands'])
    assert 'git checkout ' + MODULE.REMOTE_BRANCH in s3['commands'] and any(c.endswith('--validate') and MODULE.SCRIPT_REL in c for c in s3['commands'])
    assert not re.search(r'[0-9a-f]{40}', ' '.join(s3['commands']) + s3['checkout'])
    assert len(v['steps']) == 3 and len(v['outcomes']) == 5
    assert [o['action'] for o in v['outcomes'][:3]] == ['Run step 2.', 'Run step 3.', f'Re-pin to {PUB}.']
    assert [o for o in v['outcomes'] if 'Re-pin' in o['action']] == [v['outcomes'][2]]
    assert v['outcomes'][2]['case'].startswith('Step 3 prints PASS') and 'steps 1, 2 and 3 all print PASS' in v['outcomes'][2]['meaning']
    assert REC not in v['outcomes'][2]['case'] and not any('step 2 or step 3' in o['case'].lower() for o in v['outcomes'])
    assert 'any later commit' not in MODULE.jtext({'steps': v['steps'], 'outcomes': v['outcomes']})
    require_history(ROOT, commits=FROZEN_COMMITS)
    assert v['at_pin_deferred'] == at_pin_deferred_literal()


def test_no_forbidden_words_in_rendered_text():
    n = build()
    text = MODULE.render_markdown(n) + MODULE.jtext(n)
    for word in MODULE.FORBIDDEN_WORDS:
        assert not re.search(rf'\b{word}\b', text, re.IGNORECASE)
    assert '\r' not in text and MODULE.FORBIDDEN_WORDS == ('best', 'critical', 'important', 'recommended', 'highest')


def test_markdown_content():
    n = build()
    text = MODULE.render_markdown(n)
    assert text.startswith('# ') and 'This file is generated by' in text.split('\n')[2]
    assert '## How to verify' in text
    for d in n['digest_scope_error']['digests']:
        assert d['raw_sha256'] in text and d['lf_sha256'] in text
    for e in n['lineage']:
        assert e['sha256'] in text
    assert MODULE.DUAL_ROLE_STATEMENT in text and PUB in text and REC in text and P202 in text


def test_schema_closes_every_object_level():
    s = MODULE.schema()
    assert s['additionalProperties'] is False and s['required'] == MODULE.NOTICE_KEYS

    def walk(node):
        if isinstance(node, dict):
            if node.get('type') == 'object':
                assert node.get('additionalProperties') is False, node
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)
    walk(s)


def test_dual_role_statement_must_match_published_statement():
    n = build()
    n['dual_role_statement'] += ' Edited.'
    with pytest.raises(AuthorityError, match='dual role'):
        MODULE.validate_notice_object(n, inputs=args())


# ---- CLI ----

def frozen_bytes():
    return {p: p.read_bytes() for p in (MODULE.NOTICE_JSON, MODULE.NOTICE_MD, MODULE.NOTICE_SCHEMA)}


@pytest.mark.parametrize('argv', [[], ['--build', '--validate'], ['--emit-schema', '--build']])
def test_cli_rejects_missing_and_combined_modes(argv):
    before = frozen_bytes()
    r = subprocess.run([sys.executable, str(SCRIPT), *argv], cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 2, r.stderr
    assert frozen_bytes() == before


# ---- live files are never executed (D-01) ----

def _rm_readonly(func, path, exc):
    Path(path).chmod(stat.S_IWRITE)
    func(path)


def make_clone(name):
    require_history(ROOT, commits=FROZEN_COMMITS)
    clone = TMP / name
    if clone.exists():
        shutil.rmtree(clone, onerror=_rm_readonly)
    cloned = subprocess.run(['git', '-c', 'core.longpaths=true', 'clone', '--shared', '-q', str(ROOT), str(clone)], capture_output=True)
    if cloned.returncode != 0:
        pytest.fail(f'git clone --shared of {ROOT} failed: {cloned.stderr.decode(errors="replace")}', pytrace=False)
    assert git('config', 'core.longpaths', 'true', cwd=clone).returncode == 0
    for p in (SCRIPT, MODULE.NOTICE_JSON, MODULE.NOTICE_MD, MODULE.NOTICE_SCHEMA):
        dest = clone / p.relative_to(ROOT)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(p, dest)
    return clone


def run_in_clone(clone, mode):
    r = subprocess.run([sys.executable, MODULE.SCRIPT_REL, mode], cwd=clone, capture_output=True, text=True)
    lines = [line for line in (r.stdout + r.stderr).splitlines() if line.strip()]
    return r.returncode, (lines[-1] if lines else '')


def assert_live_edit_does_not_change_notice(clone, edit):
    before = run_in_clone(clone, '--validate')
    assert before == (0, 'PASS'), f'--validate baseline must be PASS for this test to be meaningful: {before!r}'
    assert run_in_clone(clone, '--build')[0] == 0
    json_before = (clone / MODULE.rel(MODULE.NOTICE_JSON)).read_bytes()
    md_before = (clone / MODULE.rel(MODULE.NOTICE_MD)).read_bytes()
    edit()
    assert run_in_clone(clone, '--validate') == (0, 'PASS')
    assert run_in_clone(clone, '--build')[0] == 0
    assert (clone / MODULE.rel(MODULE.NOTICE_JSON)).read_bytes() == json_before
    assert (clone / MODULE.rel(MODULE.NOTICE_MD)).read_bytes() == md_before


def test_live_publisher_and_decisions_builder_edit_does_not_change_notice():
    clone = make_clone('clone')

    def edit():
        for rel_path in (PUBLISHER_REL, DECISIONS_BUILDER_REL):
            (clone / rel_path).write_text("raise SystemExit('mutated live file executed')\n", encoding='utf-8', newline='\n')
    assert_live_edit_does_not_change_notice(clone, edit)


def test_live_data_file_edit_does_not_change_notice():
    clone = make_clone('clone-data')
    lineage = MODULE.pinned_json(PUB, MODULE.AUTHORITY)['source_lineage']
    live_reads = [e['relative_path'] for e in lineage.values() if isinstance(e, dict) and 'relative_path' in e and 'commit' not in e]
    assert 'registry/archive_assessment_governance_decisions.json' in live_reads
    assert any(p.startswith('generated/archive-assessment/ems-aa1') for p in live_reads)
    assert any(p.startswith('generated/archive-assessment/ems-aa2') for p in live_reads)
    out = MODULE.rel(MODULE.OUT)
    tampered = sorted({*MODULE.PINNED_DATA, *live_reads, MODULE.rel(MODULE.AUTHORITY), MODULE.rel(MODULE.SCHEMA), MODULE.rel(MODULE.SIGNOFF),
                       MODULE.rel(MODULE.PUBLICATION_RECORD), f'{out}/{MODULE.N_NEGATIVE}', f'{out}/{MODULE.N_TRACE}', f'{out}/{MODULE.N_MANIFEST}'})

    def edit():
        for rel_path in tampered:
            dest = clone / rel_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text('{"tampered": true}\n', encoding='utf-8', newline='\n')
    assert_live_edit_does_not_change_notice(clone, edit)


def test_git_show_passes_double_dash(monkeypatch):
    seen = []

    def fake_run(argv, **kwargs):
        seen.append(list(argv))
        return subprocess.CompletedProcess(argv, 0, stdout=b'x', stderr=b'')

    monkeypatch.setattr(MODULE.subprocess, 'run', fake_run)
    assert MODULE.git_show(PUB, 'registry/x.json') == b'x'
    assert seen[0][-1] == '--' and seen[0][:3] == ['git', 'show', f'{PUB}:registry/x.json']


@pytest.mark.parametrize('stderr, long_path_hint', [
    (b"fatal: invalid object name 'eeee'.", False),
    (b"fatal: path 'registry/x.json' does not exist in 'eeee'", False),
    (b"fatal: failed to stat 'eeee:registry/x.json': Filename too long", True),
])
def test_git_show_error_hint_names_long_paths_only_when_git_reports_them(monkeypatch, stderr, long_path_hint):
    monkeypatch.setattr(MODULE.subprocess, 'run', lambda argv, **kwargs: subprocess.CompletedProcess(argv, 128, stdout=b'', stderr=stderr))
    with pytest.raises(GitHistoryError, match='git show failed') as e:
        MODULE.git_show('e' * 40, 'registry/x.json')
    assert 'fetch full history (git fetch --unshallow)' in str(e.value)
    assert ('core.longpaths' in str(e.value)) is long_path_hint


def test_notice_has_long_path_prerequisite():
    v = build()['verify']
    assert any('core.longpaths' in p for p in v['prerequisites'])
    assert len(v['prerequisites']) == 5
    long_path = [p for p in v['prerequisites'] if 'core.longpaths' in p]
    assert len(long_path) == 1
    assert 'step 1' in long_path[0] and 'step 3' not in long_path[0]
    assert 'git clone -c core.longpaths=true' in long_path[0] and 'git config --global core.longpaths true' in long_path[0]


def test_step2_wording_does_not_overstate():
    notice = build()
    pass_means = notice['verify']['steps'][1]['pass_means']
    assert 'enforced by step 3' in pass_means and 'all three steps' in pass_means
    old_step2 = 'PASS means the publication record at this commit names'
    old_row = 'The publication record binds the pin'
    assert old_step2 not in pass_means
    text = json.dumps(notice)
    assert old_step2 not in text and old_row not in text
    md = MODULE.NOTICE_MD.read_text(encoding='utf-8')
    assert old_step2 not in md and old_row not in md
    assert 'core.longpaths' in md

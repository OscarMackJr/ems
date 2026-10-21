import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts' / 'publish_archive_assessment_applicability_authority_v2.py'
SPEC = importlib.util.spec_from_file_location('aa3_authority_v2_claims', SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)

CLAIM = 'CRLF_TO_LF'
RECORD = MODULE.PUBLICATION_RECORD
OUT = MODULE.OUT
CERT = OUT / MODULE.N_CERT
MANIFEST = OUT / MODULE.N_MANIFEST
TRACE = OUT / MODULE.N_TRACE
SIGNOFF = MODULE.SIGNOFF
REPLY = ROOT / 'registry' / 'archive_assessment_demo3_w1_req_001_reply.json'
REPLY_DOC = ROOT / 'docs' / 'DEMO3_W1_REQ_001_REPLY.md'
REPLY_PROSE = 'both digests are computed over bytes with CRLF replaced by LF'


def read(p: Path): return json.loads(p.read_bytes().decode('utf-8'))
def lf_sha(b): return hashlib.sha256(b.replace(b'\r\n', b'\n')).hexdigest()
def lf_digest(p: Path): return lf_sha(p.read_bytes())

def git(*args):
    r = subprocess.run(['git', *args], cwd=ROOT, capture_output=True)
    return subprocess.CompletedProcess(r.args, r.returncode, r.stdout, r.stderr.decode('utf-8', 'replace').strip())

def git_ready():
    try: r = git('rev-parse', '--is-shallow-repository')
    except OSError: return 'git is unavailable'
    if r.returncode != 0: return 'not a git repository'
    if r.stdout.decode().strip() == 'true': return 'shallow repository, history is incomplete'
    return None


# Files with eol=lf in .gitattributes have raw == LF bytes; the claim string and the LF recompute are still both asserted.

def test_publication_record_normalisation_claim():
    rec = read(RECORD)
    assert rec['digest_normalisation'] == CLAIM
    assert rec['authority_sha256'] == lf_digest(MODULE.AUTHORITY)
    assert rec['manifest_sha256'] == lf_digest(MANIFEST)


def test_certification_normalisation_claim():
    cert = read(CERT)
    assert cert['digest_normalisation'] == CLAIM
    assert cert['authority_sha256'] == lf_digest(MODULE.AUTHORITY)
    assert cert['authority_sha256'] == MODULE.sha_text(MODULE.jtext(read(MODULE.AUTHORITY)))
    assert cert['schema_sha256'] == lf_digest(MODULE.SCHEMA)
    assert cert['signoff_sha256'] == lf_digest(SIGNOFF)


def test_manifest_artifacts_normalisation_claim():
    manifest = read(MANIFEST)
    assert manifest['digest_normalisation'] == CLAIM
    assert manifest['artifacts']
    for art in manifest['artifacts']:
        assert lf_digest(ROOT / art['relative_path']) == art['sha256'], art['relative_path']


def test_manifest_publisher_script_normalisation_claim():
    reason = git_ready()
    if reason: pytest.skip(reason)
    manifest = read(MANIFEST)
    assert manifest['publisher_script']['sha256_normalisation'] == CLAIM
    sha = read(RECORD)['publication_commit']
    shown = git('show', f"{sha}:{manifest['publisher_script']['relative_path']}")
    assert shown.returncode == 0
    assert lf_sha(shown.stdout) == manifest['publisher_script']['sha256']


def test_traceability_decision_record_normalisation_claim():
    trace = read(TRACE)
    expected = lf_digest(MODULE.GOVERNANCE_DECISIONS)
    assert trace['decision_records']
    for rec in trace['decision_records']:
        assert rec['decision_record_digest_normalisation'] == CLAIM
        assert rec['decision_record_sha256'] == expected


def test_signoff_authority_normalisation_claim():
    signoff = read(SIGNOFF)
    assert signoff['authority_sha256_normalisation'] == CLAIM
    assert signoff['authority_sha256'] == lf_digest(MODULE.AUTHORITY)


def test_reply_pin_normalisation_claim():
    # Read only: the sent 2.0.1 reply and its builder are never regenerated here (D-14).
    pin = read(REPLY)['pin']
    assert pin['digest_normalisation'] == CLAIM
    # Compare against the 2.0.1 blobs at the pinned publication commit, not the working files, so a later republication does not break the claim.
    reason = git_ready()
    if reason: pytest.skip(reason)
    for key, path in (('authority_sha256', MODULE.AUTHORITY), ('manifest_sha256', MANIFEST)):
        shown = git('show', f"{pin['publication_commit']}:{MODULE.rel(path)}")
        assert shown.returncode == 0, shown.stderr
        assert pin[key] == lf_sha(shown.stdout), key
    assert REPLY_PROSE in REPLY_DOC.read_bytes().decode('utf-8')

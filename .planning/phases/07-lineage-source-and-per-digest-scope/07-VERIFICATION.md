---
phase: 07-lineage-source-and-per-digest-scope
verified: 2026-10-20T00:00:00Z
status: passed
score: 4/4 must-haves verified
overrides_applied: 0
---

# Phase 7 Verification

**Goal:** Every digest in the AA3 source_lineage declares how it was computed and can be recomputed from a committed file, including the AA1 manifest.

| # | Truth (ROADMAP SC) | Status | Evidence |
|---|---|---|---|
| 1 | AA1 manifest committed in its own commit, `-text` in .gitattributes, raw sha256 = f0da8e2e... | VERIFIED | Commit bb7c067 touches only .gitattributes (+1 line) and the manifest. `.gitattributes` has `generated/archive-assessment/ems-aa1/ems_aa1_analysis_artifact_manifest.json -text`. `sha256sum` of the working file = f0da8e2e45c306ccc42ae96f25a19922668f3eedecdb26006f13514e24ad9b4b. |
| 2 | Per-digest normalisation + repo-relative path (+ commit where relevant); no global field | VERIFIED | Publisher v2 `digest_entry(...)` builds each lineage entry with relative_path, sha256 and normalisation. `supersedes` and `v1_baseline` carry a commit. The validator rejects a `digest_normalisation` key in source_lineage (line 307). The only remaining `digest_normalisation` uses are in the certification, manifest and publication record, not in source_lineage. |
| 3 | Validator recomputes each digest from the cited path or commit under the declared normalisation; fails on tampering | VERIFIED | `validate_lineage` (lines 327-345) uses `git_show` for commit-pinned entries and reads the working file otherwise. It applies NORMALISERS, requires the declared normalisation to equal EXPECTED_NORMALISATION, and rejects bad paths and a missing commit. It is called from the validation path (line 660). tests/test_archive_assessment_lineage_validation.py has 28 test functions covering tampered file, changed digest, flipped normalisation, bad commit, missing path and git unavailable. Orchestrator run: all pass, none skipped. |
| 4 | aa1/aa2_closure/aa2_approval are RAW_BYTES; truly LF-normalised digests are CRLF_TO_LF; pytest covers both | VERIFIED | EXPECTED_NORMALISATION (line 75) and the build code (lines 167-170). Orchestrator ran validate_lineage on the real built authority: PASS. Tests cover both kinds, including `test_d12_raw_and_lf_digests_differ_on_crlf_fixture` and `test_real_lineage_declares_expected_normalisations`. |

## Requirements

| ID | Status |
|---|---|
| LIN-01 | SATISFIED (per-digest normalisation; global field forbidden) |
| LIN-02 | SATISFIED (validate_lineage recomputes; mismatch raises AuthorityError) |
| LIN-03 | SATISFIED (manifest committed, -text, pinned hash verified) |

All three IDs appear in REQUIREMENTS.md and are mapped to Phase 7. No orphaned requirements. REQUIREMENTS.md checkboxes still read "Pending" and need ticking at close-out (bookkeeping, not a gap).

## Spot checks and tests

The orchestrator's results are authoritative:
- `pytest tests -k archive_assessment`: 570 passed, 3 failed, 0 skipped.
- The 3 failures are exactly the accepted red window (certified 2.0.1 real-file tests), which closes at Phase 9.
- Review fixes WR-01..05 are present as commits 769ddc9, fb945f5, c0c0c05, 702c22e and aeb312c, and their tests exist.
- `--validate` fails on the committed 2.0.1 file because it has the old lineage shape. This is expected until Phase 9 and is not a gap.

## Anti-patterns

No TBD, FIXME or XXX debt markers were scanned for in this pass. No stubs were found in the verified code paths.

## Gaps

None.

## Human verification

None required.

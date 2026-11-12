---
phase: 09-certified-republication-2-0-2
plan: 02
subsystem: DEMO3 reply builder
tags: [D-01, D-02, D-03, PUB-07]
requirements: [PUB-07]
key-files:
  modified:
    - scripts/build_archive_assessment_demo3_w1_req_001_reply.py
    - tests/test_archive_assessment_demo3_w1_req_001_reply.py
metrics:
  completed: 2026-11-12
---

# Phase 9 Plan 02: Freeze the DEMO3 reply validator on 2.0.1 Summary

The reply builder and validator now take every input from git history. The authority, sign-off, governance decisions, manifest and decision traceability are read at REPLY_PUBLICATION_COMMIT (31addfa…), and the publication record at REPLY_RECORD_COMMIT (4d9b7c1…). Digests are computed over LF-normalised blobs. validate_signoff is called with the 2.0.1 id and version taken from the record. resolve_record_commit keeps the shallow-clone check verbatim and no longer uses `git log`; it confirms that the constant commit exists and is an ancestor of HEAD. push_check binds to REPLY_PUBLICATION_COMMIT. The reply JSON, MD and schema bytes are unchanged, and the rebuilt reply is byte-equal to the committed one.

## Commits
- 82cff90: feat — frozen validator (constants, pinned_* helpers, git_show inputs, resolve_record_commit)
- 02a4ea3: test — frozen-constant checks against git, reply-bytes tamper, constant tamper, fail closed without history (shallow and git_show), push-check binding, independence from the live version, missing or non-ancestor record commit

## Verification
- `python scripts/build_archive_assessment_demo3_w1_req_001_reply.py --validate` gives PASS (orchestrator).
- The orchestrator's pytest run of the reply module gives 63 passed, 1 failed (see deviation).
- Acceptance greps: REPLY_PUBLICATION_COMMIT ×11; no `'log'` git call; no live reads of the V2 artifacts in the build or validate paths.
- `git diff` on the reply artifacts is empty.
- Each commit touches only its one intended file, staged by explicit path.

## Deviations from Plan
- **Reply module not fully green.** test_publisher_still_valid_and_digest_matches_manifest is still red. It is a baseline red that exercises the live `V2.validate_published()` and the live script digest against the live manifest, not the reply validator, so freezing the reply cannot clear it. It is kept unchanged as an accepted red that clears when 2.0.2 is published in 09-04. Every reply-validator test passes.

## Self-Check: PASSED

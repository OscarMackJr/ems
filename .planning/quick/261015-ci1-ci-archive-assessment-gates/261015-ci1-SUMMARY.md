---
quick_id: 261015-ci1
slug: ci-archive-assessment-gates
status: complete
completed: 2026-10-15
commit: f767c64
key-files:
  modified:
    - .github/workflows/ems-validate.yml
---

# Quick Task 261015-ci1: Run the archive-assessment gates in CI — Summary

Added an `archive-assessment` job to `.github/workflows/ems-validate.yml`: full-history checkout (`fetch-depth: 0`), Python 3.12, `requirements.txt` plus `jsonschema` and `pytest`, then `pytest tests -k archive_assessment` and the five `--validate` CLIs. Added a `workflow_dispatch` trigger. The existing `validate` job is unchanged.

## Verification

- Workflow YAML parses: jobs `validate`, `archive-assessment`; triggers `pull_request`, `push` (main), `workflow_dispatch`
- Same commands pass locally on Windows: 492 passed; 5 validators PASS
- Not yet run on ubuntu-latest (needs a push and a manual dispatch or a PR)

## Notes

- Real-file tests still `skipif` when published artifacts are absent (audit finding, 06-REVIEW WR-02); CI reports those as skips, not failures.
- Executed inline (see 261014-vau SUMMARY for why).

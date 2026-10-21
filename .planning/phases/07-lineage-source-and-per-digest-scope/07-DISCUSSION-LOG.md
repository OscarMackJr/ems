# Phase 7 Discussion Log

**Date:** 2026-10-20
**Areas discussed:** Lineage shape, AA1 manifest home, Validator design, Normalisation sweep

## Lineage shape
| Question | Options | Selected |
|----------|---------|----------|
| Per-digest scope expression | Objects per digest / Flat keys + scope map / Flat keys + sibling fields | Objects per digest |
| Global `digest_normalisation` | Remove / Rename to default | Remove |
| Nested entries get explicit normalisation | Yes, every digest / Only the three raw ones | Yes, every digest |
| Vocabulary | Enum RAW_BYTES \| CRLF_TO_LF / Open string | Enum |

## AA1 manifest home
| Question | Options | Selected |
|----------|---------|----------|
| Repo location | generated/archive-assessment/ems-aa1/ / registry/ | generated/archive-assessment/ems-aa1/ |
| Hash mismatch | Stop, don't commit / Try CRLF/LF variants | Stop, don't commit |
| Source on disk | Under C:\temp\standars\Pass4_5 / Search C:\temp\standars | Under Pass4_5 |

Note: there was no hash match under Pass4_5. The file was found already in the repo at `generated/archive-assessment/ems-aa1/ems_aa1_analysis_artifact_manifest.json` (gitignored). Its raw-byte SHA-256 matches `f0da8e2e…` exactly, and it has 87 CRLF line endings.

## Validator design
| Question | Options | Selected |
|----------|---------|----------|
| Location | Inside publisher --validate / Separate verifier script | Inside publisher --validate |
| Recompute source | Working tree + git for commit-pinned / Working tree only | Working tree + git |
| Commit the 13 AA1 artifacts | Manifest only / Manifest + artifacts | Manifest only |
| No git history | Fail closed / Skip with SKIPPED | Fail closed |

## Normalisation sweep
| Question | Options | Selected |
|----------|---------|----------|
| Other CRLF_TO_LF claims | Audit + test, change only if wrong / Restructure all / source_lineage only | Audit + test |
| DEMO3 reply | Leave as is / Regenerate later | Leave as is |

## Deferred
- Commit the 13 AA1 analysis artifacts
- Re-point the DEMO3 reply to 2.0.2

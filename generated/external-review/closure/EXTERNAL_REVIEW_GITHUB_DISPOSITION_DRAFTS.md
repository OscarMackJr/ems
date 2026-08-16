# External Review — GitHub Disposition Drafts

No live comments or review threads were posted or resolved; these are drafts only.

## ERF-001 — Synthetic evidence storage transition and payload ambiguity

Disposition: `ADDRESSED_TO_CURRENT_AUTHORITY`.

P3 establishes STAGED_LOCAL -> CSO_APPROVED_STORAGE; no unapproved Egnyte payload schema was invented.

## ERF-002 — Unknown or malformed evaluator results must fail closed

Disposition: `REMEDIATED`.

onboarding_orchestrator validates known dispositions and result contract before WS7; focused malformed/unknown tests pass.

## ERF-003 — REPO-003 pilot circuit breaker

Disposition: `REMEDIATED`.

REPO-003 false pilot or production authorization aborts before subsequent workstream initialization.

## ERF-004 — Human decision non-repudiation and supersession

Disposition: `GOVERNANCE_DECISION_REQUIRED`.

Published authority preserves immutable machine results and attributable reviewer decisions; cryptographic signing is not currently approved authority.

## ERF-005 — Retention authority and certification supersession history

Disposition: `REMEDIATED`.

P3 specifies three-year supersession history plus holds and prohibits successor deletion or rewrite of predecessor evidence.

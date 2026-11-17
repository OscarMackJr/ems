---
phase: 14
slug: notice-to-hayes-2-0-3
status: verified
threats_open: 0
asvs_level: 1
created: 2026-11-17
---

# Phase 14 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| git object DB -> executed code | The builder executes the pinned publisher and decisions builder blobs read at 1544dc1 | Python source from public repository history (integrity-sensitive) |
| working tree -> builder | Live publisher, decisions builder and data files could be edited; they must never be read or executed by the notice build | Repository files (integrity-sensitive) |
| authority data -> git/temp paths | Lineage `relative_path` and `commit` values flow into `git show` | Repo-relative paths, 40-hex SHAs |
| builder output -> Hayes | The notice is a signed-off statement to an external assessor | Public notice JSON/MD (integrity-sensitive) |
| notice commands -> Hayes operator shell | Hayes runs the commands the notice prints | Fixed command strings |
| tests -> repository files | Tests must not modify committed notice files or the live publisher | Test outputs |
| builder output -> repository | Generated files become committed artifacts Hayes reads | Notice JSON/MD/schema |
| local repo -> remote | Pushed commits become what Hayes can pin and read | Commits |
| GitHub CLI token -> git process | Credential could cross into a git subprocess | GitHub token (secret) |

---

## Threat Register

Evidence paths: `B` = `scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py`, `T` = `tests/test_archive_assessment_demo3_w1_req_001_notice_2_0_3.py`, `CI` = `.github/workflows/ems-validate.yml`.

| Threat ID | Category | Component | Disposition | Mitigation | Status |
|-----------|----------|-----------|-------------|------------|--------|
| T-14-01 | Tampering / EoP | pinned_mutation_run executing a live or tampered file | mitigate | Current (post WR-01) form verified: B:258-266 materialises PINNED_CODE/PINNED_DATA from `git_show(NOTICE_PUBLICATION_COMMIT, p)` into a TemporaryDirectory; B:269-271 checks pub/builder/builder-V2 `ROOT` resolve inside tmp before any pinned function runs; B:272-273 + B:277-283 `live_git_subprocess` replaces `subprocess` in pub and b.V2 (refuses non-git, forces cwd=live ROOT); B:298-300 LF sha256 of publisher blob == `manifest['publisher_script']['sha256']`; B:324-327 post-run assertion that 13 path constants (3 ROOTs, GOVERNANCE_DECISIONS, V1_AUTHORITY, BUILDER_SCRIPT, both `__file__`, PROPOSALS, DRAFTING_RECORD, ANSWERS, WORDING_APPROVAL, DECISIONS_SCHEMA) resolve inside tmp. Tests: T:170-192 (ROOTs in tmp, git_run toplevel == live ROOT, shim refuses `python`), T:195-200 (digest mismatch), T:674-680 and T:683-699 (live publisher/builder and all live data files tampered in a clone; `--validate` PASS and `--build` byte-identical). | closed |
| T-14-02 | Tampering | path traversal into temp dir | mitigate | Fixed PINNED_CODE/PINNED_DATA tuples B:72-76; `bad_rel` B:97 checked on every path before write in B:259-260 and inside `git_show` B:100 (all git reads route through `git_show`). | closed |
| T-14-03 | Tampering | git option injection via SHA/path | mitigate | `git_show` B:99 `re.fullmatch(r'[0-9a-f]{40}')` on commit, B:100 `bad_rel`, B:101 single `f'{commit}:{relative_path}'` argument; lineage `commit`/`relative_path` from authority data go through `git_show` (B:220-221, B:244); `resolve_record_commit` B:178 re-checks each frozen SHA. Test T:346-353. | closed |
| T-14-04 | Spoofing | shallow/partial clone giving a false PASS | mitigate | `resolve_record_commit` B:170-184: `--is-shallow-repository` must equal `'false'` (B:175), `cat-file -e {sha}^{commit}` (B:178) and `merge-base --is-ancestor ... HEAD` (B:180) for all four frozen commits, plus publication-before-record (B:182); called first in `load_inputs` B:332. CI job sets `fetch-depth: 0` (CI:75). Tests T:277-313, T:339-343. | closed |
| T-14-05 | Repudiation | vacuous rejections | mitigate | Baseline-accepts check on unmutated inputs B:307-316 (`validate_governance_decisions`, `validate_publication`, schema, `validate_signoff`) before `run_mutations` B:318; `check_rerun` B:198-207 requires every outcome rejected, frozen result PASS, and entry-for-entry equality `(id, rejected_by, result)` with the frozen negative-invariant file (D-02). Tests T:112-139, T:157-167. | closed |
| T-14-06 | Information disclosure | temp dir left behind | accept | See Accepted Risks Log AR-14-01. `tempfile.TemporaryDirectory()` context confirmed at B:290. | closed |
| T-14-07 | Repudiation | notice overstating checks | mitigate | Counts/digests computed: `check_rerun` B:396, `lineage_entries` B:413 (recomputes sha256 from git, B:221-223), `digest_scope_error` B:414; `validate_notice_object` B:562 rebuilds and compares (`build_notice(...) != notice`); schema consts on cited values B:530-549. Tests T:398-444. | closed |
| T-14-08 | Spoofing | repository URL from operator config | mitigate | `REPOSITORY_URL` fixed constant B:60; schema `{'const': REPOSITORY_URL}` B:547; no argparse/env input for the URL (B:584-586 has only mode flags). | closed |
| T-14-09 | Tampering | hand edits to generated files | mitigate | `validate_notice` B:572-577 byte-compares LF-normalised JSON, MD and schema with a fresh build. Tests T:460-479. CI runs `--validate` (CI:100). | closed |
| T-14-10 | Tampering | notice and tool disagree on deferred text | mitigate | `at_pin_deferred` taken from pinned module `pub.AT_PIN_DEFERRED` (B:305 prefix check, B:328, B:398, B:433); schema pattern `'^PUBLICATION_RECORD_BINDING: '` B:547. Committed JSON line 372 carries the prefix. | closed |
| T-14-11 | Information disclosure | absolute paths in notice | mitigate | `contains_absolute(notice)` in `validate_notice_object` B:554-555 (helper B:92-96). Test T:373. | closed |
| T-14-12 | Repudiation | tests that cannot fail for their named reason | mitigate | Direct calls with specific `match=`: `check_rerun` T:112-135, `lineage_entries` T:206-210, `digest_scope_error` T:225-248; check ordering in B:198-206 and B:246-253 matches distinct messages. | closed |
| T-14-13 | Tampering | test writes leaking into the repository | mitigate | `write_set` T:93-102 writes to `TMP` and monkeypatches NOTICE_JSON/MD/SCHEMA; clone tests T:639-699 edit only `TMP/<clone>`; CLI test T:625-630 snapshots committed bytes before/after (`frozen_bytes`). | closed |
| T-14-14 | Spoofing | skipped history tests hiding a broken clone | mitigate | No `pytest.skip` in T (grep: none); `require_history` (tests/aa_history.py:38-44) calls `pytest.fail` unless `EMS_ALLOW_NO_HISTORY=1`; fail-closed tests without `require_history` T:251-343 ("never skipped, never reach require_history"). | closed |
| T-14-15 | Tampering | hand edits to generated files | mitigate | Same byte-rebuild `--validate` as T-14-09 (B:572-577); notice MD header states regenerate-only (B:447); CI runs `--validate` at HEAD (CI:100); regeneration commit b23a623 produced by the builder. | closed |
| T-14-16 | Tampering | unrelated work swept into the code commit | mitigate | `git show --name-only` over all phase-14 commits (8c63687..b23a623): only the builder, test, three notice files, ems-validate.yml and `.planning/` files. `.planning/config.json`, `registry/adjudication_rules.json`, `registry/policy_decisions.json` remain ` M` (never committed). | closed |
| T-14-17 | Repudiation | unreviewed wording published | mitigate | D-14 approval recorded in 14-04-SUMMARY.md:49-52 (Oscar Mack "approved", 2026-11-17); second approval after WR-02 regeneration reported by orchestrator (process evidence, not in git). | closed |
| T-14-18 | Tampering | publication, record or frozen notice/reply drift | mitigate | `git diff --stat 1544dc1 HEAD` on publisher, decisions builder, v2 authority, sign-off, governance decisions, v2 schema, `generated/archive-assessment/ems-aa3-v2`: empty. `git diff --stat 87a46d1 HEAD` on publication record, reply (MD+JSON), 2.0.2 notice (MD+JSON), publisher: empty. All paths confirmed tracked (`git ls-files`). | closed |
| T-14-19 | Tampering | unrelated modified files pushed | mitigate | As T-14-16; HEAD b23a623 == origin/feature/ems-aa3-archive-applicability-authority; pushed commits contain only the listed files; unrelated files still unstaged/untracked. | closed |
| T-14-20 | Tampering | authority, record, reply or 2.0.2 notice drift | mitigate | As T-14-18 (both diffs empty at HEAD b23a623 == origin). | closed |
| T-14-21 | Repudiation | notice sent before it is on the remote | mitigate | `send_condition` B:438, committed JSON line 360, MD "## Sending" line 120-122; HEAD == origin verified; CI run 44171475201 success at b23a623 (orchestrator evidence); 14-05-SUMMARY.md:28-40 push checkpoint. | closed |
| T-14-22 | Elevation of privilege | unapproved push, PR, merge or tag | mitigate | 14-05-SUMMARY.md:38-40 (Oscar Mack "push", 2026-11-17); `git tag --points-at HEAD` empty; `gh pr list --head feature/ems-aa3-archive-applicability-authority` empty; second push approval reported by orchestrator. | closed |
| T-14-23 | Information disclosure | GitHub token leaked to files or logs | mitigate | Pushes were plain `git push` (no token env config used, per orchestrator). Strict token grep `gh[pousr]_[A-Za-z0-9]{20,}\|github_pat_[A-Za-z0-9_]{20,}` over the phase dir and the five phase-14 artifacts: no match (rc=1); loose grep only hits 14-05-PLAN.md:118 acceptance text. CI secret-pattern step CI:60-68 present (note: excludes `*.md`). | closed |
| T-14-SC | Tampering | package installs | accept | See Accepted Risks Log AR-14-02. Notice install command pins `jsonschema==4.26.0` (B:61); CI archive-assessment job installs the same pin (CI:85, WR-03). | closed |

*Status: open · closed*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-14-01 | T-14-06 | Temp materialisation uses a `TemporaryDirectory` context (B:290); if cleanup fails the residue is public repository blobs from commit 1544dc1, with no secrets. | Phase 14 plan threat register (plan-time acceptance, Oscar Mack as approving authority) | 2026-11-17 |
| AR-14-02 | T-14-SC | No package is installed by any phase-14 plan. The notice instructs Hayes to install `jsonschema==4.26.0`, the version EMS and CI already use (CI:85). `requirements.txt` remains partly unpinned (pre-existing, out of scope). | Phase 14 plan threat register (plans 01-05) | 2026-11-17 |

---

## Observations (non-blocking, informational)

1. **Execute-before-digest order (T-14-01).** `load_pinned_publisher` runs `spec.loader.exec_module(pub)` and `pub.decisions_builder()` (B:266-267) before the LF digest check against `manifest.publisher_script.sha256` (B:298-300). The executed bytes come from the content-addressed git object at a 40-hex frozen commit whose ancestry is checked first (B:332), so a tampered blob would require rewriting git history; the residual risk is low and within the declared mitigation, but a hash-before-exec order would be stricter.
2. **Decisions builder blob not digest-bound.** Only the publisher blob is compared to a manifest digest; the decisions builder (PINNED_CODE[1]) relies on the frozen-commit read alone. The same content-addressing argument applies.
3. **CI secret scan excludes Markdown.** The CI secret-pattern step (CI:64-65) uses `--exclude='*.md'`, so it does not cover `.planning/` docs or the notice MD; the local strict grep run during this audit covers them.
4. **Register count.** The register contains 24 unique IDs (T-14-01..T-14-23 plus T-14-SC); the orchestrator brief said 23.

## Unregistered Flags

None. No phase-14 SUMMARY.md contains a `## Threat Flags` section.

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-11-17 | 24 | 24 | 0 | gsd-security-auditor (Claude) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-11-17

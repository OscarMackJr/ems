# EMS Demo Pin and 2.0.3 Notice Send Record

Date: 2026-11-19
Status: Recorded
Scope: record-only. No code, registry, or Hayes change is made by this task.

## 1. Demo pin decision

- Demo commit: `755cb275564f44b0af15dcad86267d809fe23f79` (755cb27), tip of `origin/feature/ems-aa3-archive-applicability-authority` (pushed).
- CI "EMS Validate" run 44423016638 (workflow_dispatch, 2026-11-18 23:42 UTC) concluded success at 755cb27.
- Decision: v1.3.0 Phases 17-19 are parked until after the demo (about 2 weeks). Phase 17 has not started. Plan 17-04 (first publisher edit) opens the red window and must not run before the demo.

## 2. Why 755cb27 and not local HEAD

Local HEAD `4efad08f1b01aafb41fefe90c708c45706ff6cb5` (4efad08) is 8 commits ahead of 755cb27: 57bbab5, c57c6a9, 782108c, b8a5a9a, d9e6eac, 6e70f03, 4782e4a, 4efad08. All of them touch `.planning/` only (`git diff --name-only 755cb27 HEAD -- . ':!.planning'` is empty). Non-planning content is identical, and 755cb27 is on the remote with green CI.

## 3. Authority in force at the demo commit

- Authority: EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-2.0.3.
- Published at `1544dc19ba235d732c832d1651895550ed5a265d` (1544dc1), the commit Hayes pins; signed off by Oscar Mack on 2026-11-17.
- Record commit: `87a46d147413bd99e931c71a1ab165eb0903f014` (87a46d1).
- Decisions digest 4e746d1f... unchanged. 21 decided (3 rules, 18 no-rule, AA4-GOV-001..021), 59 NOT_YET_DECIDED.

## 4. Changes between 1544dc1 and 755cb27 outside .planning

- The 2.0.3 notice: `docs/DEMO3_W1_REQ_001_NOTICE_2_0_3.md`, its registry JSON, schema, and builder script.
- `registry/archive_assessment_applicability_authority_v2_publication_record.json`.
- `.github/workflows/ems-validate.yml`.
- Five `tests/` files (Phase 14-16 work).

No decision change.

## 5. Validation evidence

Plain `python scripts/publish_archive_assessment_applicability_authority.py --validate` printed PASS in the working tree on 2026-11-19 (exit 0).

## 6. 2.0.3 notice send record (2.0.3 half of NOTICE-05)

- The notice `docs/DEMO3_W1_REQ_001_NOTICE_2_0_3.md` was sent to Hayes at commit `91d88473129a8996e97da23be58de33076ec5b51` (91d8847, 2026-11-18 09:28 -0500, on the remote).
- Confirmed by the EMS governance authority (Oscar Mack) on 2026-11-18.
- Sources: 16-CONTEXT.md D-01 and 16-REVIEW-CLOSURE.md "Related records".
- Notice content is unchanged since 91d8847. The working tree shows it modified only by line-ending conversion, which is unrelated and must not be staged.
- NOTICE-05 remains Pending overall. The 2.0.4 half (record the 2.0.4 send commit) belongs to Phase 19.

## 7. Known gap for the demo

Hayes Verify's committed demo3/run-service records still pin EMS 62a8955 (AA3 of 2026-08-17), not 1544dc1. No Hayes change is made in this task.

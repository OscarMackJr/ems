# EMS demo script — DEMO3-W1-REQ-001 applicability decisions (authority 2.0.3)

**What to show:** EMS answers a formal request from Hayes Verify about 21 controls. For each of them it publishes
an explicit, machine-readable decision with an authority behind it. Anyone can verify that answer from a public
clone in under a minute. "EMS decided" can always be told apart from "EMS has not decided yet".

**Tags (on origin):**

| Tag | Commit | Role |
|---|---|---|
| `ems-aa3-authority-2.0.3` | `1544dc1` | The pin Hayes cites |
| `ems-demo-2026-12` | `755cb27` | The demo commit |

**Run time:** about 30 s for clone + install + step 1, then about 6 s each for steps 2 and 3. Rehearsed on
2026-11-19 on a fresh clone of the public repo.

## 0. Before the audience (PowerShell, Python 3.12)

```powershell
git clone -c core.longpaths=true https://github.com/OscarMackJr/ems.git C:\ems-demo
cd C:\ems-demo
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt jsonschema==4.26.0
```

## 1. The question (talk, 1 min)

Hayes Verify is an external assessor. It reads EMS read-only at a pinned commit and makes no applicability
decisions itself. It asked EMS about 21 controls: "When is this control not applicable to an archived repository?"

The rules EMS must follow:

- Every not-applicable result needs an explicit rule.
- `UNKNOWN` is never treated as false.
- Absence of evidence is not "not applicable".

## 2. The pinned bytes are certified (step 1)

```powershell
git checkout ems-aa3-authority-2.0.3
.\.venv\Scripts\python.exe scripts/publish_archive_assessment_applicability_authority_v2.py --validate --at-pin
```

**Expect:** `{"status": "PASS", "mode": "AT_PIN", "deferred": ["PUBLICATION_RECORD_BINDING: ..."]}`

**Say:**

- Hash certification covers the authority, the manifest and the lineage.
- The one deferred item is the publication record. It can't exist inside the commit it names, so step 2 checks it.

## 3. The publication is intact at the demo commit (steps 2 and 3)

```powershell
git checkout ems-demo-2026-12
.\.venv\Scripts\python.exe scripts/publish_archive_assessment_applicability_authority_v2.py --validate
.\.venv\Scripts\python.exe scripts/build_archive_assessment_demo3_w1_req_001_notice_2_0_3.py --validate
```

**Expect:** `PASS`, then `PASS`.

**Say:**

- Step 2: the publication files are byte-identical between the pin and here.
- Step 3: the notice sent to Hayes is rebuilt from frozen inputs. The 29 tamper mutations are rerun against the
  pinned publisher, the digests are recomputed, and everything matches.

## 4. The decisions (the point of the demo)

```powershell
.\.venv\Scripts\python.exe C:\temp\standars\ems\.planning\quick\261119-t1l-ems-demo-script\show_decisions.py .
```

**Expect:** 80 controls, broken down as follows.

| State | Count | Controls and authority |
|---|---|---|
| `RULE_PUBLISHED` | 3 | CTRL-030 Disaster Recovery Testing and CTRL-039 Release Approval: not applicable only when `production=KNOWN_FALSE`. CTRL-052 AI Attribution: not applicable only when `ai_enabled=KNOWN_FALSE`. Authorities AA4-GOV-014/016/018. |
| `NO_RULE_WILL_BE_PUBLISHED` | 18 | AA4-GOV-001..021, excluding the three above. |
| `NOT_YET_DECIDED` | 59 | — |

**Say:**

- Rule conditions use only `KNOWN_TRUE` or `KNOWN_FALSE`. An `UNKNOWN` classification can never make a control
  not applicable.
- "No rule" is a decision, not a gap.
- The other 59 controls are explicitly undecided. That is the distinction Hayes can cite.

## 5. Governance (talk, 1 min)

- Each decision was signed off by Oscar Mack as the EMS governance authority. He is also the Hayes Verify
  developer, and that dual role is written into every decision record.
- The drafts were written blind, from the control catalog only. They were committed before any target was seen.
- The notice to Hayes was sent at `91d8847`.

## If something fails on stage

| Symptom | Cause / action |
|---|---|
| `Filename too long` at clone or checkout | Clone with `-c core.longpaths=true`, or use a short root such as `C:\ems-demo`. |
| Step 1 complains about a shallow clone or history | Use a full clone (`git fetch --unshallow`). |
| Plain `--validate` fails at `ems-aa3-authority-2.0.3` | This is by design: the record comes after the pin. Use `--at-pin` there, and plain mode at `ems-demo-2026-12`. |
| Any other failure | Stop and do not improvise. Show the step 1–3 output from the rehearsal record (261119-t1l-SUMMARY.md). |

## Known gap (be ready if asked)

Hayes Verify's committed records still pin EMS `62a8955` (AA3, 2026-08-17), not `1544dc1`. The re-pin is a
Hayes-side change and is not yet made (see 261119-sd5-DEMO-PIN.md).

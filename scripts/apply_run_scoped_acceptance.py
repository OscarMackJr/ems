import argparse
import json
from datetime import UTC, datetime
from pathlib import Path


def load_jsonl(path):
    rows=[]
    if not Path(path).exists():
        return rows
    with Path(path).open("r",encoding="utf-8-sig") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


ap=argparse.ArgumentParser()
ap.add_argument("--batch-id",required=True)
ap.add_argument("--qualified",required=True)
ap.add_argument("--reviewed",required=True)
ap.add_argument("--output",required=True)
ap.add_argument("--batch-owner",required=True)
ap.add_argument("--accept-qualified",action="store_true")
args=ap.parse_args()

qualified=load_jsonl(args.qualified)
reviewed=load_jsonl(args.reviewed)
decisions=[]
errors=[]

for row in qualified:
    if row.get("batch_id") != args.batch_id:
        errors.append(f"qualified row batch mismatch: {row.get('control_id')}/{row.get('target_id')}")
        continue
    if args.accept_qualified:
        if row.get("evidence_state") != "SUFFICIENT":
            errors.append(f"qualified row is not SUFFICIENT: {row.get('control_id')}/{row.get('target_id')}")
            continue
        decisions.append({
            **row,
            "acceptance_state":"ACCEPTED",
            "acceptance_mode":"BATCH_AUTO_QUALIFIED_HUMAN_APPROVED",
            "decision_owner":args.batch_owner,
            "decision_rationale":"Accepted as part of EMS-controlled batch approval after deterministic qualification.",
            "accepted_at_utc":datetime.now(UTC).isoformat(),
        })

for row in reviewed:
    if row.get("batch_id") != args.batch_id:
        errors.append(f"review row batch mismatch: {row.get('control_id')}/{row.get('target_id')}")
        continue
    decision=(row.get("human_decision") or "").strip().upper()
    if decision not in {"ACCEPT","REJECT","HOLD"}:
        errors.append(f"missing/invalid human decision: {row.get('control_id')}/{row.get('target_id')}")
        continue

    if decision=="ACCEPT" and row.get("evidence_state")!="SUFFICIENT":
        errors.append(
            f"cannot ACCEPT insufficient evidence: {row.get('control_id')}/{row.get('target_id')}"
        )
        continue

    state = {
        "ACCEPT":"ACCEPTED",
        "REJECT":"REJECTED",
        "HOLD":"HELD",
    }[decision]

    decisions.append({
        **row,
        "acceptance_state":state,
        "acceptance_mode":"HUMAN_EXCEPTION_REVIEW",
        "decision_owner":row.get("decision_owner") or args.batch_owner,
        "decision_rationale":row.get("decision_rationale") or "Human exception review.",
        "accepted_at_utc":datetime.now(UTC).isoformat(),
    })

out=Path(args.output)
out.parent.mkdir(parents=True,exist_ok=True)
with out.open("w",encoding="utf-8") as f:
    for row in decisions:
        f.write(json.dumps(row)+"\n")

summary={
    "status":"PASS" if not errors else "FAIL",
    "batch_id":args.batch_id,
    "decision_count":len(decisions),
    "accepted_count":sum(r["acceptance_state"]=="ACCEPTED" for r in decisions),
    "rejected_count":sum(r["acceptance_state"]=="REJECTED" for r in decisions),
    "held_count":sum(r["acceptance_state"]=="HELD" for r in decisions),
    "errors":errors,
}
print(json.dumps(summary,indent=2))
raise SystemExit(0 if not errors else 1)

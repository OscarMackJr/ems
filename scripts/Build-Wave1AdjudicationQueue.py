import argparse
import csv
import json
from pathlib import Path

def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--compliance", required=True)
    ap.add_argument("--observations", required=True)
    ap.add_argument("--rules", required=True)
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args()

    rules = load_json(args.rules)
    observations = load_json(args.observations)
    obs_by = {(o["repository_id"], o["control_id"]): o for o in observations}

    with Path(args.compliance).open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))

    scope = set(rules["status_scope"])
    default_disp = rules["default_dispositions"]
    control_rules = rules.get("control_rules", {})

    queue = []

    for row in rows:
        status = row.get("compliance_status", "")
        if status not in scope:
            continue

        key = (row["repository_id"], row["control_id"])
        obs = obs_by.get(key, {})
        c_rule = control_rules.get(row["control_id"], {})

        if status == "NOT_APPLICABLE":
            disposition = c_rule.get("not_applicable_disposition", default_disp.get("NOT_APPLICABLE", "CONFIRM_NA"))
        elif status == "WARNING":
            disposition = c_rule.get("warning_disposition", c_rule.get("default_disposition", default_disp.get("WARNING", "COLLECTOR_REVIEW")))
            if disposition == "CONFIRM_NA":
                disposition = "COLLECTOR_REVIEW"
        elif status == "FAIL":
            disposition = c_rule.get("fail_disposition", c_rule.get("default_disposition", default_disp.get("FAIL", "REMEDIATE")))
            if disposition == "CONFIRM_NA":
                disposition = "REMEDIATE"
        else:
            disposition = default_disp.get(status, "COLLECTOR_REVIEW")
        rationale = c_rule.get("reason", f"Default adjudication for status {status}.")

        assertions = obs.get("assertions", {})
        note = obs.get("note", "")

        prior = row.get("wave1_previous_status", "")
        regression = bool(prior and prior != status and prior in {"PASS","WARNING"} and status in {"WARNING","FAIL"})

        queue.append({
            "repository_id": row["repository_id"],
            "repository_name": row["repository_name"],
            "tier": row.get("tier",""),
            "control_id": row["control_id"],
            "control_name": row["control_name"],
            "family": row.get("family",""),
            "wave1_status": status,
            "previous_status": prior,
            "regression_flag": regression,
            "proposed_disposition": disposition,
            "adjudication_rationale": rationale,
            "collector_source": obs.get("source",""),
            "collector_note": note,
            "assertions_json": json.dumps(assertions, separators=(",",":")),
            "reviewer_disposition": "",
            "reviewer_decision": "",
            "reviewer_notes": "",
            "owner": "",
            "target_date": "",
            "evidence_reference": ""
        })

    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)

    fields = list(queue[0].keys()) if queue else []
    if queue:
        with (out/"wave1_adjudication_queue.csv").open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=fields)
            w.writeheader()
            w.writerows(queue)

    (out/"wave1_adjudication_queue.json").write_text(json.dumps(queue, indent=2), encoding="utf-8")

    summary = {
        "queue_count": len(queue),
        "by_status": {},
        "by_proposed_disposition": {},
        "regression_count": sum(1 for q in queue if q["regression_flag"]),
        "regressions": [
            {
                "repository": q["repository_name"],
                "control_id": q["control_id"],
                "control_name": q["control_name"],
                "previous_status": q["previous_status"],
                "wave1_status": q["wave1_status"]
            }
            for q in queue if q["regression_flag"]
        ]
    }

    for q in queue:
        summary["by_status"][q["wave1_status"]] = summary["by_status"].get(q["wave1_status"], 0) + 1
        d = q["proposed_disposition"]
        summary["by_proposed_disposition"][d] = summary["by_proposed_disposition"].get(d, 0) + 1

    (out/"wave1_adjudication_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()



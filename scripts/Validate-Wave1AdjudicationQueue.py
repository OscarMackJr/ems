import argparse
import csv
import json
import sys
from pathlib import Path

ALLOWED = {"REMEDIATE","COLLECTOR_REVIEW","POLICY_REVIEW","CONFIRM_NA","ACCEPT","EXCEPTION_REQUEST","DEFER"}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--queue", required=True)
    ap.add_argument("--report", required=True)
    args = ap.parse_args()

    errors = []
    with Path(args.queue).open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))

    for i, r in enumerate(rows, start=2):
        if r["proposed_disposition"] not in ALLOWED:
            errors.append(f"Line {i}: invalid proposed_disposition {r['proposed_disposition']}")
        if r["wave1_status"] not in {"FAIL","WARNING","NOT_APPLICABLE"}:
            errors.append(f"Line {i}: unexpected adjudication status {r['wave1_status']}")
        if not r["repository_id"] or not r["control_id"]:
            errors.append(f"Line {i}: missing repository/control identifier")

    result = {
        "status": "PASS" if not errors else "FAIL",
        "row_count": len(rows),
        "errors": errors
    }
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    sys.exit(0 if not errors else 1)

if __name__ == "__main__":
    main()

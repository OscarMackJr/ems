import argparse
import csv
import json
from pathlib import Path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--queue", required=True)
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args()

    with Path(args.queue).open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))

    resolved = []
    unresolved = []

    for r in rows:
        chosen = (r.get("reviewer_disposition") or "").strip()
        decision = (r.get("reviewer_decision") or "").strip()

        if chosen and decision:
            resolved.append(r)
        else:
            unresolved.append(r)

    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)

    def write_csv(name, data):
        if not data:
            return
        with (out/name).open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(data[0].keys()))
            w.writeheader()
            w.writerows(data)

    write_csv("wave1_adjudication_resolved.csv", resolved)
    write_csv("wave1_adjudication_unresolved.csv", unresolved)

    action_buckets = {}
    for r in resolved:
        d = r["reviewer_disposition"]
        action_buckets[d] = action_buckets.get(d, 0) + 1

    summary = {
        "total_rows": len(rows),
        "resolved_count": len(resolved),
        "unresolved_count": len(unresolved),
        "resolved_by_disposition": action_buckets
    }
    (out/"wave1_adjudication_final_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()

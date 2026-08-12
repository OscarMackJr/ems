import argparse,csv,json
from pathlib import Path
from collections import defaultdict

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--queue",required=True)
    ap.add_argument("--outdir",required=True)
    a=ap.parse_args()

    with Path(a.queue).open(encoding="utf-8-sig",newline="") as fh:
        rows=list(csv.DictReader(fh))

    pending=[
        r for r in rows
        if r.get("proposed_disposition")=="POLICY_REVIEW"
        and not (r.get("reviewer_disposition") or "").strip()
    ]

    grouped=defaultdict(list)
    for r in pending:
        grouped[(r["control_id"],r["control_name"])].append(r)

    out_rows=[]
    detail={}
    for (cid,cname),items in sorted(grouped.items()):
        repos=sorted({r["repository_name"] for r in items})
        statuses=sorted({r["wave1_status"] for r in items})
        rationales=sorted({r.get("adjudication_rationale","") for r in items if r.get("adjudication_rationale")})
        out_rows.append({
            "control_id":cid,
            "control_name":cname,
            "row_count":len(items),
            "repositories":";".join(repos),
            "wave1_statuses":";".join(statuses),
            "current_rationale":" | ".join(rationales),
            "policy_decision":"",
            "policy_effective_date":"",
            "policy_owner":"",
            "policy_notes":"",
            "approved_status_mapping":""
        })
        detail[cid]=items

    out=Path(a.outdir);out.mkdir(parents=True,exist_ok=True)
    if out_rows:
        with (out/"policy_review_queue.csv").open("w",newline="",encoding="utf-8") as fh:
            w=csv.DictWriter(fh,fieldnames=list(out_rows[0].keys()))
            w.writeheader();w.writerows(out_rows)

    (out/"policy_review_detail.json").write_text(json.dumps(detail,indent=2),encoding="utf-8")
    print(json.dumps({
        "policy_control_count":len(out_rows),
        "policy_row_count":len(pending),
        "controls":[{"control_id":r["control_id"],"count":r["row_count"]} for r in out_rows]
    },indent=2))

if __name__=="__main__":main()

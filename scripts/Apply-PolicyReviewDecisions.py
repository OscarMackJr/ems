import argparse,csv,json
from pathlib import Path

ALLOWED_STATUS={"PASS","WARNING","FAIL","NOT_APPLICABLE","NOT_EVALUATED","EXCEPTION","POLICY_PENDING"}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--policy-queue",required=True)
    ap.add_argument("--adjudication-queue",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()

    with Path(a.policy_queue).open(encoding="utf-8-sig",newline="") as fh:
        policies=list(csv.DictReader(fh))

    decisions={}
    errors=[]
    for p in policies:
        decision=(p.get("policy_decision") or "").strip()
        mapping=(p.get("approved_status_mapping") or "").strip()
        if not decision:
            continue
        if not mapping:
            errors.append(f"{p['control_id']}: policy_decision set but approved_status_mapping missing")
            continue
        if mapping not in ALLOWED_STATUS:
            errors.append(f"{p['control_id']}: invalid approved_status_mapping {mapping}")
            continue
        decisions[p["control_id"]]=p

    if errors:
        raise SystemExit("\n".join(errors))

    with Path(a.adjudication_queue).open(encoding="utf-8-sig",newline="") as fh:
        rows=list(csv.DictReader(fh))

    applied=0
    for r in rows:
        if r.get("proposed_disposition")!="POLICY_REVIEW":
            continue
        if (r.get("reviewer_disposition") or "").strip():
            continue
        p=decisions.get(r["control_id"])
        if not p:
            continue

        r["reviewer_disposition"]="ACCEPT"
        r["reviewer_decision"]="POLICY_APPROVED"
        r["reviewer_notes"]=(
            f"Policy decision: {p['policy_decision']}. "
            f"Approved status mapping: {p['approved_status_mapping']}. "
            f"{p.get('policy_notes','')}"
        ).strip()
        r["owner"]=p.get("policy_owner","")
        r["evidence_reference"]=f"policy_review_queue:{r['control_id']}"
        applied+=1

    out=Path(a.out)
    with out.open("w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh,fieldnames=list(rows[0].keys()))
        w.writeheader();w.writerows(rows)

    print(json.dumps({"policy_controls_with_decisions":len(decisions),"adjudication_rows_closed":applied},indent=2))

if __name__=="__main__":main()

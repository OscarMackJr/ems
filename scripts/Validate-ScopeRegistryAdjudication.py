import argparse,csv,json,sys
from pathlib import Path

DECISIONS={"APPROVED","RECLASSIFY","DEFER"}
SCOPES={"REPOSITORY","SERVICE","APPLICATION","PLATFORM","ORGANIZATION","EMS"}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--queue",required=True)
    ap.add_argument("--report",required=True)
    ap.add_argument("--require-complete",action="store_true")
    a=ap.parse_args()

    with Path(a.queue).open(encoding="utf-8-sig",newline="") as fh:
        rows=list(csv.DictReader(fh))

    errors=[];warnings=[];counts={}

    for i,r in enumerate(rows,start=2):
        d=(r.get("reviewer_decision") or "").strip()
        p=(r.get("proposed_scope") or "").strip()
        rat=(r.get("reviewer_rationale") or "").strip()

        if not d:
            if a.require_complete:
                errors.append(f"Line {i} {r['control_id']}: reviewer_decision required")
            else:
                warnings.append(f"{r['control_id']}: not yet adjudicated")
            continue

        if d not in DECISIONS:
            errors.append(f"Line {i} {r['control_id']}: invalid reviewer_decision {d}")
            continue

        counts[d]=counts.get(d,0)+1

        if d=="APPROVED":
            if p and p!=r["current_scope"]:
                errors.append(f"Line {i} {r['control_id']}: APPROVED cannot change scope")
        elif d=="RECLASSIFY":
            if p not in SCOPES:
                errors.append(f"Line {i} {r['control_id']}: RECLASSIFY requires valid proposed_scope")
            if p==r["current_scope"]:
                errors.append(f"Line {i} {r['control_id']}: RECLASSIFY proposed_scope equals current_scope")

        if d in {"APPROVED","RECLASSIFY"} and not rat:
            errors.append(f"Line {i} {r['control_id']}: reviewer_rationale required")

    result={
        "status":"PASS" if not errors else "FAIL",
        "row_count":len(rows),
        "decision_counts":counts,
        "errors":errors,
        "warnings":warnings
    }
    Path(a.report).parent.mkdir(parents=True,exist_ok=True)
    Path(a.report).write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result,indent=2))
    sys.exit(1 if errors else 0)

if __name__=="__main__":main()

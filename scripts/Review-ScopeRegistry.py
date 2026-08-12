import argparse,csv,json
from pathlib import Path
from datetime import date

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--queue",required=True)
    ap.add_argument("--model",required=True)
    ap.add_argument("--out",required=True)
    ap.add_argument("--exceptions",required=True)
    a=ap.parse_args()

    model=json.loads(Path(a.model).read_text(encoding="utf-8"))
    with Path(a.queue).open(encoding="utf-8-sig",newline="") as fh:
        rows=list(csv.DictReader(fh))

    targets=model["targets"]
    deferred=set(model["defer"])
    templates=model["rationale_templates"]
    reviewed=[]
    exceptions=[]

    for r in rows:
        cid=r["control_id"]
        current=r["current_scope"]

        if cid in targets:
            target=targets[cid]
            if target==current:
                r["reviewer_decision"]="APPROVED"
                r["proposed_scope"]=current
            else:
                r["reviewer_decision"]="RECLASSIFY"
                r["proposed_scope"]=target

            impact=int(r.get("not_evaluated_row_count") or 0)
            r["reviewer_rationale"]=(
                f"{templates[target]} "
                f"Wave 2A impact shows {impact} NOT_EVALUATED repository row(s) for this control. "
                f"Classification reviewed against the control's primary operating boundary."
            )
            r["reviewer"]=model["reviewer"]
            r["review_date"]=date.today().isoformat()

        elif cid in deferred:
            r["reviewer_decision"]="DEFER"
            r["proposed_scope"]=""
            r["reviewer_rationale"]=(
                "Scope cannot be approved from the current registry metadata alone. "
                "Review the authoritative control definition and evidence source before enabling inheritance."
            )
            r["reviewer"]=model["reviewer"]
            r["review_date"]=date.today().isoformat()
            exceptions.append({
                "control_id":cid,
                "control_name":r["control_name"],
                "current_scope":current,
                "not_evaluated_row_count":r.get("not_evaluated_row_count",""),
                "reason":"Authoritative control semantics required before scope approval."
            })
        else:
            r["reviewer_decision"]="DEFER"
            r["reviewer_rationale"]="No automated review rule exists for this control."
            r["reviewer"]=model["reviewer"]
            r["review_date"]=date.today().isoformat()
            exceptions.append({
                "control_id":cid,
                "control_name":r["control_name"],
                "current_scope":current,
                "not_evaluated_row_count":r.get("not_evaluated_row_count",""),
                "reason":"No automated scope-review rule."
            })

        reviewed.append(r)

    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh,fieldnames=list(reviewed[0].keys()))
        w.writeheader();w.writerows(reviewed)

    ex=Path(a.exceptions);ex.parent.mkdir(parents=True,exist_ok=True)
    if exceptions:
        with ex.open("w",newline="",encoding="utf-8") as fh:
            w=csv.DictWriter(fh,fieldnames=list(exceptions[0].keys()))
            w.writeheader();w.writerows(exceptions)
    else:
        ex.write_text("control_id,control_name,current_scope,not_evaluated_row_count,reason\n",encoding="utf-8")

    counts={}
    for r in reviewed:
        d=r["reviewer_decision"]
        counts[d]=counts.get(d,0)+1

    print(json.dumps({
        "row_count":len(reviewed),
        "decision_counts":counts,
        "exception_count":len(exceptions)
    },indent=2))

if __name__=="__main__":main()

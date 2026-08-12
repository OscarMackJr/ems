import argparse,csv,json
from pathlib import Path
import yaml

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--registry",required=True)
    ap.add_argument("--compliance",required=True)
    ap.add_argument("--outdir",required=True)
    a=ap.parse_args()

    reg=yaml.safe_load(Path(a.registry).read_text(encoding="utf-8"))
    cmap={c["control_id"]:c for c in reg["controls"]}

    with Path(a.compliance).open(encoding="utf-8-sig",newline="") as fh:
        rows=list(csv.DictReader(fh))

    outdir=Path(a.outdir);outdir.mkdir(parents=True,exist_ok=True)

    matrix=[]
    current_ne=0
    by_scope={}
    repo_true_ne=0
    inherited_candidate_rows=0

    for r in rows:
        c=cmap.get(r["control_id"])
        if not c:
            continue
        status=r["compliance_status"]
        scope=c["scope"]
        is_ne=status=="NOT_EVALUATED"
        if is_ne:
            current_ne+=1
            by_scope[scope]=by_scope.get(scope,0)+1
            if scope=="REPOSITORY":
                repo_true_ne+=1
            elif c["inheritance_allowed"]:
                inherited_candidate_rows+=1

        matrix.append({
            "repository_name":r["repository_name"],
            "control_id":r["control_id"],
            "control_name":r["control_name"],
            "current_status":status,
            "scope":scope,
            "scope_owner":c["scope_owner"],
            "inheritance_allowed":c["inheritance_allowed"],
            "evidence_authority":c["evidence_authority"],
            "classification_status":c["classification_status"],
            "wave2a_effective_interpretation":
                ("REPOSITORY_EVALUATION_REQUIRED" if scope=="REPOSITORY" else
                 "HIGHER_SCOPE_EVIDENCE_REQUIRED" if is_ne else
                 "EXISTING_RESULT_RETAINED")
        })

    fields=list(matrix[0].keys())
    with (outdir/"control_scope_matrix.csv").open("w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh,fieldnames=fields);w.writeheader();w.writerows(matrix)

    impacts=[]
    for scope,count in sorted(by_scope.items()):
        impacts.append({
            "scope":scope,
            "not_evaluated_rows":count,
            "repository_evaluation_required": scope=="REPOSITORY",
            "inheritance_candidate": scope!="REPOSITORY"
        })
    with (outdir/"scope_impact_analysis.csv").open("w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh,fieldnames=list(impacts[0].keys()) if impacts else
                         ["scope","not_evaluated_rows","repository_evaluation_required","inheritance_candidate"])
        w.writeheader();w.writerows(impacts)

    summary={
        "current_not_evaluated":current_ne,
        "not_evaluated_by_scope":by_scope,
        "true_repository_not_evaluated":repo_true_ne,
        "higher_scope_inheritance_candidates":inherited_candidate_rows,
        "potential_repository_not_evaluated_reduction_if_higher_scope_evidence_exists":
            inherited_candidate_rows,
        "note":"Wave 2A does not change compliance statuses. It identifies rows that should be resolved by higher-scope evidence rather than repository-local collectors."
    }
    (outdir/"scope_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print(json.dumps(summary,indent=2))

if __name__=="__main__":main()

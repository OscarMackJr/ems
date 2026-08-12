import argparse,csv,json,re
from pathlib import Path
from datetime import date

CONTROLS={
"EMS-CTRL-049":{
    "name":"Approved AI Platforms",
    "scope":"ORGANIZATION",
    "assertion":"unapproved_platform_handling_detected",
    "positive_groups":[
        ["unapproved","ai","platform"],
        ["blocked","ai"],
        ["rejected","ai"],
        ["denied","ai"],
        ["ai","exception"],
        ["ai","escalat"]
    ]
},
"EMS-CTRL-050":{
    "name":"Prompt Data Classification",
    "scope":"ORGANIZATION",
    "assertion":"sensitive_data_handling_detected",
    "positive_groups":[
        ["prompt","sensitive"],
        ["prompt","confidential"],
        ["prompt","restricted"],
        ["prompt","classification"],
        ["prompt","redact"]
    ]
},
"EMS-CTRL-053":{
    "name":"AI Security Review",
    "scope":"ORGANIZATION",
    "assertion":"risk_or_finding_tracking_detected",
    "positive_groups":[
        ["ai","security","finding"],
        ["ai","security","risk"],
        ["ai","security","remediation"],
        ["ai","security","exception"],
        ["ai","security","assessment"]
    ]
}
}

TEXT_EXTS={".md",".txt",".csv",".json",".yaml",".yml"}

def txt(p):
    try:return p.read_text(encoding="utf-8",errors="ignore").lower()
    except:return ""

def allowed_files(root):
    roots=[]
    for rel in ["evidence","reviews","assessments","registers","generated/wave2/higher-scope-remediation"]:
        p=root/rel
        if p.exists(): roots.append(p)
    out=[]
    for base in roots:
        for p in base.rglob("*"):
            if p.is_file() and p.suffix.lower() in TEXT_EXTS:
                low=str(p).lower()
                if ".bak" in low: continue
                out.append(p)
    return out

def is_prior_or_definition(path):
    name=path.name.lower()
    low=str(path).lower().replace("/","\\")
    if any(x in name for x in [
        "effective_compliance","repository_control_compliance","qualification_summary",
        "collector_report","control_catalog","control_registry","schema","policy","standard"
    ]):
        return True
    if "\\generated\\wave2\\higher-scope-collectors\\" in low:
        return True
    return False

def matches(text,groups):
    matched=[]
    for g in groups:
        if all(tok in text for tok in g):
            matched.append(g)
    return matched

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--ems-root",required=True)
    ap.add_argument("--outdir",required=True)
    a=ap.parse_args()

    root=Path(a.ems_root)
    out=Path(a.outdir);out.mkdir(parents=True,exist_ok=True)
    files=allowed_files(root)

    candidates=[]
    results=[]

    for cid,cfg in CONTROLS.items():
        operating=[]
        rejected=[]
        for p in files:
            text=txt(p)
            groups=matches(text,cfg["positive_groups"])
            if not groups: continue
            row={
                "control_id":cid,
                "control_name":cfg["name"],
                "scope":cfg["scope"],
                "assertion":cfg["assertion"],
                "source_path":str(p),
                "matched_signal_groups":";".join("+".join(g) for g in groups)
            }
            if is_prior_or_definition(p):
                row["source_class"]="REJECTED_NONOPERATING"
                rejected.append(row)
            else:
                row["source_class"]="OPERATING_EVIDENCE"
                operating.append(row)
            candidates.append(row)

        sufficient=len(operating)>=1
        results.append({
            "control_id":cid,
            "control_name":cfg["name"],
            "scope":cfg["scope"],
            "assertion":cfg["assertion"],
            "operating_evidence_count":len(operating),
            "rejected_source_count":len(rejected),
            "status":"PASS" if sufficient else "WARNING",
            "sufficiency":"SUFFICIENT" if sufficient else "INSUFFICIENT",
            "promotion_eligible":sufficient,
            "operating_sources":";".join(x["source_path"] for x in operating)
        })

    with (out/"targeted_evidence_candidates.csv").open("w",newline="",encoding="utf-8") as fh:
        fields=["control_id","control_name","scope","assertion","source_path","matched_signal_groups","source_class"]
        w=csv.DictWriter(fh,fieldnames=fields);w.writeheader();w.writerows(candidates)

    with (out/"gap_resolution.csv").open("w",newline="",encoding="utf-8") as fh:
        fields=list(results[0].keys())
        w=csv.DictWriter(fh,fieldnames=fields);w.writeheader();w.writerows(results)

    summary={
        "control_count":3,
        "resolved_gap_count":sum(str(x["promotion_eligible"]).lower()=="true" for x in results),
        "remaining_gap_count":sum(str(x["promotion_eligible"]).lower()!="true" for x in results)
    }
    (out/"gap_resolution_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print(json.dumps(summary,indent=2))

if __name__=="__main__":main()

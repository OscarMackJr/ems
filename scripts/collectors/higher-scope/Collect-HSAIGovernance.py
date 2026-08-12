#!/usr/bin/env python3
import argparse, csv, json, re
from pathlib import Path
from datetime import datetime, timezone

CONTROLS = {
    "EMS-CTRL-007": ("AI-assisted development governance", "ORGANIZATION", [
        ("approved_ai_governance_evidence_detected", ["ai", "approved", "governance"]),
        ("human_accountability_detected", ["human", "accountab"]),
        ("confidential_data_protection_detected", ["confidential", "data"]),
        ("approved_service_or_platform_detected", ["approved", "service"]),
    ]),
    "EMS-CTRL-049": ("Approved AI Platforms", "ORGANIZATION", [
        ("approved_ai_platform_inventory_detected", ["approved", "ai", "platform"]),
        ("platform_approval_or_owner_detected", ["owner", "approv"]),
        ("unapproved_platform_handling_detected", ["unapproved", "prohibit"]),
        ("platform_evidence_retained", ["ai", "platform"]),
    ]),
    "EMS-CTRL-050": ("Prompt Data Classification", "ORGANIZATION", [
        ("prompt_data_classification_rule_detected", ["prompt", "classification"]),
        ("sensitive_data_handling_detected", ["sensitive", "data"]),
        ("classification_enforcement_or_guidance_detected", ["classification", "ai"]),
        ("prompt_classification_evidence_retained", ["prompt", "data"]),
    ]),
    "EMS-CTRL-052": ("AI Attribution", "ORGANIZATION", [
        ("ai_use_attribution_requirement_detected", ["ai", "attribution"]),
        ("human_reviewer_or_accountability_detected", ["human", "review"]),
        ("ai_assisted_change_traceability_detected", ["ai", "assist"]),
        ("attribution_evidence_retained", ["attribution", "ai"]),
    ]),
    "EMS-CTRL-053": ("AI Security Review", "ORGANIZATION", [
        ("ai_security_review_requirement_detected", ["ai", "security", "review"]),
        ("security_owner_or_approver_detected", ["security", "approv"]),
        ("risk_or_finding_tracking_detected", ["risk", "finding"]),
        ("security_review_evidence_retained", ["security", "review"]),
    ]),
    "EMS-CTRL-054": ("AI Model Risk Review", "ORGANIZATION", [
        ("model_risk_review_requirement_detected", ["model", "risk", "review"]),
        ("model_risk_criteria_detected", ["model", "risk"]),
        ("review_owner_or_approval_detected", ["risk", "approv"]),
        ("model_risk_evidence_retained", ["model", "risk"]),
    ]),
}

TEXT_EXTS = {".md",".txt",".yaml",".yml",".json",".csv",".ps1",".py",".toml",".ini",".cfg",".xml"}

def utcnow():
    return datetime.now(timezone.utc).isoformat()

def status(assertions):
    vals = [a["result"] for a in assertions.values()]
    if vals and all(v == "PASS" for v in vals):
        return "PASS"
    if any(v == "FAIL" for v in vals):
        return "WARNING"
    if any(v in ("UNKNOWN","WARNING") for v in vals):
        return "WARNING"
    return "NOT_EVALUATED"

def scan_files(root):
    excluded = {".git",".venv","venv","node_modules","__pycache__"}
    rows = []
    for p in root.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in TEXT_EXTS:
            continue
        if any(part in excluded for part in p.parts):
            continue
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        rows.append((p, txt.lower()))
    return rows

def match(files, terms):
    hits=[]
    for p,txt in files:
        if all(t.lower() in txt for t in terms):
            hits.append(str(p))
    return hits

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--outdir", required=True)
    args=ap.parse_args()
    repo=Path(args.root).resolve()
    out=Path(args.outdir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    files=scan_files(repo)

    envs=[]
    assertion_rows=[]
    for cid,(name,scope,checks) in CONTROLS.items():
        A={}
        for assertion,terms in checks:
            hits=match(files, terms)
            result="PASS" if hits else "UNKNOWN"
            detail=(f"{len(hits)} retained artifact(s) matched required semantic signals."
                    if hits else "No retained artifact matched all required semantic signals.")
            A[assertion]={"result":result,"detail":detail,"evidence_paths":hits[:20]}
            assertion_rows.append({
                "control_id":cid,"control_name":name,"scope":scope,
                "assertion":assertion,"result":result,"detail":detail
            })
        st=status(A)
        envs.append({
            "collector_id":"HS-AI-GOVERNANCE",
            "collector_version":"2B2.5",
            "control_id":cid,"control_name":name,"scope":scope,
            "collector_status":st,
            "evidence_class":"OPERATING_EVIDENCE",
            "assertions":A,
            "collected_at":utcnow(),
            "source_root":str(repo),
            "promotion_candidate": st=="PASS",
            "notes":"Semantic discovery is evidence discovery only; promotion remains qualification-gated."
        })

    with (out/"evidence_envelopes.jsonl").open("w",encoding="utf-8") as f:
        for e in envs: f.write(json.dumps(e,sort_keys=True)+"\n")
    with (out/"assertions.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=["control_id","control_name","scope","assertion","result","detail"])
        w.writeheader(); w.writerows(assertion_rows)

    counts={}
    for e in envs: counts[e["collector_status"]]=counts.get(e["collector_status"],0)+1
    report={
        "collector_id":"HS-AI-GOVERNANCE","collector_version":"2B2.5",
        "control_count":len(envs),"status_counts":counts,
        "promotion_candidate_count":sum(1 for e in envs if e["promotion_candidate"])
    }
    (out/"collector_report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps(report,indent=2))

if __name__=="__main__":
    main()

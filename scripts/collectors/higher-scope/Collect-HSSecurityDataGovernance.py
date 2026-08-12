import argparse,csv,json
from pathlib import Path
from datetime import datetime,timezone

CONTROLS={
"EMS-CTRL-023":{
"name":"Vulnerability Remediation Targets","scope":"ORGANIZATION",
"assertions":{
"vulnerability_findings_detected":[["vulnerability"],["finding","security"]],
"severity_or_priority_recorded":[["severity"],["priority"]],
"remediation_target_or_due_date_recorded":[["target","date"],["due","date"],["sla"]],
"owner_or_accountability_recorded":[["owner"],["assigned"]],
"remediation_status_or_closure_history_retained":[["status"],["closed"],["remediation"]]
}},
"EMS-CTRL-024":{
"name":"Security Exception Approval","scope":"ORGANIZATION",
"assertions":{
"security_exception_record_detected":[["security","exception"],["waiver","security"]],
"exception_scope_and_reason_recorded":[["scope","reason"],["exception","reason"]],
"approver_or_authority_recorded":[["approver"],["approved","by"],["authority"]],
"expiry_or_review_date_recorded":[["expiry"],["expiration"],["review","date"]],
"exception_status_or_closure_history_retained":[["status"],["closed"],["approved"]]
}},
"EMS-CTRL-063":{
"name":"Data Classification","scope":"ORGANIZATION",
"assertions":{
"data_classification_record_detected":[["data","classification"]],
"classification_level_recorded":[["confidential"],["restricted"],["internal"],["public"]],
"data_owner_or_steward_recorded":[["data","owner"],["steward"]],
"system_or_dataset_scope_recorded":[["dataset"],["system"],["repository"]],
"classification_review_or_update_history_retained":[["review"],["updated"],["history"]]
}},
"EMS-CTRL-065":{
"name":"Data Retention Compliance","scope":"ORGANIZATION",
"assertions":{
"retention_schedule_or_record_detected":[["retention"],["retention","schedule"]],
"retention_period_recorded":[["days"],["months"],["years"],["retention","period"]],
"data_scope_or_category_recorded":[["data","category"],["dataset"],["record","type"]],
"owner_or_authority_recorded":[["owner"],["authority"]],
"retention_execution_or_disposition_evidence_retained":[["deleted"],["disposed"],["purged"],["retained"]]
}},
"EMS-CTRL-066":{
"name":"Production Data Protection","scope":"ORGANIZATION",
"assertions":{
"production_data_protection_record_detected":[["production","data"],["prod","data"]],
"sensitive_or_production_data_scope_recorded":[["sensitive"],["confidential"],["production"]],
"protection_control_or_handling_recorded":[["encrypt"],["mask"],["redact"],["access","control"]],
"owner_or_responsible_party_recorded":[["owner"],["responsible"]],
"protection_validation_or_review_evidence_retained":[["validation"],["review"],["test"],["audit"]]
}}
}

TEXT_EXTS={".md",".txt",".csv",".json",".yaml",".yml"}

def read(p):
    try:return p.read_text(encoding="utf-8",errors="ignore").lower()
    except:return ""

def files(root):
    out=[]
    for p in root.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in TEXT_EXTS: continue
        low=str(p).lower().replace("/","\\")
        if any(x in low for x in ["\\.git\\","\\.venv\\","\\node_modules\\","\\site-packages\\"]): continue
        out.append(p)
    return out

def match(text,groups):
    return any(all(tok in text for tok in g) for g in groups)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--ems-root",required=True)
    ap.add_argument("--outdir",required=True)
    a=ap.parse_args()
    root=Path(a.ems_root);out=Path(a.outdir);out.mkdir(parents=True,exist_ok=True)
    fs=files(root)
    envs=[]; rows=[]

    for cid,cfg in CONTROLS.items():
        assertions={}
        for name,groups in cfg["assertions"].items():
            hits=[]
            for p in fs:
                t=read(p)
                if match(t,groups): hits.append(str(p))
            assertions[name]={
                "result":"PASS" if hits else "UNKNOWN",
                "detail":f"{len(hits)} candidate artifact(s) matched semantic signals." if hits else "No candidate artifact matched semantic signals.",
                "evidence_paths":hits[:30]
            }
            rows.append({
                "control_id":cid,"control_name":cfg["name"],"scope":cfg["scope"],
                "assertion":name,"result":assertions[name]["result"],"candidate_count":len(hits)
            })
        st="PASS" if all(v["result"]=="PASS" for v in assertions.values()) else "WARNING"
        envs.append({
            "collector_id":"HS-SECURITY-DATA-GOVERNANCE",
            "collector_version":"2B2.6",
            "control_id":cid,"control_name":cfg["name"],"scope":cfg["scope"],
            "status":st,"assertions":assertions,
            "collected_at":datetime.now(timezone.utc).isoformat(),
            "promotion_candidate":False,
            "notes":"Discovery only. Promotion requires second-stage operating-evidence qualification."
        })

    (out/"evidence_envelopes.jsonl").write_text("".join(json.dumps(x)+"\n" for x in envs),encoding="utf-8")
    with (out/"assertions.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=["control_id","control_name","scope","assertion","result","candidate_count"]);w.writeheader();w.writerows(rows)

    counts={}
    for e in envs:counts[e["status"]]=counts.get(e["status"],0)+1
    report={"collector_id":"HS-SECURITY-DATA-GOVERNANCE","collector_version":"2B2.6","control_count":5,"status_counts":counts}
    (out/"collector_report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps(report,indent=2))

if __name__=="__main__":main()

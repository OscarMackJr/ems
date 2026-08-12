import argparse,csv,json,re
from pathlib import Path
from datetime import date, datetime

CONTROLS={
"EMS-CTRL-075":"Continuous Compliance Scan",
"EMS-CTRL-076":"Corrective Action Tracking",
}

def assertion(result,detail): return {"result":result,"detail":detail}
def txt(p):
    try:return p.read_text(encoding="utf-8",errors="replace")
    except:return ""
def status(A):
    vals=[v["result"] for v in A.values()]
    if vals and all(x=="PASS" for x in vals):return "PASS"
    if any(x=="FAIL" for x in vals):return "WARNING"
    if any(x=="PASS" for x in vals):return "WARNING"
    return "NOT_EVALUATED"

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--ems-root",required=True)
    ap.add_argument("--outdir",required=True)
    a=ap.parse_args()

    root=Path(a.ems_root);out=Path(a.outdir);out.mkdir(parents=True,exist_ok=True)
    fs=[]
    for p in root.rglob("*"):
        if p.is_file():
            low=str(p).lower()
            if any(x in low for x in ["\\.git\\","\\.venv\\","\\site-packages\\","\\__pycache__\\"]):continue
            fs.append(p)

    # CTRL-075 evidence: actual execution outputs, not just code.
    compliance_outputs=[p for p in fs if any(x in p.name.lower() for x in [
        "repository_control_compliance","effective_compliance","compliance_postpolicy",
        "inheritance_impact_report","compliance_report","continuous_compliance"
    ]) and p.suffix.lower() in {".csv",".json"}]

    def is_execution_artifact(p):
        low=str(p).lower().replace("/","\\")
        name=p.name.lower()

        if any(x in low for x in [
            "\\schemas\\",
            "\\registry\\",
            "\\scripts\\",
            "\\docs\\",
            ".bak"
        ]):
            return False

        if name.endswith(".schema.json"):
            return False

        if "\\generated\\" not in low and "\\releases\\" not in low and "\\release\\" not in low:
            return False

        if p.suffix.lower() not in {".csv",".json"}:
            return False

        t=txt(p).lower()

        return any(x in name for x in [
            "repository_control_compliance",
            "effective_compliance",
            "compliance_postpolicy",
            "inheritance_impact_report",
            "validation",
            "observation",
            "compliance_report"
        ]) or any(x in t for x in [
            '"row_count"',
            '"observation_count"',
            '"errors": []',
            'repository_name,control_id',
            'repository_name,'
        ])

    execution_reports=[p for p in fs if is_execution_artifact(p)]

    repo_names=set()
    evaluated_control_ids=set()
    applicable_control_ids=set()
    result_row_count=0

    for p in compliance_outputs:
        if p.suffix.lower()==".csv":
            try:
                with p.open(encoding="utf-8-sig",newline="") as fh:
                    rows=list(csv.DictReader(fh))
            except Exception:
                rows=[]

            result_row_count += len(rows)

            for r in rows:
                repo=(r.get("repository_name") or r.get("repository") or "").strip()
                cid=(r.get("control_id") or "").strip()
                row_status=(r.get("compliance_status") or r.get("effective_status") or r.get("status") or "").strip()

                if repo:
                    repo_names.add(repo)

                if re.fullmatch(r"EMS-CTRL-\d{3}",cid):
                    evaluated_control_ids.add(cid)

                    if row_status and row_status != "NOT_APPLICABLE":
                        applicable_control_ids.add(cid)

        elif p.suffix.lower()==".json":
            t=txt(p)
            repo_names |= set(re.findall(r'"repository_name"\s*:\s*"([^"]+)"',t))
            evaluated_control_ids |= set(re.findall(r'EMS-CTRL-\d{3}',t))

    latest_candidates=[p for p in execution_reports if p.exists()]
    latest=max(latest_candidates,key=lambda p:p.stat().st_mtime) if latest_candidates else None

    retained_outputs=[p for p in compliance_outputs if "\\generated\\" in str(p).lower().replace("/","\\") or "\\releases\\" in str(p).lower().replace("/","\\") or "\\release\\" in str(p).lower().replace("/","\\")]

    # CTRL-076 evidence: queues, findings, adjudication, remediation, corrective action.
    tracking_files=[p for p in fs if any(x in p.name.lower() for x in [
        "adjudication_queue","remediation","corrective","exceptions","findings","policy_review_queue",
        "collector_acceptance","wave1_closeout","review_exceptions"
    ]) and p.suffix.lower() in {".csv",".json",".yaml",".yml"}]

    tracking_text="\n".join(txt(p) for p in tracking_files[:200]).lower()
    findings_detected=bool(tracking_files)
    structure_detected=any(x in tracking_text for x in [
        "reviewer_disposition","proposed_disposition","corrective","remediation","resolution",
        "reviewer_decision","status","owner"
    ])
    owner_or_disp=any(x in tracking_text for x in [
        "owner","reviewer_disposition","proposed_disposition","reviewer_decision"
    ])
    open_trace=any(x in tracking_text for x in [
        "warning","fail","policy_pending","defer","open","remediate"
    ])
    closed_history=any(x in tracking_text for x in [
        "approved","resolved","accept","confirm_na","closed","final"
    ])
    retained_tracking=[p for p in tracking_files if "\\generated\\" in str(p).lower().replace("/","\\") or "\\registry\\" in str(p).lower().replace("/","\\") or "\\releases\\" in str(p).lower().replace("/","\\")]

    envs=[]; arows=[]; srows=[]

    for cid,name in CONTROLS.items():
        A={};sources=[]
        if cid=="EMS-CTRL-075":
            A["continuous_compliance_execution_detected"]=assertion(
                "PASS" if compliance_outputs or execution_reports else "UNKNOWN",
                f"{len(compliance_outputs)} compliance output(s); {len(execution_reports)} execution/validation report(s) detected."
            )
            A["managed_repository_population_evaluated"]=assertion(
                "PASS" if len(repo_names)>=6 else ("WARNING" if repo_names else "UNKNOWN"),
                f"{len(repo_names)} structurally parsed managed repository name(s) observed: {sorted(repo_names)}"
            )

            catalog_control_count=80
            evaluated_control_count=len(evaluated_control_ids)
            applicable_control_count=len(applicable_control_ids)

            coverage_ok=(
                evaluated_control_count >= applicable_control_count
                and applicable_control_count > 0
                and result_row_count > 0
            )

            A["control_results_generated"]=assertion(
                "PASS" if coverage_ok else ("WARNING" if evaluated_control_count or result_row_count else "UNKNOWN"),
                (
                    f"catalog_control_count={catalog_control_count}; "
                    f"evaluated_control_count={evaluated_control_count}; "
                    f"applicable_control_count={applicable_control_count}; "
                    f"result_row_count={result_row_count}"
                )
            )

            A["scan_output_retained"]=assertion(
                "PASS" if retained_outputs else "UNKNOWN",
                f"{len(retained_outputs)} retained generated/release compliance output(s) detected."
            )

            A["latest_execution_identifiable"]=assertion(
                "PASS" if latest else "UNKNOWN",
                (
                    f"Latest execution artifact={latest}; "
                    f"mtime={datetime.fromtimestamp(latest.stat().st_mtime).isoformat()}"
                    if latest else
                    "No qualifying generated/release execution artifact available."
                )
            )
            sources=[str(p) for p in (compliance_outputs[:20]+execution_reports[:20])]

        elif cid=="EMS-CTRL-076":
            A["findings_or_exceptions_detected"]=assertion(
                "PASS" if findings_detected else "UNKNOWN",
                f"{len(tracking_files)} finding/exception/remediation tracking artifact(s) detected."
            )
            A["corrective_action_tracking_structure_exists"]=assertion(
                "PASS" if structure_detected else "UNKNOWN",
                "Tracking structure includes status/disposition/remediation semantics." if structure_detected else "No corrective-action tracking structure detected."
            )
            A["owner_or_disposition_recorded"]=assertion(
                "PASS" if owner_or_disp else "UNKNOWN",
                "Owner/disposition/reviewer decision fields detected." if owner_or_disp else "No owner/disposition field detected."
            )
            A["open_items_remain_traceable"]=assertion(
                "PASS" if open_trace else "UNKNOWN",
                "Open/warning/fail/remediation states remain visible in retained tracking artifacts." if open_trace else "No open-item traceability signal detected."
            )
            A["closed_items_preserve_resolution_history"]=assertion(
                "PASS" if closed_history else "UNKNOWN",
                "Approved/resolved/closed history detected." if closed_history else "No resolved-history signal detected."
            )
            A["corrective_action_evidence_retained"]=assertion(
                "PASS" if retained_tracking else "UNKNOWN",
                f"{len(retained_tracking)} retained corrective-action artifact(s) detected."
            )
            sources=[str(p) for p in tracking_files[:40]]

        st=status(A);promo=(st=="PASS" and all(v["result"]=="PASS" for v in A.values()) and bool(sources))
        env={
            "evidence_id":f"EMS-{cid}-HS-CONTINUOUS-COMPLIANCE-{date.today().isoformat()}",
            "control_id":cid,"control_name":name,"scope":"EMS",
            "collector_id":"HS-CONTINUOUS-COMPLIANCE","collector_version":"2B2.3",
            "status":st,"evidence_class":"OPERATING_EVIDENCE","assertions":A,
            "evidence_sources":sorted(set(sources)),"evidence_date":date.today().isoformat(),
            "promotion_candidate":promo,
            "notes":"Open findings do not fail CTRL-076 when ownership/status/history remain controlled and traceable."
        }
        envs.append(env)
        for k,v in A.items(): arows.append({"control_id":cid,"control_name":name,"assertion":k,"result":v["result"],"detail":v["detail"]})
        for s in env["evidence_sources"]: srows.append({"control_id":cid,"source":s})

    (out/"evidence_envelopes.jsonl").write_text("".join(json.dumps(e)+"\n" for e in envs),encoding="utf-8")
    with (out/"assertions.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=["control_id","control_name","assertion","result","detail"]);w.writeheader();w.writerows(arows)
    with (out/"evidence_sources.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=["control_id","source"]);w.writeheader();w.writerows(srows)

    report={"collector_id":"HS-CONTINUOUS-COMPLIANCE","collector_version":"2B2.3","control_count":2,"status_counts":{},"promotion_candidate_count":sum(e["promotion_candidate"] for e in envs)}
    for e in envs:report["status_counts"][e["status"]]=report["status_counts"].get(e["status"],0)+1
    (out/"collector_report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps(report,indent=2))

if __name__=="__main__":main()




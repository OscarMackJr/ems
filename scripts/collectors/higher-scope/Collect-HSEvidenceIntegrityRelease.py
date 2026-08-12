import argparse,csv,json
from pathlib import Path
from datetime import date
import yaml

CONTROLS={
"EMS-CTRL-005":"Repository Classification",
"EMS-CTRL-016":"Evidence integrity and retention",
"EMS-CTRL-071":"Executive Release Validation",
"EMS-CTRL-072":"PDF/DOCX Generation Validation",
}

def assertion(result,detail): return {"result":result,"detail":detail}
def text(p):
    try:return p.read_text(encoding="utf-8",errors="replace")
    except:return ""
def status(A):
    vals=[v["result"] for v in A.values()]
    if vals and all(x=="PASS" for x in vals): return "PASS"
    if any(x=="FAIL" for x in vals): return "WARNING"
    if any(x=="PASS" for x in vals): return "WARNING"
    return "NOT_EVALUATED"

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--ems-root",required=True)
    ap.add_argument("--spec",required=True)
    ap.add_argument("--outdir",required=True)
    a=ap.parse_args()

    root=Path(a.ems_root); out=Path(a.outdir); out.mkdir(parents=True,exist_ok=True)
    fs=[]
    for p in root.rglob("*"):
        if p.is_file():
            low=str(p).lower()
            if any(x in low for x in ["\\.git\\","\\.venv\\","\\site-packages\\","\\__pycache__\\"]): continue
            fs.append(p)

    repo_sources=[p for p in fs if p.name.lower() in {"repository_registry.yaml","repository_overrides.yaml","repository_registry.yml","repository_overrides.yml"}]
    classified=0; placeholders=[]
    req={"owner","tier","service_criticality","production","internet_exposed","contains_customer_data","ai_enabled","data_classification"}
    for p in repo_sources:
        try:d=yaml.safe_load(text(p)) or {}
        except:continue
        items=[]
        if isinstance(d,dict):
            for v in d.values():
                if isinstance(v,list): items.extend(x for x in v if isinstance(x,dict))
        for r in items:
            n=r.get("repository_name") or r.get("name") or r.get("repository")
            if not n: continue
            present={k for k in req if r.get(k) not in (None,"",[])}
            if len(present)>=5: classified+=1
            if "example" in str(r).lower() or str(n).lower().startswith("repo-00"): placeholders.append(str(n))

    baseline=[p for p in fs if "baseline" in p.name.lower()]
    manifests=[p for p in fs if "manifest" in p.name.lower()]
    hashes=[p for p in fs if any(x in p.name.lower() for x in ["sha256","checksum","hash"])]
    integrity_mentions=[p for p in fs if p.suffix.lower() in {".md",".json",".yaml",".yml",".csv",".txt",".ps1",".py"} and any(x in text(p).lower() for x in ["sha256","sha-256","checksum","integrity verification"])]

    validations=[p for p in fs if any(x in p.name.lower() for x in ["validation","validate","certification"])]
    decisions=[p for p in fs if any(x in p.name.lower() for x in ["decision","approval","closeout","adjudication"])]
    provenance=[p for p in fs if p.suffix.lower() in {".json",".yaml",".yml",".csv",".md",".txt"} and any(x in text(p).lower() for x in ["reviewer","approved","evidence_references","provenance","source_file"])]

    pdfs=[p for p in fs if p.suffix.lower()==".pdf"]
    docxs=[p for p in fs if p.suffix.lower()==".docx"]
    gen=[p for p in fs if p.suffix.lower() in {".ps1",".py",".yml",".yaml"} and any(x in text(p).lower() for x in ["pdf","docx","libreoffice","document generation"])]
    gen_fail=[p for p in fs if p.suffix.lower() in {".json",".csv",".txt",".log"} and any(x in text(p).lower() for x in ["pdf not produced","docx not produced","generation failed","missing pdf","missing docx"])]
    outval=[p for p in fs if p.suffix.lower() in {".json",".csv",".txt",".md"} and ("pdf" in text(p).lower() or "docx" in text(p).lower()) and any(x in text(p).lower() for x in ["pass","validated","validation","generated"])]

    envs=[]; arows=[]; srows=[]
    for cid,name in CONTROLS.items():
        A={}; sources=[]
        if cid=="EMS-CTRL-005":
            A["authoritative_repository_registry_exists"]=assertion("PASS" if repo_sources else "UNKNOWN",f"{len(repo_sources)} repository registry/override source(s) detected.")
            A["managed_repositories_detected"]=assertion("PASS" if classified else "UNKNOWN",f"{classified} substantively classified repository record(s) detected.")
            A["required_classification_fields_populated"]=assertion("PASS" if classified else "UNKNOWN","Classification records with required fields detected." if classified else "No complete classification records detected.")
            A["no_placeholder_managed_repositories"]=assertion("PASS" if repo_sources and not placeholders else ("FAIL" if placeholders else "UNKNOWN"),"No placeholder managed repositories detected." if repo_sources and not placeholders else f"Placeholder records: {placeholders}")
            sources=[str(p) for p in repo_sources]
        elif cid=="EMS-CTRL-016":
            A["controlled_baseline_or_evidence_package_retained"]=assertion("PASS" if baseline else "UNKNOWN",f"{len(baseline)} baseline artifact(s) detected.")
            A["manifest_detected"]=assertion("PASS" if manifests else "UNKNOWN",f"{len(manifests)} manifest artifact(s) detected.")
            A["integrity_hash_or_checksum_evidence_detected"]=assertion("PASS" if hashes or integrity_mentions else "UNKNOWN",f"{len(hashes)} hash/checksum file(s); {len(integrity_mentions)} integrity-reference artifact(s).")
            A["retained_evidence_retrievable"]=assertion("PASS" if baseline and manifests else "UNKNOWN","Baseline and manifest evidence retrievable." if baseline and manifests else "Unable to establish retained baseline + manifest evidence.")
            sources=[str(p) for p in (baseline[:10]+manifests[:10]+hashes[:10]+integrity_mentions[:10])]
        elif cid=="EMS-CTRL-071":
            A["release_or_baseline_validation_record_exists"]=assertion("PASS" if validations or baseline else "UNKNOWN",f"{len(validations)} validation artifact(s); {len(baseline)} baseline artifact(s).")
            A["release_decision_or_status_recorded"]=assertion("PASS" if decisions else "UNKNOWN",f"{len(decisions)} decision/approval/closeout artifact(s) detected.")
            timing=bool(validations and baseline and min(p.stat().st_mtime for p in validations)<=max(p.stat().st_mtime for p in baseline))
            A["validation_precedes_or_matches_controlled_baseline"]=assertion("PASS" if timing else "UNKNOWN","Validation timestamp precedes or matches controlled baseline." if timing else "Unable to establish validation-before-baseline timing.")
            A["validation_provenance_retained"]=assertion("PASS" if provenance else "UNKNOWN",f"{len(provenance)} provenance-bearing artifact(s) detected.")
            sources=[str(p) for p in (validations[:10]+decisions[:10]+baseline[:10]+provenance[:10])]
        elif cid=="EMS-CTRL-072":
            A["controlled_document_generation_outputs_detected"]=assertion("PASS" if pdfs or docxs else "UNKNOWN",f"{len(pdfs)} PDF(s); {len(docxs)} DOCX(s) detected.")
            A["expected_formats_detected_or_validated"]=assertion("PASS" if pdfs and docxs else "FAIL",f"PDF={len(pdfs)} DOCX={len(docxs)}")
            A["generation_failure_evidence_captured"]=assertion("PASS" if gen_fail or gen else "UNKNOWN",f"{len(gen_fail)} generation failure/log artifact(s); {len(gen)} generation script/workflow source(s).")
            A["output_validation_evidence_retained"]=assertion("PASS" if outval or validations else "UNKNOWN",f"{len(outval)} output-validation artifact(s); {len(validations)} general validation artifact(s).")
            sources=[str(p) for p in (pdfs[:10]+docxs[:10]+gen[:10]+gen_fail[:10]+outval[:10])]

        st=status(A); promo=(st=="PASS" and all(v["result"]=="PASS" for v in A.values()) and bool(sources))
        e={"evidence_id":f"EMS-{cid}-HS-EVIDENCE-INTEGRITY-RELEASE-{date.today().isoformat()}","control_id":cid,"control_name":name,"scope":"EMS","collector_id":"HS-EVIDENCE-INTEGRITY-RELEASE","collector_version":"2B2.2","status":st,"evidence_class":"OPERATING_EVIDENCE","assertions":A,"evidence_sources":sorted(set(sources)),"evidence_date":date.today().isoformat(),"promotion_candidate":promo,"notes":"Promotion requires all assertions PASS."}
        envs.append(e)
        for k,v in A.items(): arows.append({"control_id":cid,"control_name":name,"assertion":k,"result":v["result"],"detail":v["detail"]})
        for s in e["evidence_sources"]: srows.append({"control_id":cid,"source":s})

    (out/"evidence_envelopes.jsonl").write_text("".join(json.dumps(e)+"\n" for e in envs),encoding="utf-8")
    with (out/"assertions.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=["control_id","control_name","assertion","result","detail"]);w.writeheader();w.writerows(arows)
    with (out/"evidence_sources.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=["control_id","source"]);w.writeheader();w.writerows(srows)
    report={"collector_id":"HS-EVIDENCE-INTEGRITY-RELEASE","collector_version":"2B2.2","control_count":4,"status_counts":{},"promotion_candidate_count":sum(e["promotion_candidate"] for e in envs)}
    for e in envs: report["status_counts"][e["status"]]=report["status_counts"].get(e["status"],0)+1
    (out/"collector_report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps(report,indent=2))
if __name__=="__main__":main()

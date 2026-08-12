import argparse,csv,json,re
from pathlib import Path
from datetime import date

SPEC_CONTROLS={
"EMS-CTRL-073":("Engineering KPI Review","ORGANIZATION"),
"EMS-CTRL-074":("Quarterly Management Review","ORGANIZATION"),
"EMS-CTRL-077":("Technical Debt Register","ORGANIZATION"),
"EMS-CTRL-078":("Lessons Learned Review","ORGANIZATION"),
"EMS-CTRL-080":("Annual EMS Review","EMS"),
}

def assertion(result,detail): return {"result":result,"detail":detail}
def txt(p):
    try:return p.read_text(encoding="utf-8",errors="replace")
    except:return ""
def status(A):
    vals=[v["result"] for v in A.values()]
    if vals and all(x=="PASS" for x in vals): return "PASS"
    if any(x=="FAIL" for x in vals): return "WARNING"
    if any(x=="PASS" for x in vals): return "WARNING"
    return "NOT_EVALUATED"

def candidate_files(root):
    out=[]
    for p in root.rglob("*"):
        if not p.is_file(): continue
        low=str(p).lower().replace("/","\\")
        if any(x in low for x in ["\\.git\\","\\.venv\\","\\site-packages\\","\\__pycache__\\"]): continue
        if p.suffix.lower() not in {".md",".txt",".csv",".json",".yaml",".yml",".docx",".pdf"}: continue
        # Prior compliance outputs do not prove management review.
        if any(x in p.name.lower() for x in ["effective_compliance","repository_control_compliance","compliance_postpolicy"]): continue
        out.append(p)
    return out

def textual_candidates(fs, terms):
    hits=[]
    for p in fs:
        if p.suffix.lower() in {".docx",".pdf"}:
            name=p.name.lower()
            if any(t in name for t in terms): hits.append(p)
            continue
        t=txt(p).lower()
        if any(term in p.name.lower() or term in t for term in terms):
            hits.append(p)
    return hits

def has_any(texts, terms):
    alltext="\n".join(texts).lower()
    return any(t in alltext for t in terms)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--ems-root",required=True)
    ap.add_argument("--outdir",required=True)
    a=ap.parse_args()

    root=Path(a.ems_root); out=Path(a.outdir); out.mkdir(parents=True,exist_ok=True)
    fs=candidate_files(root)

    envs=[];arows=[];srows=[]

    for cid,(name,scope) in SPEC_CONTROLS.items():
        A={};sources=[]

        if cid=="EMS-CTRL-073":
            hits=textual_candidates(fs,["kpi","key performance","engineering metrics","scorecard"])
            texts=[txt(p) for p in hits if p.suffix.lower() not in {".pdf",".docx"}]
            A["kpi_review_artifact_detected"]=assertion("PASS" if hits else "UNKNOWN",f"{len(hits)} KPI/scorecard review artifact(s) detected.")
            A["engineering_metrics_present"]=assertion("PASS" if has_any(texts,["metric","kpi","availability","defect","lead time","deployment","coverage","quality"]) else "UNKNOWN","Engineering metric terms detected." if has_any(texts,["metric","kpi","availability","defect","lead time","deployment","coverage","quality"]) else "No engineering metric terms detected.")
            A["review_owner_or_approver_present"]=assertion("PASS" if has_any(texts,["owner","reviewer","approved by","approver","cto","cso","engineering leadership"]) else "UNKNOWN","Review owner/approver signal detected.")
            A["review_date_identifiable"]=assertion("PASS" if any(re.search(r'20\d{2}[-/]\d{1,2}[-/]\d{1,2}',t) for t in texts) else "UNKNOWN","Review date detected." if any(re.search(r'20\d{2}[-/]\d{1,2}[-/]\d{1,2}',t) for t in texts) else "No explicit review date detected.")
            A["review_outcome_or_action_recorded"]=assertion("PASS" if has_any(texts,["action","decision","follow-up","follow up","approved","remediate","improvement"]) else "UNKNOWN","Outcome/action signal detected.")
            sources=[str(p) for p in hits[:20]]

        elif cid=="EMS-CTRL-074":
            hits=textual_candidates(fs,["quarterly review","quarterly management","q1 review","q2 review","q3 review","q4 review"])
            texts=[txt(p) for p in hits if p.suffix.lower() not in {".pdf",".docx"}]
            A["quarterly_review_artifact_detected"]=assertion("PASS" if hits else "UNKNOWN",f"{len(hits)} quarterly management-review artifact(s) detected.")
            A["management_participation_detected"]=assertion("PASS" if has_any(texts,["management","executive","cto","cso","leadership"]) else "UNKNOWN","Management/executive participation signal detected.")
            A["review_period_identifiable"]=assertion("PASS" if has_any(texts,["q1","q2","q3","q4","quarter"]) else "UNKNOWN","Quarter/review period identified.")
            A["decisions_or_actions_recorded"]=assertion("PASS" if has_any(texts,["decision","action","approved","follow-up","follow up"]) else "UNKNOWN","Decision/action signal detected.")
            A["review_evidence_retained"]=assertion("PASS" if hits and any("\\generated\\" in str(p).lower().replace("/","\\") or "\\docs\\" in str(p).lower().replace("/","\\") or "\\evidence\\" in str(p).lower().replace("/","\\") for p in hits) else "UNKNOWN","Retained review artifact detected in controlled tree.")
            sources=[str(p) for p in hits[:20]]

        elif cid=="EMS-CTRL-077":
            hits=textual_candidates(fs,["technical debt","tech debt","debt register","debt backlog"])
            texts=[txt(p) for p in hits if p.suffix.lower() not in {".pdf",".docx"}]
            A["technical_debt_register_detected"]=assertion("PASS" if hits else "UNKNOWN",f"{len(hits)} technical-debt artifact(s) detected.")
            A["debt_items_identifiable"]=assertion("PASS" if has_any(texts,["item","id","debt","issue","backlog"]) else "UNKNOWN","Debt item identifiers/records detected.")
            A["owner_or_accountability_recorded"]=assertion("PASS" if has_any(texts,["owner","assigned","accountable"]) else "UNKNOWN","Owner/accountability signal detected.")
            A["status_or_priority_recorded"]=assertion("PASS" if has_any(texts,["status","priority","severity","open","closed"]) else "UNKNOWN","Status/priority signal detected.")
            A["retained_history_detected"]=assertion("PASS" if has_any(texts,["created","updated","closed","history","date"]) else "UNKNOWN","History/date signal detected.")
            sources=[str(p) for p in hits[:20]]

        elif cid=="EMS-CTRL-078":
            hits=textual_candidates(fs,["lessons learned","postmortem","retrospective","retro"])
            texts=[txt(p) for p in hits if p.suffix.lower() not in {".pdf",".docx"}]
            A["lessons_learned_artifact_detected"]=assertion("PASS" if hits else "UNKNOWN",f"{len(hits)} lessons-learned/postmortem artifact(s) detected.")
            A["source_event_or_project_identifiable"]=assertion("PASS" if has_any(texts,["project","incident","release","event","initiative"]) else "UNKNOWN","Source event/project signal detected.")
            A["lessons_or_findings_recorded"]=assertion("PASS" if has_any(texts,["lesson","finding","what went well","what went wrong","root cause"]) else "UNKNOWN","Lesson/finding content detected.")
            A["actions_or_followups_recorded"]=assertion("PASS" if has_any(texts,["action","follow-up","follow up","owner","next step"]) else "UNKNOWN","Action/follow-up signal detected.")
            A["review_evidence_retained"]=assertion("PASS" if hits else "UNKNOWN","Lessons-learned evidence retained.")
            sources=[str(p) for p in hits[:20]]

        elif cid=="EMS-CTRL-080":
            hits=textual_candidates(fs,["annual ems review","annual review","ems review"])
            texts=[txt(p) for p in hits if p.suffix.lower() not in {".pdf",".docx"}]
            A["annual_review_artifact_detected"]=assertion("PASS" if hits else "UNKNOWN",f"{len(hits)} annual/EMS review artifact(s) detected.")
            A["ems_scope_explicit"]=assertion("PASS" if has_any(texts,["ems","engineering management system"]) else "UNKNOWN","EMS scope explicitly referenced.")
            A["review_year_identifiable"]=assertion("PASS" if any(re.search(r'\b20\d{2}\b',t) for t in texts) else "UNKNOWN","Review year detected." if any(re.search(r'\b20\d{2}\b',t) for t in texts) else "No review year detected.")
            A["review_outcome_or_approval_recorded"]=assertion("PASS" if has_any(texts,["approved","decision","outcome","action","accepted"]) else "UNKNOWN","Review outcome/approval signal detected.")
            A["annual_review_evidence_retained"]=assertion("PASS" if hits and any("\\docs\\" in str(p).lower().replace("/","\\") or "\\evidence\\" in str(p).lower().replace("/","\\") or "\\releases\\" in str(p).lower().replace("/","\\") for p in hits) else "UNKNOWN","Retained annual review artifact detected.")
            sources=[str(p) for p in hits[:20]]

        st=status(A)
        promo=(st=="PASS" and all(v["result"]=="PASS" for v in A.values()) and bool(sources))
        e={
            "evidence_id":f"{scope}-{cid}-HS-MANAGEMENT-REVIEW-{date.today().isoformat()}",
            "control_id":cid,"control_name":name,"scope":scope,
            "collector_id":"HS-MANAGEMENT-REVIEW","collector_version":"2B2.4",
            "status":st,"evidence_class":"OPERATING_EVIDENCE",
            "assertions":A,"evidence_sources":sorted(set(sources)),
            "evidence_date":date.today().isoformat(),
            "promotion_candidate":promo,
            "notes":"Management-review controls require actual retained review/register artifacts; policy or prior compliance outputs are not sufficient."
        }
        envs.append(e)
        for k,v in A.items(): arows.append({"control_id":cid,"control_name":name,"scope":scope,"assertion":k,"result":v["result"],"detail":v["detail"]})
        for s in e["evidence_sources"]: srows.append({"control_id":cid,"scope":scope,"source":s})

    (out/"evidence_envelopes.jsonl").write_text("".join(json.dumps(e)+"\n" for e in envs),encoding="utf-8")
    with (out/"assertions.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=["control_id","control_name","scope","assertion","result","detail"]);w.writeheader();w.writerows(arows)
    with (out/"evidence_sources.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=["control_id","scope","source"]);w.writeheader();w.writerows(srows)

    report={"collector_id":"HS-MANAGEMENT-REVIEW","collector_version":"2B2.4","control_count":5,"status_counts":{},"promotion_candidate_count":sum(e["promotion_candidate"] for e in envs)}
    for e in envs: report["status_counts"][e["status"]]=report["status_counts"].get(e["status"],0)+1
    (out/"collector_report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps(report,indent=2))

if __name__=="__main__":main()

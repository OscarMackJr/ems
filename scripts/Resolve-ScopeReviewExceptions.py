import argparse,csv,json,re
from pathlib import Path
import yaml

DEFERRED={
"EMS-CTRL-001","EMS-CTRL-002","EMS-CTRL-003","EMS-CTRL-004","EMS-CTRL-005","EMS-CTRL-006",
"EMS-CTRL-007","EMS-CTRL-008","EMS-CTRL-016","EMS-CTRL-022","EMS-CTRL-023","EMS-CTRL-024",
"EMS-CTRL-055","EMS-CTRL-056","EMS-CTRL-057","EMS-CTRL-058","EMS-CTRL-059","EMS-CTRL-060"
}

EXPLICIT={
"EMS-CTRL-022":("PLATFORM","APPROVED","Security advisory monitoring is primarily provided by shared security/platform capabilities and may be inherited by repositories."),
"EMS-CTRL-023":("ORGANIZATION","APPROVED","Vulnerability remediation targets are established as organizational security policy and applied across repositories/services."),
"EMS-CTRL-024":("ORGANIZATION","APPROVED","Security exception approval is an organizational governance decision, not a repository-local implementation control.")
}

def walk_controls(obj):
    found=[]
    if isinstance(obj,dict):
        # Common control record patterns
        cid=obj.get("control_id") or obj.get("id")
        if isinstance(cid,str) and re.fullmatch(r"EMS-CTRL-\d{3}",cid):
            found.append(obj)
        for v in obj.values():
            found.extend(walk_controls(v))
    elif isinstance(obj,list):
        for v in obj:
            found.extend(walk_controls(v))
    return found

def text_of(c):
    pieces=[]
    for k in ("name","control_name","title","description","purpose","requirement","requirements","objective","statement"):
        v=c.get(k)
        if isinstance(v,str): pieces.append(v)
        elif isinstance(v,list): pieces.extend(str(x) for x in v)
    return " ".join(pieces).strip()

def scope_recommendation(text):
    t=text.lower()
    # High-confidence EMS governance/doc controls
    if any(x in t for x in [
        "engineering management system","ems governance","controlled document",
        "document metadata","cross-reference","revision history","annual ems",
        "requirements traceability"
    ]):
        return "EMS","HIGH","Semantics indicate the control governs EMS/document-control operation."
    if any(x in t for x in [
        "management review","quarterly review","policy approval","executive",
        "organization-wide","organizational","training","awareness","exception approval",
        "remediation target","governance committee"
    ]):
        return "ORGANIZATION","HIGH","Semantics indicate an entity-wide governance/policy obligation."
    if any(x in t for x in [
        "repository","branch","pull request","commit","codeowners","source code",
        "dependency","sbom","unit test","workflow"
    ]):
        return "REPOSITORY","HIGH","Semantics indicate repository-local implementation/evidence."
    if any(x in t for x in [
        "cloud platform","shared platform","iam","secrets management","security advisory",
        "environment separation","infrastructure platform"
    ]):
        return "PLATFORM","MEDIUM","Semantics indicate shared platform implementation/evidence."
    if any(x in t for x in [
        "service","runtime","disaster recovery","rollback","restore","availability","performance"
    ]):
        return "SERVICE","MEDIUM","Semantics indicate a deployable service/runtime boundary."
    if any(x in t for x in [
        "application","schema","database migration"
    ]):
        return "APPLICATION","MEDIUM","Semantics indicate an application/data boundary."
    return "","LOW","No sufficiently strong semantic scope signal was detected."

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--catalog",required=True)
    ap.add_argument("--reviewed-queue",required=True)
    ap.add_argument("--out",required=True)
    ap.add_argument("--exceptions",required=True)
    a=ap.parse_args()

    cat=yaml.safe_load(Path(a.catalog).read_text(encoding="utf-8")) or {}
    controls=walk_controls(cat)
    cmap={}
    for c in controls:
        cid=c.get("control_id") or c.get("id")
        if cid: cmap[cid]=c

    with Path(a.reviewed_queue).open(encoding="utf-8-sig",newline="") as fh:
        rows=list(csv.DictReader(fh))

    unresolved=[]
    for r in rows:
        cid=r["control_id"]
        if cid not in DEFERRED:
            continue

        c=cmap.get(cid)
        if c:
            name=c.get("control_name") or c.get("name") or c.get("title") or r["control_name"]
            r["control_name"]=name
            semantic=text_of(c)
        else:
            semantic=""

        if cid in EXPLICIT:
            target,decision,rationale=EXPLICIT[cid]
            r["reviewer_decision"]=decision if target==r["current_scope"] else "RECLASSIFY"
            r["proposed_scope"]=target
            r["reviewer_rationale"]=rationale
            r["reviewer"]="EMS Architecture Exception Resolver"
            continue

        target,confidence,rationale=scope_recommendation(semantic)
        if target and confidence=="HIGH":
            r["reviewer_decision"]="APPROVED" if target==r["current_scope"] else "RECLASSIFY"
            r["proposed_scope"]=target
            r["reviewer_rationale"]=rationale
            r["reviewer"]="EMS Architecture Exception Resolver"
        else:
            r["reviewer_decision"]="DEFER"
            r["proposed_scope"]=target
            r["reviewer_rationale"]=(
                f"{rationale} Authoritative semantics: {semantic[:800]}"
            )
            unresolved.append({
                "control_id":cid,
                "control_name":r["control_name"],
                "current_scope":r["current_scope"],
                "suggested_scope":target,
                "confidence":confidence,
                "authoritative_semantics":semantic[:1500]
            })

    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh,fieldnames=list(rows[0].keys()))
        w.writeheader();w.writerows(rows)

    ex=Path(a.exceptions);ex.parent.mkdir(parents=True,exist_ok=True)
    fields=["control_id","control_name","current_scope","suggested_scope","confidence","authoritative_semantics"]
    with ex.open("w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh,fieldnames=fields);w.writeheader();w.writerows(unresolved)

    decisions={}
    for r in rows:
        decisions[r["reviewer_decision"]]=decisions.get(r["reviewer_decision"],0)+1
    print(json.dumps({
        "catalog_controls_found":len(cmap),
        "decision_counts":decisions,
        "remaining_deferred":len(unresolved)
    },indent=2))

if __name__=="__main__":main()

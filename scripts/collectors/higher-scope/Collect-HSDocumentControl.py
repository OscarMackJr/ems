import argparse,csv,json,re,subprocess
from pathlib import Path
from datetime import date
import yaml

CONTROL_IDS=["EMS-CTRL-001","EMS-CTRL-002","EMS-CTRL-008","EMS-CTRL-067","EMS-CTRL-068","EMS-CTRL-069","EMS-CTRL-070"]

def read_text(p):
    try:
        return p.read_text(encoding="utf-8",errors="replace")
    except Exception:
        return ""

def all_files(root):
    for p in root.rglob("*"):
        if p.is_file():
            low=str(p).lower()
            if any(x in low for x in ["\\.git\\","\\.venv\\","\\site-packages\\","\\__pycache__\\"]):
                continue
            yield p

def yaml_json_docs(root):
    docs=[]
    for p in all_files(root):
        if p.suffix.lower() not in {".yaml",".yml",".json"}:
            continue
        try:
            obj=json.loads(read_text(p)) if p.suffix.lower()==".json" else yaml.safe_load(read_text(p))
            docs.append((p,obj))
        except Exception:
            pass
    return docs

def walk_ids(obj, ids):
    if isinstance(obj,dict):
        cid=obj.get("control_id") or obj.get("id")
        if isinstance(cid,str) and re.fullmatch(r"EMS-CTRL-\d{3}",cid):
            ids.append(cid)
        for v in obj.values(): walk_ids(v,ids)
    elif isinstance(obj,list):
        for v in obj: walk_ids(v,ids)

def metadata_signals(obj, out):
    if isinstance(obj,dict):
        keys={str(k).lower() for k in obj}
        if any(k in keys for k in {"owner","authority","policy_owner","scope_owner"}): out["owner"]=True
        if any(k in keys for k in {"status","classification_status","document_status"}): out["status"]=True
        if any(k in keys for k in {"version","revision","document_version"}): out["version"]=True
        for v in obj.values(): metadata_signals(v,out)
    elif isinstance(obj,list):
        for v in obj: metadata_signals(v,out)

def git(cmd, cwd):
    try:
        r=subprocess.run(["git"]+cmd,cwd=cwd,text=True,capture_output=True,encoding="utf-8",errors="replace")
        return r.returncode,r.stdout.strip(),r.stderr.strip()
    except Exception as e:
        return 1,"",str(e)

def assertion(result, detail):
    return {"result":result,"detail":detail}

def status_from_assertions(assertions):
    vals=[x["result"] for x in assertions.values()]
    if vals and all(v=="PASS" for v in vals): return "PASS"
    if any(v=="FAIL" for v in vals): return "WARNING"
    if any(v=="PASS" for v in vals): return "WARNING"
    return "NOT_EVALUATED"

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--ems-root",required=True)
    ap.add_argument("--spec",required=True)
    ap.add_argument("--outdir",required=True)
    a=ap.parse_args()

    root=Path(a.ems_root)
    spec=json.loads(Path(a.spec).read_text(encoding="utf-8"))
    out=Path(a.outdir);out.mkdir(parents=True,exist_ok=True)

    docs=yaml_json_docs(root)
    files=list(all_files(root))
    file_paths=[str(p) for p in files]
    texts={p:read_text(p) for p in files if p.suffix.lower() in {".md",".txt",".yaml",".yml",".json",".csv",".ps1",".py"}}

    # Separate authoritative definitions from ordinary references.
    authoritative_definition_files=[]
    for p,obj in docs:
        low=str(p).lower().replace("/","\\")
        name=p.name.lower()

        if any(x in low for x in [
            "\\generated\\",
            "\\releases\\",
            "\\release\\",
            ".bak",
            ".pre-",
            "\\evidence\\",
        ]):
            continue

        if name in {
            "control_catalog.yaml",
            "control_catalog.yml",
            "control_registry.yaml",
            "control_registry.yml",
        }:
            authoritative_definition_files.append((p,obj))

    definition_ids=[]
    for _,obj in authoritative_definition_files:
        walk_ids(obj,definition_ids)

    reference_ids=[]
    for _,obj in docs:
        walk_ids(obj,reference_ids)

    unique_definition_ids=set(definition_ids)
    unique_reference_ids=set(reference_ids)

    from collections import Counter
    definition_counts=Counter(definition_ids)
    duplicate_definition_ids=sorted(
        cid for cid,count in definition_counts.items()
        if count > 1
    )

    meta={"owner":False,"status":False,"version":False}
    for _,obj in docs: metadata_signals(obj,meta)

    # Cross-reference analysis for EMS control ids.
    reference_files=[]
    referenced=set()
    for p,t in texts.items():
        found=set(re.findall(r"EMS-CTRL-\d{3}",t))
        if found:
            reference_files.append(str(p))
            referenced |= found
    valid={f"EMS-CTRL-{i:03d}" for i in range(1,81)}
    dangling=sorted(x for x in referenced if x not in valid)

    # Requirements / mappings
    trace_sources=[str(p) for p in files if any(x in p.name.lower() for x in ["trace","requirement","mapping","control_catalog","control_registry"])]
    mapping_hits=[p for p,t in texts.items() if ("requirement" in t.lower() and "EMS-CTRL-" in t)]

    # Evidence/control association
    evidence_paths=[str(p) for p in files if "evidence" in str(p).lower() or "adjudication" in str(p).lower() or "release" in str(p).lower()]
    provenance_hits=[str(p) for p,t in texts.items() if any(k in t.lower() for k in ["source_file","evidence_source","evidence_references","provenance","collector_id"])]

    # Governance authority / inventory
    governance_sources=[str(p) for p in files if any(x in p.name.lower() for x in ["policy","governance","standard","control_catalog","control_registry"])]
    inventory_sources=[str(p) for p in files if any(x in p.name.lower() for x in ["catalog","registry","manifest","document"])]
    version_release_sources=[str(p) for p in files if any(x in p.name.lower() for x in ["manifest","release","changelog","revision"])]

    rc,head,_=git(["rev-parse","HEAD"],root)
    rc2,log,_=git(["log","--oneline","-5"],root)
    rc3,tags,_=git(["tag","--list"],root)

    envelopes=[]
    assertion_rows=[]
    source_rows=[]

    for cid in CONTROL_IDS:
        name=spec["controls"][cid]["name"]
        A={}
        sources=[]

        if cid=="EMS-CTRL-001":
            A["governance_authority_source_exists"]=assertion("PASS" if governance_sources else "UNKNOWN",f"{len(governance_sources)} governance/control authority source(s) detected.")
            A["controlled_version_or_release_marker_exists"]=assertion("PASS" if version_release_sources or (rc3==0 and tags) else "UNKNOWN","Release/version marker detected." if version_release_sources or tags else "No release/version marker detected.")
            A["approval_or_status_metadata_exists"]=assertion("PASS" if meta["status"] else "UNKNOWN","Status metadata detected." if meta["status"] else "No status metadata signal detected.")
            A["governance_source_discoverable"]=assertion("PASS" if governance_sources else "UNKNOWN","Governance/control source discoverable." if governance_sources else "No governance/control source discoverable.")
            sources=governance_sources[:10]+version_release_sources[:5]

        elif cid=="EMS-CTRL-002":
            A["controlled_document_inventory_detected"]=assertion(
                "PASS" if authoritative_definition_files else "UNKNOWN",
                f"{len(authoritative_definition_files)} authoritative control-definition source(s) detected."
            )
            A["controlled_ids_unique"]=assertion(
                "PASS" if authoritative_definition_files and not duplicate_definition_ids else (
                    "FAIL" if duplicate_definition_ids else "UNKNOWN"
                ),
                (
                    f"definition_occurrence_count={len(definition_ids)}; "
                    f"unique_definition_count={len(unique_definition_ids)}; "
                    f"reference_occurrence_count={len(reference_ids)}; "
                    f"unique_reference_count={len(unique_reference_ids)}; "
                    f"duplicate_definitions={duplicate_definition_ids}"
                )
            )
            A["version_or_status_metadata_detected"]=assertion(
                "PASS" if meta["version"] or meta["status"] else "UNKNOWN",
                f"version={meta['version']} status={meta['status']}"
            )
            A["controlled_artifacts_retrievable"]=assertion(
                "PASS" if files else "UNKNOWN",
                f"{len(files)} repository artifact(s) traversable."
            )
            sources=[str(p) for p,_ in authoritative_definition_files]

        elif cid=="EMS-CTRL-008":
            A["evidence_artifact_structure_exists"]=assertion("PASS" if (root/"evidence").exists() or evidence_paths else "UNKNOWN","Evidence directory/artifacts detected." if (root/"evidence").exists() or evidence_paths else "No evidence structure detected.")
            A["evidence_control_association_detected"]=assertion("PASS" if any("EMS-CTRL-" in texts.get(p,"") for p in texts) else "UNKNOWN","Control identifiers detected in controlled artifacts.")
            A["evidence_provenance_detected"]=assertion("PASS" if provenance_hits else "UNKNOWN",f"{len(provenance_hits)} provenance-bearing artifact(s) detected.")
            A["controlled_evidence_location_detected"]=assertion("PASS" if (root/"evidence").exists() or (root/"releases").exists() else "UNKNOWN","Controlled evidence/release location exists.")
            sources=(evidence_paths[:15]+provenance_hits[:10])

        elif cid=="EMS-CTRL-067":
            A["controlled_ids_detected"]=assertion("PASS" if unique_definition_ids else "UNKNOWN",f"{len(unique_definition_ids)} authoritative EMS control ids detected.")
            A["metadata_owner_or_authority_detected"]=assertion("PASS" if meta["owner"] else "UNKNOWN","Owner/authority metadata detected." if meta["owner"] else "No owner/authority metadata detected.")
            A["metadata_status_detected"]=assertion("PASS" if meta["status"] else "UNKNOWN","Status metadata detected." if meta["status"] else "No status metadata detected.")
            A["metadata_version_detected"]=assertion("PASS" if meta["version"] else "UNKNOWN","Version metadata detected." if meta["version"] else "No version metadata detected.")
            sources=[str(p) for p,_ in docs[:20]]

        elif cid=="EMS-CTRL-068":
            A["cross_reference_sources_detected"]=assertion("PASS" if reference_files else "UNKNOWN",f"{len(reference_files)} control-reference-bearing file(s) detected.")
            A["referenced_control_ids_resolve"]=assertion("PASS" if referenced and not dangling else ("FAIL" if dangling else "UNKNOWN"),f"{len(referenced)} referenced control ids; dangling={len(dangling)}.")
            A["no_dangling_control_references"]=assertion("PASS" if referenced and not dangling else ("FAIL" if dangling else "UNKNOWN"),"No dangling control references." if referenced and not dangling else f"Dangling references: {dangling[:20]}")
            sources=reference_files[:20]

        elif cid=="EMS-CTRL-069":
            A["requirements_or_traceability_sources_detected"]=assertion("PASS" if trace_sources else "UNKNOWN",f"{len(trace_sources)} requirement/traceability/mapping source(s) detected.")
            A["control_mapping_detected"]=assertion("PASS" if mapping_hits or trace_sources else "UNKNOWN",f"{len(mapping_hits)} direct requirement-to-control text mapping source(s) detected.")
            A["orphaned_required_mappings_zero"]=assertion("PASS" if trace_sources and not dangling else ("FAIL" if dangling else "UNKNOWN"),"No invalid EMS control references detected in traceable sources." if trace_sources and not dangling else "Unable to establish zero orphaned mappings.")
            sources=trace_sources[:20]+[str(p) for p in mapping_hits[:10]]

        elif cid=="EMS-CTRL-070":
            A["git_repository_detected"]=assertion("PASS" if rc==0 else "UNKNOWN","Git repository detected." if rc==0 else "Git repository not detected.")
            A["git_history_detected"]=assertion("PASS" if rc2==0 and log else "UNKNOWN","Git history detected." if log else "No Git history detected.")
            A["tag_or_release_history_detected"]=assertion("PASS" if (rc3==0 and tags) or version_release_sources else "UNKNOWN","Tag/release history detected." if tags or version_release_sources else "No tag/release history detected.")
            A["current_revision_identifiable"]=assertion("PASS" if rc==0 and head else "UNKNOWN",f"HEAD={head}" if head else "Current revision not identifiable.")
            sources=version_release_sources[:10]
            if head: sources.append("git:HEAD="+head)

        status=status_from_assertions(A)
        promotion=status in {"PASS","WARNING"} and all(x["result"]=="PASS" for x in A.values())

        env={
            "evidence_id":f"EMS-{cid}-HS-DOCUMENT-CONTROL-{date.today().isoformat()}",
            "control_id":cid,
            "control_name":name,
            "scope":"EMS",
            "collector_id":"HS-DOCUMENT-CONTROL",
            "collector_version":spec["version"],
            "status":status,
            "evidence_class":"OPERATING_EVIDENCE",
            "assertions":A,
            "evidence_sources":sorted(set(sources)),
            "evidence_date":date.today().isoformat(),
            "promotion_candidate":promotion,
            "notes":"PASS requires every required assertion to pass. Partial evidence yields WARNING; absence yields NOT_EVALUATED."
        }
        envelopes.append(env)

        for k,v in A.items():
            assertion_rows.append({
                "control_id":cid,"control_name":name,"assertion":k,
                "result":v["result"],"detail":v["detail"]
            })
        for s in env["evidence_sources"]:
            source_rows.append({"control_id":cid,"source":s})

    with (out/"evidence_envelopes.jsonl").open("w",encoding="utf-8") as fh:
        for e in envelopes:
            fh.write(json.dumps(e)+"\n")

    with (out/"assertions.csv").open("w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh,fieldnames=["control_id","control_name","assertion","result","detail"])
        w.writeheader();w.writerows(assertion_rows)

    with (out/"evidence_sources.csv").open("w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh,fieldnames=["control_id","source"])
        w.writeheader();w.writerows(source_rows)

    report={
        "collector_id":"HS-DOCUMENT-CONTROL",
        "collector_version":spec["version"],
        "control_count":len(envelopes),
        "status_counts":{},
        "promotion_candidate_count":sum(e["promotion_candidate"] for e in envelopes)
    }
    for e in envelopes:
        report["status_counts"][e["status"]]=report["status_counts"].get(e["status"],0)+1
    (out/"collector_report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps(report,indent=2))

if __name__=="__main__":main()


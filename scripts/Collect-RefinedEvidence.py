import argparse, csv, json, subprocess, base64
from pathlib import Path
import yaml

def gh_api(path):
    p=subprocess.run(["gh","api",path],capture_output=True,text=True,encoding="utf-8",errors="replace")
    if p.returncode!=0:return None,p.stderr.strip()
    if not p.stdout.strip():return {},None
    try:return json.loads(p.stdout),None
    except Exception as e:return None,str(e)

def root_items(repo):
    d,e=gh_api(f"repos/{repo}/contents")
    return d if isinstance(d,list) else [],e

def exists(repo,path):
    d,e=gh_api(f"repos/{repo}/contents/{path}")
    return bool(d)

def workflows(repo):
    d,e=gh_api(f"repos/{repo}/actions/workflows")
    return (d or {}).get("workflows",[]) if d else [],e

def workflow_text(repo):
    texts=[];wfs,_=workflows(repo)
    for w in wfs:
        d,e=gh_api(f"repos/{repo}/contents/{w.get('path','')}")
        if d and d.get("content"):
            try:texts.append(base64.b64decode(d["content"]).decode("utf-8","replace").lower())
            except Exception:pass
    return "\n".join(texts),wfs

def detect_stack(repo):
    items,_=root_items(repo);names={x.get("name","") for x in items};stack=set()
    if "package.json" in names:stack.add("javascript")
    if any(n in names for n in ["pyproject.toml","requirements.txt","Pipfile"]):stack.add("python")
    if "Cargo.toml" in names:stack.add("rust")
    if any(n.endswith(".sln") or n.endswith(".csproj") for n in names):stack.add("dotnet")
    return stack,names

def eval_025(repo):
    stack,names=detect_stack(repo);text,wfs=workflow_text(repo);ev=[]
    if "javascript" in stack and any(x in text for x in ["npm test","npm run test","yarn test","pnpm test","jest","vitest"]):ev.append("javascript_test")
    if "python" in stack and any(x in text for x in ["pytest","python -m unittest","tox","nox"]):ev.append("python_test")
    if "rust" in stack and "cargo test" in text:ev.append("rust_test")
    if "dotnet" in stack and "dotnet test" in text:ev.append("dotnet_test")
    markers=[m for m in ["tests","test","__tests__"] if exists(repo,m)]
    status="PASS" if ev else ("WARNING" if markers else "NOT_EVALUATED")
    return status,{"detected_stack":sorted(stack),"test_commands":ev,"test_markers":markers,"workflow_count":len(wfs)}

def eval_033(repo):
    stack,names=detect_stack(repo);text,wfs=workflow_text(repo)
    deterministic=False;runtime=False
    if "javascript" in stack:
        deterministic |= any(n in names for n in ["package-lock.json","yarn.lock","pnpm-lock.yaml","npm-shrinkwrap.json"])
        runtime |= "actions/setup-node@" in text and ("node-version" in text or "node-version-file" in text)
    if "python" in stack:
        deterministic |= any(n in names for n in ["poetry.lock","Pipfile.lock","requirements.txt"])
        runtime |= "actions/setup-python@" in text and ("python-version" in text or "python-version-file" in text)
    if "rust" in stack:
        deterministic |= "Cargo.lock" in names
        runtime |= "rust-toolchain" in names or "toolchain" in text
    if "dotnet" in stack:
        deterministic |= any(n in names for n in ["packages.lock.json","Directory.Packages.props"])
        runtime |= "global.json" in names or ("actions/setup-dotnet@" in text and "dotnet-version" in text)
    if deterministic and runtime and wfs:status="PASS"
    elif deterministic or runtime or wfs:status="WARNING"
    else:status="NOT_EVALUATED"
    return status,{"detected_stack":sorted(stack),"dependency_resolution_deterministic":deterministic,"runtime_or_toolchain_pinned":runtime,"workflow_present":bool(wfs)}

def eval_artifacts(repo,kind):
    d,e=gh_api(f"repos/{repo}/actions/artifacts?per_page=100")
    if d is None:return "NOT_EVALUATED",{"api_error":e}
    artifacts=d.get("artifacts",[]);text,wfs=workflow_text(repo)
    upload="actions/upload-artifact@" in text
    semantic=any(k in text for k in (["test-results","coverage","junit","trx","pytest"] if kind=="test" else ["build","dist","publish","release"]))
    relevant=upload and semantic
    status="PASS" if artifacts else ("WARNING" if relevant else "NOT_EVALUATED")
    return status,{"artifact_count":len(artifacts),"upload_artifact_action_detected":upload,"relevant_artifact_workflow_detected":relevant}

def eval_015(repo,baseline):
    assertions={}
    for req in baseline.get("required",[]):
        assertions[req["id"]]=any(exists(repo,p) for p in req.get("any_of",[]))
    items,_=root_items(repo);names={x.get("name","") for x in items}
    wfs,_=workflows(repo);assertions["workflow"]=bool(wfs)
    dep=False
    for pat in baseline.get("recognized_dependency_manifests",[]):
        if pat.startswith("*."):
            dep |= any(n.endswith(pat[1:]) for n in names)
        else:dep |= pat in names
    assertions["dependency_manifest"]=dep
    vals=list(assertions.values())
    return ("PASS" if all(vals) else ("WARNING" if any(vals) else "FAIL")),assertions

def eval_079(repo_name,compliance,rollup):
    fail=warn=ne=0;domains={}
    for name,spec in rollup["domains"].items():
        states=[compliance.get((repo_name,c)) for c in spec["controls"]]
        states=[s for s in states if s and s!="NOT_APPLICABLE"]
        domains[name]=states;fail+=states.count("FAIL");warn+=states.count("WARNING");ne+=states.count("NOT_EVALUATED")
    status="FAIL" if fail else ("WARNING" if ne or warn>2 else "PASS")
    return status,{"domains":domains,"fail_count":fail,"warning_count":warn,"not_evaluated_count":ne}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--repositories",required=True);ap.add_argument("--baseline-template",required=True)
    ap.add_argument("--rollup",required=True);ap.add_argument("--compliance",required=True);ap.add_argument("--out",required=True)
    a=ap.parse_args()
    repos=yaml.safe_load(Path(a.repositories).read_text(encoding="utf-8"))["repositories"]
    baseline=yaml.safe_load(Path(a.baseline_template).read_text(encoding="utf-8"))
    rollup=yaml.safe_load(Path(a.rollup).read_text(encoding="utf-8"))
    comp={}
    with Path(a.compliance).open(encoding="utf-8-sig",newline="") as fh:
        for r in csv.DictReader(fh):comp[(r["repository_name"],r["control_id"])]=r["compliance_status"]
    out=[]
    for r in repos:
        full=r["github"];name=r["name"]
        for cid,fn in [
          ("EMS-CTRL-015",lambda:eval_015(full,baseline)),
          ("EMS-CTRL-025",lambda:eval_025(full)),
          ("EMS-CTRL-031",lambda:eval_artifacts(full,"test")),
          ("EMS-CTRL-033",lambda:eval_033(full)),
          ("EMS-CTRL-037",lambda:eval_artifacts(full,"build")),
          ("EMS-CTRL-079",lambda:eval_079(name,comp,rollup))
        ]:
            status,assertions=fn()
            out.append({"repository_id":r["id"],"repository_name":name,"control_id":cid,"status":status,"assertions":assertions})
    Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    Path(a.out).write_text(json.dumps(out,indent=2),encoding="utf-8")
    print(f"Generated {len(out)} refined collector observations.")
if __name__=="__main__":main()

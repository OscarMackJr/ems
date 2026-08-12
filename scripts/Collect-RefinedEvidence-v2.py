import argparse, csv, json, subprocess, base64, fnmatch
from pathlib import Path
import yaml

def gh_api(path):
    p=subprocess.run(
        ["gh","api",path],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    if p.returncode!=0:
        return None,p.stderr.strip()
    if not p.stdout.strip():
        return {},None
    try:
        return json.loads(p.stdout),None
    except Exception as e:
        return None,str(e)

def repo_tree(repo, branch=None):
    ref = f"?recursive=1"
    if branch:
        ref += f"&ref={branch}"
    d,e=gh_api(f"repos/{repo}/git/trees/{branch or 'HEAD'}{ref}")
    if d and isinstance(d,dict):
        return d.get("tree",[]),None
    # Fallback via default branch lookup
    info,e2=gh_api(f"repos/{repo}")
    if not info:
        return [],e or e2
    branch=info.get("default_branch")
    d,e=gh_api(f"repos/{repo}/git/trees/{branch}?recursive=1")
    return (d or {}).get("tree",[]) if d else [],e

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
        path=w.get("path","")
        d,e=gh_api(f"repos/{repo}/contents/{path}")
        if d and d.get("content"):
            try:
                texts.append(base64.b64decode(d["content"]).decode("utf-8","replace").lower())
            except Exception:
                pass
    return "\n".join(texts),wfs

def detect_stack_and_manifests(repo):
    tree,_=repo_tree(repo)
    paths=[x.get("path","") for x in tree if x.get("type")=="blob"]
    names=[p.split("/")[-1] for p in paths]
    stack=set()
    manifests=[]

    def add_if(pattern, stack_name=None):
        matched=[p for p in paths if fnmatch.fnmatch(p, pattern) or fnmatch.fnmatch(p.split("/")[-1], pattern)]
        if matched:
            manifests.extend(matched)
            if stack_name:
                stack.add(stack_name)

    add_if("package.json","javascript")
    add_if("pyproject.toml","python")
    add_if("requirements.txt","python")
    add_if("Pipfile","python")
    add_if("Cargo.toml","rust")
    add_if("*.csproj","dotnet")
    add_if("*.sln","dotnet")

    return stack, sorted(set(manifests)), paths

def eval_025(repo):
    stack,manifests,paths=detect_stack_and_manifests(repo)
    text,wfs=workflow_text(repo)
    evidence=[]

    if "javascript" in stack and any(x in text for x in ["npm test","npm run test","yarn test","pnpm test","jest","vitest"]):
        evidence.append("javascript_test")
    if "python" in stack and any(x in text for x in ["pytest","python -m unittest","tox","nox"]):
        evidence.append("python_test")
    if "rust" in stack and "cargo test" in text:
        evidence.append("rust_test")
    if "dotnet" in stack and "dotnet test" in text:
        evidence.append("dotnet_test")

    markers=[]
    for p in paths:
        low=p.lower()
        if (
            low.startswith("tests/") or "/tests/" in low or
            low.startswith("test/") or "/test/" in low or
            "__tests__" in low or
            low.endswith("_test.py") or low.endswith(".tests.csproj")
        ):
            markers.append(p)

    if evidence:
        status="PASS"
    elif markers:
        status="WARNING"
    else:
        status="NOT_EVALUATED"

    return status,{
        "detected_stack":sorted(stack),
        "manifest_paths":manifests[:50],
        "test_commands":evidence,
        "test_markers":markers[:50],
        "workflow_count":len(wfs)
    }

def eval_033(repo):
    stack,manifests,paths=detect_stack_and_manifests(repo)
    text,wfs=workflow_text(repo)

    deterministic=False
    runtime=False
    details={}

    pathset=set(paths)

    if "javascript" in stack:
        js_lock=any(
            p.endswith(("package-lock.json","yarn.lock","pnpm-lock.yaml","npm-shrinkwrap.json"))
            for p in paths
        )
        deterministic |= js_lock
        runtime |= "actions/setup-node@" in text and ("node-version" in text or "node-version-file" in text)
        details["javascript_lockfile"]=js_lock

    if "python" in stack:
        py_lock=any(
            p.endswith(("poetry.lock","Pipfile.lock","requirements.txt"))
            for p in paths
        )
        deterministic |= py_lock
        runtime |= "actions/setup-python@" in text and ("python-version" in text or "python-version-file" in text)
        details["python_lock_or_pin_file"]=py_lock

    if "rust" in stack:
        rust_lock=any(p.endswith("Cargo.lock") for p in paths)
        deterministic |= rust_lock
        runtime |= any(p.endswith("rust-toolchain") or p.endswith("rust-toolchain.toml") for p in paths) or "toolchain" in text
        details["rust_lockfile"]=rust_lock

    if "dotnet" in stack:
        dotnet_lock=any(
            p.endswith(("packages.lock.json","Directory.Packages.props"))
            for p in paths
        )
        deterministic |= dotnet_lock
        runtime |= any(p.endswith("global.json") for p in paths) or (
            "actions/setup-dotnet@" in text and "dotnet-version" in text
        )
        details["dotnet_lock_or_central_version_file"]=dotnet_lock

    if deterministic and runtime and wfs:
        status="PASS"
    elif deterministic or runtime or wfs:
        status="WARNING"
    else:
        status="NOT_EVALUATED"

    details.update({
        "detected_stack":sorted(stack),
        "manifest_paths":manifests[:50],
        "dependency_resolution_deterministic":deterministic,
        "runtime_or_toolchain_pinned":runtime,
        "workflow_present":bool(wfs)
    })
    return status,details

def eval_artifacts(repo,kind):
    d,e=gh_api(f"repos/{repo}/actions/artifacts?per_page=100")
    if d is None:
        return "NOT_EVALUATED",{"api_error":e}

    artifacts=d.get("artifacts",[])
    text,wfs=workflow_text(repo)

    upload="actions/upload-artifact@" in text

    if kind=="test":
        producer_signals=[
            "test-results","coverage","junit","trx","pytest","coverage.xml",
            "lcov","cobertura","jacoco","dotnet test","cargo test","npm test","pytest"
        ]
        relevant_workflow=upload and any(k in text for k in producer_signals)

        artifact_names=[(a.get("name") or "").lower() for a in artifacts]
        retained_test_artifact=any(
            any(k in n for k in ["test","coverage","junit","trx","lcov","cobertura","jacoco"])
            for n in artifact_names
        )

        if relevant_workflow and retained_test_artifact:
            status="PASS"
        elif relevant_workflow or retained_test_artifact:
            status="WARNING"
        else:
            status="NOT_EVALUATED"

        return status,{
            "artifact_count":len(artifacts),
            "upload_artifact_action_detected":upload,
            "test_artifact_workflow_detected":relevant_workflow,
            "retained_test_artifact_detected":retained_test_artifact,
            "sample_artifact_names":artifact_names[:20]
        }

    build_signals=["build","dist","publish","release","package","binary","installer"]
    relevant_workflow=upload and any(k in text for k in build_signals)
    artifact_names=[(a.get("name") or "").lower() for a in artifacts]
    retained_build_artifact=bool(artifacts)

    if relevant_workflow and retained_build_artifact:
        status="PASS"
    elif relevant_workflow or retained_build_artifact:
        status="WARNING"
    else:
        status="NOT_EVALUATED"

    return status,{
        "artifact_count":len(artifacts),
        "upload_artifact_action_detected":upload,
        "build_artifact_workflow_detected":relevant_workflow,
        "retained_build_artifact_detected":retained_build_artifact,
        "sample_artifact_names":artifact_names[:20]
    }

def eval_015(repo,baseline):
    assertions={}
    for req in baseline.get("required",[]):
        assertions[req["id"]]=any(exists(repo,p) for p in req.get("any_of",[]))

    stack,manifests,paths=detect_stack_and_manifests(repo)
    wfs,_=workflows(repo)

    assertions["workflow"]=bool(wfs)
    assertions["dependency_manifest"]=bool(manifests)
    assertions["detected_stack"]=sorted(stack)
    assertions["manifest_paths"]=manifests[:50]

    required_bools=[
        v for k,v in assertions.items()
        if k not in {"detected_stack","manifest_paths"}
    ]

    status="PASS" if all(required_bools) else ("WARNING" if any(required_bools) else "FAIL")
    return status,assertions

def merge_effective_status(baseline_csv, refined):
    effective={}
    with Path(baseline_csv).open(encoding="utf-8-sig",newline="") as fh:
        for r in csv.DictReader(fh):
            effective[(r["repository_name"],r["control_id"])]=r["compliance_status"]

    for o in refined:
        effective[(o["repository_name"],o["control_id"])]=o["status"]

    return effective

def eval_079(repo_name,effective,rollup):
    fail=warn=ne=0
    domains={}

    for domain,spec in rollup["domains"].items():
        states=[]
        for cid in spec["controls"]:
            state=effective.get((repo_name,cid))
            if state and state!="NOT_APPLICABLE":
                states.append(state)
        domains[domain]=states
        fail+=states.count("FAIL")
        warn+=states.count("WARNING")
        ne+=states.count("NOT_EVALUATED")

    if fail>0:
        status="FAIL"
    elif ne>0 or warn>2:
        status="WARNING"
    else:
        status="PASS"

    return status,{
        "domains":domains,
        "fail_count":fail,
        "warning_count":warn,
        "not_evaluated_count":ne
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--repositories",required=True)
    ap.add_argument("--baseline-template",required=True)
    ap.add_argument("--rollup",required=True)
    ap.add_argument("--compliance",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()

    repos=yaml.safe_load(Path(args.repositories).read_text(encoding="utf-8"))["repositories"]
    baseline=yaml.safe_load(Path(args.baseline_template).read_text(encoding="utf-8"))
    rollup=yaml.safe_load(Path(args.rollup).read_text(encoding="utf-8"))

    refined=[]

    # Stage 1: base refined controls.
    for r in repos:
        full=r["github"]
        name=r["name"]
        for cid,fn in [
            ("EMS-CTRL-015",lambda:eval_015(full,baseline)),
            ("EMS-CTRL-025",lambda:eval_025(full)),
            ("EMS-CTRL-031",lambda:eval_artifacts(full,"test")),
            ("EMS-CTRL-033",lambda:eval_033(full)),
            ("EMS-CTRL-037",lambda:eval_artifacts(full,"build")),
        ]:
            status,assertions=fn()
            refined.append({
                "repository_id":r["id"],
                "repository_name":name,
                "control_id":cid,
                "status":status,
                "assertions":assertions,
                "stage":1
            })

    # Stage 2: roll-up CTRL-079 using newly refined statuses.
    effective=merge_effective_status(args.compliance, refined)

    for r in repos:
        status,assertions=eval_079(r["name"],effective,rollup)
        refined.append({
            "repository_id":r["id"],
            "repository_name":r["name"],
            "control_id":"EMS-CTRL-079",
            "status":status,
            "assertions":assertions,
            "stage":2
        })

    out=Path(args.out)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(refined,indent=2),encoding="utf-8")
    print(f"Generated {len(refined)} Collector Refinement v2 observations.")

if __name__=="__main__":
    main()

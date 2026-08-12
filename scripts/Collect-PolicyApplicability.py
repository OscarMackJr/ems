import argparse, json, re, subprocess, sys
from pathlib import Path
import yaml

CONTROLS = ("EMS-CTRL-034","EMS-CTRL-036","EMS-CTRL-038","EMS-CTRL-039")

def run_gh(args):
    p=subprocess.run(["gh"]+args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                     encoding="utf-8", errors="replace")
    if p.returncode:
        return None, p.stderr.strip()
    try:
        return json.loads(p.stdout or "null"), None
    except json.JSONDecodeError:
        return p.stdout, None

def load_repos(path):
    data=yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    items=data.get("repositories", data if isinstance(data,list) else [])
    out=[]
    if isinstance(items,dict):
        for k,v in items.items():
            if isinstance(v,dict):
                name=v.get("name") or v.get("repository_name") or k
                full=v.get("full_name") or v.get("repository") or name
            else:
                name=k; full=k
            out.append((name,full))
    else:
        for v in items:
            if not isinstance(v,dict): continue
            name=v.get("name") or v.get("repository_name") or v.get("id")
            full=v.get("full_name") or v.get("repository") or name
            if name: out.append((name,full))
    return out

def repo_slug(full, org):
    if "/" in full: return full
    return f"{org}/{full}"

def workflow_signals(repo):
    workflows,err=run_gh(["api",f"repos/{repo}/actions/workflows","--paginate"])
    arr=[]
    if isinstance(workflows,dict): arr=workflows.get("workflows",[])
    elif isinstance(workflows,list):
        for x in workflows:
            if isinstance(x,dict) and "workflows" in x: arr.extend(x["workflows"])
    text=" ".join((str(x.get("name",""))+" "+str(x.get("path",""))) for x in arr).lower()
    release=bool(re.search(r"\brelease\b|publish|package",text))
    deploy=bool(re.search(r"\bdeploy\b|deployment|production|prod\b",text))
    asset=bool(re.search(r"\brelease\b|publish|package|artifact",text))
    return len(arr),release,deploy,asset,err

def override_value(overrides, repo_name, basis):
    r=(overrides.get("repositories") or {}).get(repo_name,{})
    if basis in r:
        return r[basis]
    return None

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--repositories",required=True)
    ap.add_argument("--policy",required=True)
    ap.add_argument("--overrides",required=True)
    ap.add_argument("--organization",default="OscarMackJr")
    ap.add_argument("--out",required=True)
    a=ap.parse_args()

    policy=yaml.safe_load(Path(a.policy).read_text(encoding="utf-8"))
    overrides=yaml.safe_load(Path(a.overrides).read_text(encoding="utf-8")) or {}
    results=[]

    for name,full in load_repos(a.repositories):
        repo=repo_slug(full,a.organization)

        releases,e1=run_gh(["api",f"repos/{repo}/releases?per_page=100"])
        releases=releases if isinstance(releases,list) else []
        release_count=len(releases)
        asset_count=sum(len(x.get("assets",[])) for x in releases if isinstance(x,dict))

        tags,e2=run_gh(["api",f"repos/{repo}/tags?per_page=100"])
        tags=tags if isinstance(tags,list) else []
        tag_names=[x.get("name","") for x in tags if isinstance(x,dict)]
        # Release/version tags: conservative semantic-version-like signal.
        release_tags=[x for x in tag_names if re.match(r"^v?\d+\.\d+(?:\.\d+)?(?:[-+].*)?$",x)]

        envs,e3=run_gh(["api",f"repos/{repo}/environments"])
        env_count=len((envs or {}).get("environments",[])) if isinstance(envs,dict) else 0

        wf_count,release_wf,deploy_wf,asset_wf,e4=workflow_signals(repo)

        facts={
            "github_release_count":release_count,
            "github_release_asset_count":asset_count,
            "release_tag_count":len(release_tags),
            "github_environment_count":env_count,
            "workflow_count":wf_count,
            "release_workflow_detected":release_wf,
            "deployment_workflow_detected":deploy_wf,
            "release_asset_workflow_detected":asset_wf,
            "api_warnings":[x for x in (e1,e2,e3,e4) if x]
        }

        basis_values={
            "formal_release": release_count>0 or release_wf,
            "distributable_release_artifacts": asset_count>0 or asset_wf,
            "release_tags": len(release_tags)>0,
            "controlled_release_or_deployment": release_wf or deploy_wf or env_count>0
        }

        for cid in CONTROLS:
            spec=policy["controls"][cid]
            basis=spec["applicability_basis"]
            auto=basis_values[basis]
            ov=override_value(overrides,name,basis)
            effective=bool(ov) if ov is not None else auto
            source="repository_override" if ov is not None else "automated_evidence"
            app="APPLICABLE" if effective else "NOT_APPLICABLE"
            reason=(f"{basis}=true based on {source}."
                    if effective else spec["not_applicable_reason"])
            results.append({
                "repository_name":name,
                "repository":repo,
                "control_id":cid,
                "control_name":spec["name"],
                "applicability":app,
                "applicability_basis":basis,
                "applicability_reason":reason,
                "decision_source":source,
                "facts":facts
            })

    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(results,indent=2),encoding="utf-8")
    print(json.dumps({
        "row_count":len(results),
        "applicable":sum(x["applicability"]=="APPLICABLE" for x in results),
        "not_applicable":sum(x["applicability"]=="NOT_APPLICABLE" for x in results)
    },indent=2))

if __name__=="__main__": main()

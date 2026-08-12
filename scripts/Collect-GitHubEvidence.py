import argparse,json,subprocess,yaml,datetime
from pathlib import Path
def api(path):
 p=subprocess.run(["gh","api",path],capture_output=True,text=True)
 if p.returncode:return None
 try:return json.loads(p.stdout)
 except:return {}
def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--repositories",required=True); ap.add_argument("--mapping",required=True); ap.add_argument("--out",required=True); a=ap.parse_args()
 repos=yaml.safe_load(Path(a.repositories).read_text())["repositories"]; mp=yaml.safe_load(Path(a.mapping).read_text())["controls"]; out=[]
 for r in repos:
  for cid,m in mp.items():
   col=m["collector"]; status="NOT_EVALUATED"; details={}; repo=r["github"]; branch=r.get("default_branch")
   if col=="branch_protection" and branch:
    d=api(f"repos/{repo}/branches/{branch}/protection"); status="PASS" if d else "NOT_EVALUATED"; details={"protection_detected":bool(d)}
   elif col=="pull_request_rules" and branch:
    d=api(f"repos/{repo}/branches/{branch}/protection"); status="PASS" if d and d.get("required_pull_request_reviews") else ("FAIL" if d else "NOT_EVALUATED")
   elif col=="codeowners_enforcement":
    d=api(f"repos/{repo}/contents/CODEOWNERS") or api(f"repos/{repo}/contents/.github/CODEOWNERS"); status="PASS" if d else "FAIL"
   elif col=="repository_metadata":
    d=api(f"repos/{repo}"); status="PASS" if d and d.get("default_branch") else "WARNING"
   elif col=="repository_files":
    status="PASS" if api(f"repos/{repo}/contents/.github/workflows") and api(f"repos/{repo}/contents/README.md") else "WARNING"
   elif col=="build_workflow":
    d=api(f"repos/{repo}/actions/workflows"); status="PASS" if d and d.get("total_count",0)>0 else "WARNING"
   elif col=="release_workflow":
    d=api(f"repos/{repo}/actions/workflows"); names=[x.get("name","").lower() for x in (d or {}).get("workflows",[])]; status="PASS" if any("release" in n or "deploy" in n for n in names) else "WARNING"
   elif col=="repository_health":
    d=api(f"repos/{repo}/community/profile"); pct=(d or {}).get("health_percentage"); status="PASS" if isinstance(pct,int) and pct>=70 else "WARNING"
   elif col=="secret_scanning":
    d=api(f"repos/{repo}/secret-scanning/alerts"); status="PASS" if d is not None else "NOT_EVALUATED"
   elif col=="dependency_security":
    d=api(f"repos/{repo}/dependabot/alerts"); status="PASS" if d is not None else "NOT_EVALUATED"
   elif col=="sbom":
    d=api(f"repos/{repo}/dependency-graph/sbom"); status="PASS" if d else "NOT_EVALUATED"
   out.append({"repository_id":r["id"],"control_id":cid,"status":status,"observed_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),"evidence_refs":[m["evidence_id"]],"source":"GitHub API","details":details})
 Path(a.out).parent.mkdir(parents=True,exist_ok=True); Path(a.out).write_text(json.dumps(out,indent=2)); print(f"Generated {len(out)} GitHub observations.")
if __name__=="__main__":main()


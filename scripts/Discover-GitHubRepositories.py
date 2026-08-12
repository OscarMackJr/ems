import argparse,json,subprocess,yaml
from pathlib import Path
def run(args):
 p=subprocess.run(["gh"]+args,capture_output=True,text=True)
 if p.returncode: raise RuntimeError(p.stderr)
 return json.loads(p.stdout)
def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--org",required=True); ap.add_argument("--overrides",required=True); ap.add_argument("--outdir",required=True); ap.add_argument("--registry-out",required=True); a=ap.parse_args()
 repos=run(["repo","list",a.org,"--limit","1000","--json","name,nameWithOwner,visibility,isArchived,isFork,defaultBranchRef,primaryLanguage,repositoryTopics,createdAt,updatedAt"])
 ov=yaml.safe_load(Path(a.overrides).read_text()) or {}; overrides={x["github"]:x for x in ov.get("overrides",[])}
 rows=[]
 for i,r in enumerate(sorted(repos,key=lambda x:x["name"].lower()),1):
  lang=(r.get("primaryLanguage") or {}).get("name")
  x={"id":f"REPO-{i:03d}","name":r["name"],"github":r["nameWithOwner"],"owner":"UNCLASSIFIED","tier":"UNCLASSIFIED","service_criticality":"UNCLASSIFIED","production":"UNKNOWN","internet_exposed":"UNKNOWN","contains_customer_data":"UNKNOWN","ai_enabled":"UNKNOWN","technologies":[lang] if lang else [],"data_classification":["UNCLASSIFIED"],"visibility":r["visibility"],"default_branch":(r.get("defaultBranchRef") or {}).get("name"),"archived":r["isArchived"],"fork":r["isFork"],"status":"Discovered"}
  if x["github"] in overrides: x.update(overrides[x["github"]]); x["id"]=f"REPO-{i:03d}"; x["name"]=r["name"]; x["github"]=r["nameWithOwner"]; x["status"]="Classified"
  rows.append(x)
 out=Path(a.outdir); out.mkdir(parents=True,exist_ok=True); (out/"repository_inventory.json").write_text(json.dumps(rows,indent=2))
 Path(a.registry_out).write_text(yaml.safe_dump({"repositories":rows},sort_keys=False))
 print(f"Discovered {len(rows)} repositories; classified {sum(x['status']=='Classified' for x in rows)}.")
if __name__=="__main__":main()

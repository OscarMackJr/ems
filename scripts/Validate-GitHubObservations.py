import argparse,json,yaml,sys
from pathlib import Path
VALID={"PASS","FAIL","WARNING","EXCEPTION","NOT_APPLICABLE","NOT_EVALUATED"}
def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--observations",required=True); ap.add_argument("--repositories",required=True); ap.add_argument("--controls",required=True); ap.add_argument("--report",required=True); a=ap.parse_args()
 o=json.loads(Path(a.observations).read_text()); repos={x["id"] for x in yaml.safe_load(Path(a.repositories).read_text())["repositories"]}; ctrls={x["id"] for x in yaml.safe_load(Path(a.controls).read_text())["controls"]}; errors=[]
 for i,x in enumerate(o):
  if x.get("repository_id") not in repos: errors.append(f"{i}: unknown repository")
  if x.get("control_id") not in ctrls: errors.append(f"{i}: unknown control")
  if x.get("status") not in VALID: errors.append(f"{i}: invalid status")
 r={"status":"PASS" if not errors else "FAIL","observation_count":len(o),"errors":errors}; Path(a.report).write_text(json.dumps(r,indent=2)); print(json.dumps(r,indent=2)); sys.exit(0 if not errors else 1)
if __name__=="__main__":main()

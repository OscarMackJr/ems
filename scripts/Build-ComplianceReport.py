import argparse,csv,json
from pathlib import Path
def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--applicability-dir",required=True); ap.add_argument("--observations",required=True); ap.add_argument("--outdir",required=True); a=ap.parse_args()
 obs={(x["repository_id"],x["control_id"]):x for x in json.loads(Path(a.observations).read_text())}; rows=[]
 for f in Path(a.applicability_dir).glob("REPO-*_applicable_controls.csv"):
  for r in csv.DictReader(f.open()):
   o=obs.get((r["repository_id"],r["control_id"])); r["compliance_status"]=o["status"] if o else "NOT_EVALUATED"; r["evidence_refs"]=";".join(o.get("evidence_refs",[])) if o else ""; rows.append(r)
 out=Path(a.outdir); fields=["repository_id","repository_name","tier","control_id","control_name","family","applicability_reason","compliance_status","evidence_refs"]
 with (out/"repository_control_compliance.csv").open("w",newline="") as h:
  w=csv.DictWriter(h,fieldnames=fields);w.writeheader();w.writerows(rows)
 (out/"repository_control_compliance.json").write_text(json.dumps(rows,indent=2)); print(f"Generated compliance report with {len(rows)} rows.")
if __name__=="__main__":main()
